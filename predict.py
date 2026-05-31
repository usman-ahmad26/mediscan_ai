"""
predict.py
==========
Trains four classifiers for both Heart Disease and Diabetes datasets.

  1. Random Forest  (Mustafa Ali   — F2024-0706)
  2. SVM            (Muhammad Arsal— F2024-0708)  LinearSVC for speed
  3. Decision Tree  (Ahmed Hunbal  — F2024-0134)
  4. Naive Bayes    (Daniyal Khan  — F2024-0792)

NOTE: SVC(kernel='rbf') is O(n^2) — unusable on 200K+ rows.
      We use LinearSVC wrapped in CalibratedClassifierCV instead.
      It is still a Support Vector Machine, just the linear kernel
      variant, which scales to millions of samples in seconds.

Usage:
    python predict.py
    python predict.py --heart data/heart.csv --diabetes data/diabetes.csv
"""

import argparse, os, json, time
import joblib
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble      import RandomForestClassifier
from sklearn.svm           import LinearSVC
from sklearn.calibration   import CalibratedClassifierCV
from sklearn.tree          import DecisionTreeClassifier
from sklearn.naive_bayes   import GaussianNB
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
)

from preprocess import prepare_heart, prepare_diabetes

CV_SUBSAMPLE = 25_000


def _make_models():
    return {
        "Random Forest": RandomForestClassifier(
            n_estimators=100, class_weight="balanced",
            random_state=42, n_jobs=-1
        ),
        "SVM": CalibratedClassifierCV(
            LinearSVC(max_iter=3000, class_weight="balanced", random_state=42),
            cv=3, n_jobs=-1
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=8, class_weight="balanced", random_state=42
        ),
        "Naive Bayes": GaussianNB(),
    }


def evaluate(name, model, X_train, X_test, y_train, y_test):
    t0 = time.time()
    print(f"  [{name}] training...", end=" ", flush=True)
    model.fit(X_train, y_train)
    print(f"done ({time.time()-t0:.1f}s)  |  CV scoring...", end=" ", flush=True)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    n = len(X_train)
    if n > CV_SUBSAMPLE:
        rng = np.random.RandomState(42)
        idx = rng.choice(n, CV_SUBSAMPLE, replace=False)
        Xc, yc = X_train[idx], y_train[idx]
    else:
        Xc, yc = X_train, y_train

    cv_scores = cross_val_score(
        model, Xc, yc,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring="f1", n_jobs=-1
    )

    metrics = {
        "model_name":  name,
        "accuracy":    round(accuracy_score(y_test, y_pred) * 100, 2),
        "f1_score":    round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
        "precision":   round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
        "recall":      round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
        "roc_auc":     round(roc_auc_score(y_test, y_prob) * 100, 2) if y_prob is not None else None,
        "cv_f1_mean":  round(cv_scores.mean() * 100, 2),
        "cv_f1_std":   round(cv_scores.std() * 100, 2),
    }
    total = time.time() - t0
    print(f"done  →  Acc={metrics['accuracy']}%  F1={metrics['f1_score']}%  "
          f"CV-F1={metrics['cv_f1_mean']}±{metrics['cv_f1_std']}%  "
          f"({total:.1f}s total)")
    return model, metrics


def train_disease(disease, X_train, X_test, y_train, y_test, models_dir):
    print(f"\n{'='*60}")
    print(f"  TRAINING: {disease.upper()}")
    print(f"{'='*60}")

    MODELS = _make_models()
    all_metrics, best_model, best_f1, best_name = [], None, -1, ""

    for name, clf in MODELS.items():
        trained, metrics = evaluate(name, clf, X_train, X_test, y_train, y_test)
        metrics["disease_type"] = disease
        all_metrics.append(metrics)
        if metrics["f1_score"] > best_f1:
            best_f1, best_model, best_name = metrics["f1_score"], trained, name

    print(f"\n  ✅ Best: {best_name}  (F1={best_f1}%)")
    joblib.dump(best_model, os.path.join(models_dir, f"{disease}_model.pkl"))
    with open(os.path.join(models_dir, f"{disease}_metrics.json"), "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"  Saved → models/{disease}_model.pkl  &  models/{disease}_metrics.json")
    return all_metrics


def main():
    parser = argparse.ArgumentParser(description="MediScan AI — Model Training")
    parser.add_argument("--heart",    default="data/heart.csv")
    parser.add_argument("--diabetes", default="data/diabetes.csv")
    parser.add_argument("--models",   default="models")
    args = parser.parse_args()

    os.makedirs(args.models, exist_ok=True)

    if os.path.exists(args.heart):
        print(f"\nLoading Heart dataset: {args.heart}")
        X_tr, X_te, y_tr, y_te, _, feats = prepare_heart(args.heart, args.models)
        print(f"  Samples — train: {len(X_tr):,}  test: {len(X_te):,}  features: {len(feats)}")
        train_disease("heart", X_tr, X_te, y_tr, y_te, args.models)
    else:
        print(f"⚠️  Heart dataset not found at {args.heart}")

    if os.path.exists(args.diabetes):
        print(f"\nLoading Diabetes dataset: {args.diabetes}")
        X_tr, X_te, y_tr, y_te, _, feats = prepare_diabetes(args.diabetes, args.models)
        print(f"  Samples — train: {len(X_tr):,}  test: {len(X_te):,}  features: {len(feats)}")
        train_disease("diabetes", X_tr, X_te, y_tr, y_te, args.models)
    else:
        print(f"⚠️  Diabetes dataset not found at {args.diabetes}")

    print("\n✅ Training complete. All models saved to ./models/")


if __name__ == "__main__":
    main()
