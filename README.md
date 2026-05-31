# 🩺 MediScan AI

**ML-powered disease risk prediction — CSC-233 AI Lab Project, BNU Spring 2026**

> Early Detection, Better Outcomes.

---

## 📋 Project Overview

MediScan AI is a Streamlit web application that predicts the risk of **Heart Disease** and **Diabetes**
using four supervised machine-learning classifiers trained on CDC BRFSS survey data.

| Feature | Details |
|---|---|
| Diseases | Heart Disease (BRFSS 2022), Diabetes (BRFSS 2015) |
| Models | Random Forest, SVM, Decision Tree, Naive Bayes |
| Evaluation | Accuracy, F1, Precision, Recall, ROC-AUC, 5-Fold CV |
| NLP Chat | Gemini 1.5 Flash symptom triage |
| Database | SQLite (local) + MongoDB (optional) |
| PDF Report | ReportLab-generated downloadable health report |

---

## 👥 Team

| # | Name | Roll | Contribution |
|---|---|---|---|
| 1 | Usman Ahmad | F2025-0893 | NLP Symptom Chat (Gemini API) |
| 2 | Muhammad Arsal | F2024-0708 | SVM Classifier |
| 3 | Mustafa Ali | F2024-0706 | Random Forest Classifier |
| 4 | Ahmed Hunbal | F2024-0134 | Decision Tree Classifier |
| 5 | Daniyal Khan | F2024-0792 | Naive Bayes Classifier |

---

## 🗂️ Project Structure

```
mediscan_ai/
├── app.py                  # Main Streamlit entry point
├── preprocess.py           # Data cleaning & feature engineering
├── predict.py              # Model training script (all 4 models × 2 diseases)
├── db.py                   # MongoDB + SQLite database layer
├── requirements.txt        # Python dependencies
├── data/                   # Place your CSV datasets here
│   ├── heart_2022_with_nans.csv
│   └── diabetes_binary_health_indicators_BRFSS2015.csv
├── models/                 # Auto-created after training
│   ├── heart_model.pkl
│   ├── heart_scaler.pkl
│   ├── heart_feature_cols.pkl
│   ├── heart_metrics.json
│   ├── diabetes_model.pkl
│   ├── diabetes_scaler.pkl
│   ├── diabetes_feature_cols.pkl
│   └── diabetes_metrics.json
└── pages/
    ├── heart.py            # Heart Disease prediction page
    ├── diabetes.py         # Diabetes prediction page
    ├── chat.py             # Gemini symptom chat
    ├── compare.py          # Model comparison dashboard
    ├── history.py          # Prediction history + PDF export
    └── analytics.py        # Analytics dashboard (6 MongoDB pipelines)
```

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Place datasets in `data/` folder

```
data/heart_2022_with_nans.csv
data/diabetes_binary_health_indicators_BRFSS2015.csv
```

Download from Kaggle:
- Heart: [heart-disease-2022](https://www.kaggle.com/datasets/kamilpytlak/personal-key-indicators-of-heart-disease)
- Diabetes: [pima-indians-diabetes-database](https://www.kaggle.com/datasets/alexteboul/diabetes-health-indicators-dataset)

### 3. Train all models

```bash
python predict.py
```

This trains all 4 classifiers for both diseases and saves models + metrics to `models/`.

### 4. Run the app

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## 🗄️ MongoDB Setup (Optional)

MongoDB is optional — the app works fully with SQLite without it.
To enable MongoDB features (6 aggregation pipelines, text search):

```bash
# Install MongoDB Community Edition
# Then start it:
mongod --dbpath /data/db
```

The app auto-detects MongoDB on `localhost:27017`.

---

## 📊 Datasets

| Dataset | Source | Samples | Features | Target |
|---|---|---|---|---|
| Heart Disease | CDC BRFSS 2022 | ~246,000 | 17 | HeartDisease (Yes/No) |
| Diabetes | CDC BRFSS 2015 | ~253,680 | 21 | Diabetes_binary (0/1) |

---

## 🤖 Models

| Model | Implementer | Key Config |
|---|---|---|
| Random Forest | Mustafa Ali | 100 trees, SMOTE balancing |
| SVM | Muhammad Arsal | RBF kernel, probability=True |
| Decision Tree | Ahmed Hunbal | max_depth=8 |
| Naive Bayes | Daniyal Khan | GaussianNB |

All models use:
- 80/20 train/test split
- SMOTE for class imbalance
- StandardScaler normalisation
- 5-Fold Stratified Cross Validation

---

## ⚕️ Disclaimer

MediScan AI is an **educational tool only**. Results are not a medical diagnosis.
Always consult a qualified healthcare professional for medical advice.
