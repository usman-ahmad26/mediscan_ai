"""
preprocess.py
=============
Data loading, cleaning, and feature engineering for MediScan AI.

Heart dataset  : heart.csv  (CDC BRFSS 2022 — auto-detects column names)
Diabetes dataset: diabetes.csv (CDC BRFSS 2015 — Diabetes_binary target)

The 2022 BRFSS heart dataset uses completely different column names from the
2020 version. This module auto-detects which version you have and normalises
everything to a common internal schema before training.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except ImportError:
    HAS_SMOTE = False


# ─────────────────────────────────────────────────────────────
# HEART DISEASE
# ─────────────────────────────────────────────────────────────

# 2022 BRFSS column names → internal name
HEART_2022_MAP = {
    "HadHeartAttack":        "HeartDisease",
    "SmokerStatus":          "Smoking",
    "AlcoholDrinkers":       "AlcoholDrinking",
    "HadStroke":             "Stroke",
    "DifficultyWalking":     "DiffWalking",
    "PhysicalActivities":    "PhysicalActivity",
    "HadAsthma":             "Asthma",
    "HadKidneyDisease":      "KidneyDisease",
    "HadSkinCancer":         "SkinCancer",
    "SleepHours":            "SleepTime",
    "PhysicalHealthDays":    "PhysicalHealth",
    "MentalHealthDays":      "MentalHealth",
    "GeneralHealth":         "GenHealth",
    "AgeCategory":           "AgeCategory",
    "Sex":                   "Sex",
    "BMI":                   "BMI",
    "RaceEthnicityCategory": "Race",
    "HadDiabetes":           "Diabetic",
}

# 2020 BRFSS column names are already in the internal schema
HEART_2020_TARGET = "HeartDisease"

HEART_FEATURE_COLS = [
    "BMI", "Smoking", "AlcoholDrinking", "Stroke", "PhysicalHealth",
    "MentalHealth", "DiffWalking", "Sex", "AgeCategory", "Race",
    "Diabetic", "PhysicalActivity", "GenHealth", "SleepTime",
    "Asthma", "KidneyDisease", "SkinCancer"
]


def _normalise_heart_2022(df: pd.DataFrame) -> pd.DataFrame:
    """Rename 2022 BRFSS columns to internal schema."""
    df = df.rename(columns=HEART_2022_MAP)

    # SmokerStatus in 2022 is a multi-category string — convert to binary
    if "Smoking" in df.columns and df["Smoking"].dtype == object:
        df["Smoking"] = df["Smoking"].apply(
            lambda x: 0 if str(x).lower() in ("never smoked", "never") else 1
        )

    # HadDiabetes in 2022 is multi-category — convert to binary
    if "Diabetic" in df.columns and df["Diabetic"].dtype == object:
        df["Diabetic"] = df["Diabetic"].apply(
            lambda x: 0 if str(x).lower() in ("no", "no, pre-diabetes or borderline diabetes") else 1
        )

    return df


def load_heart(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates()

    print(f"  Columns detected: {list(df.columns[:6])} ...")

    # Auto-detect dataset version
    if "HadHeartAttack" in df.columns:
        print("  Detected: BRFSS 2022 format — remapping columns")
        df = _normalise_heart_2022(df)
        target_col = "HeartDisease"
        # Target in 2022 is Yes/No
        df[target_col] = df[target_col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    elif "HeartDisease" in df.columns:
        print("  Detected: BRFSS 2020 format")
        target_col = "HeartDisease"
        df[target_col] = df[target_col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
    else:
        # Last resort: use first binary-looking column or raise clear error
        candidates = [c for c in df.columns if "heart" in c.lower() or "attack" in c.lower()]
        if candidates:
            target_col = candidates[0]
            print(f"  Using '{target_col}' as target column")
            df = df.rename(columns={target_col: "HeartDisease"})
            target_col = "HeartDisease"
            if df[target_col].dtype == object:
                df[target_col] = df[target_col].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
        else:
            raise KeyError(
                f"Cannot find a heart disease target column in {path}.\n"
                f"Available columns: {list(df.columns)}"
            )

    df = df.dropna(subset=[target_col])

    # Fill NaNs
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Encode remaining Yes/No object columns
    for col in df.columns:
        if df[col].dtype == object:
            unique_vals = set(df[col].dropna().str.lower().unique())
            if unique_vals <= {"yes", "no"}:
                df[col] = df[col].map({"Yes": 1, "No": 0, "yes": 1, "no": 0}).fillna(0).astype(int)

    # Ordinal: AgeCategory
    age_order = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-49",
                 "50-54", "55-59", "60-64", "65-69", "70-74", "75-79", "80 or older"]
    if "AgeCategory" in df.columns and df["AgeCategory"].dtype == object:
        df["AgeCategory"] = pd.Categorical(
            df["AgeCategory"], categories=age_order, ordered=True
        ).codes.replace(-1, 6)

    # Ordinal: GenHealth
    gen_order = ["Poor", "Fair", "Good", "Very good", "Excellent"]
    if "GenHealth" in df.columns and df["GenHealth"].dtype == object:
        df["GenHealth"] = pd.Categorical(
            df["GenHealth"], categories=gen_order, ordered=True
        ).codes.replace(-1, 2)

    # Binary: Sex
    if "Sex" in df.columns and df["Sex"].dtype == object:
        df["Sex"] = df["Sex"].map({"Male": 1, "Female": 0}).fillna(0).astype(int)

    # Label encode any remaining object columns
    le = LabelEncoder()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = le.fit_transform(df[col].astype(str))

    return df


def prepare_heart(path: str, models_dir: str = "models"):
    df = load_heart(path)

    available = [c for c in HEART_FEATURE_COLS if c in df.columns]
    if not available:
        raise ValueError(f"No expected feature columns found. Got: {list(df.columns)}")

    X = df[available].values.astype(float)
    y = df["HeartDisease"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if HAS_SMOTE:
        try:
            sm = SMOTE(random_state=42)
            X_train, y_train = sm.fit_resample(X_train, y_train)
        except Exception:
            pass

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(scaler,    os.path.join(models_dir, "heart_scaler.pkl"))
    joblib.dump(available, os.path.join(models_dir, "heart_feature_cols.pkl"))

    return X_train, X_test, y_train, y_test, scaler, available


# ─────────────────────────────────────────────────────────────
# DIABETES
# ─────────────────────────────────────────────────────────────

DIABETES_FEATURE_COLS = [
    "HighBP", "HighChol", "CholCheck", "BMI", "Smoker",
    "Stroke", "HeartDiseaseorAttack", "PhysActivity", "Fruits",
    "Veggies", "HvyAlcoholConsump", "AnyHealthcare", "NoDocbcCost",
    "GenHlth", "MentHlth", "PhysHlth", "DiffWalk",
    "Sex", "Age", "Education", "Income"
]


def load_diabetes(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.drop_duplicates()

    print(f"  Columns detected: {list(df.columns[:6])} ...")

    # Find target column
    if "Diabetes_binary" in df.columns:
        target_col = "Diabetes_binary"
    elif "Diabetes" in df.columns:
        target_col = "Diabetes"
        df = df.rename(columns={"Diabetes": "Diabetes_binary"})
        target_col = "Diabetes_binary"
    else:
        candidates = [c for c in df.columns if "diabet" in c.lower()]
        if candidates:
            target_col = candidates[0]
            df = df.rename(columns={target_col: "Diabetes_binary"})
            target_col = "Diabetes_binary"
        else:
            raise KeyError(
                f"Cannot find diabetes target column in {path}.\n"
                f"Available columns: {list(df.columns)}"
            )

    df = df.dropna(subset=[target_col])

    for col in DIABETES_FEATURE_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    df[target_col] = df[target_col].astype(int)
    return df


def prepare_diabetes(path: str, models_dir: str = "models"):
    df = load_diabetes(path)

    available = [c for c in DIABETES_FEATURE_COLS if c in df.columns]
    if not available:
        raise ValueError(f"No expected feature columns found. Got: {list(df.columns)}")

    X = df[available].values.astype(float)
    y = df["Diabetes_binary"].values.astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if HAS_SMOTE:
        try:
            sm = SMOTE(random_state=42)
            X_train, y_train = sm.fit_resample(X_train, y_train)
        except Exception:
            pass

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)

    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(scaler,    os.path.join(models_dir, "diabetes_scaler.pkl"))
    joblib.dump(available, os.path.join(models_dir, "diabetes_feature_cols.pkl"))

    return X_train, X_test, y_train, y_test, scaler, available
