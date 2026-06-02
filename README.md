 HEAD
# MediScan AI

**ML-powered disease risk prediction**

> Early Detection, Better Outcomes.

---

## 📋 Project Overview

MediScan AI is a Streamlit web application that predicts the risk of **Heart Disease** and **Diabetes** using four supervised machine-learning classifiers trained on CDC BRFSS survey data.

| Feature | Details |
|----------|----------|
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

```text
mediscan_ai/
├── app.py
├── preprocess.py
├── predict.py
├── db.py
├── requirements.txt
├── data/
│   ├── heart_2022_with_nans.csv
│   └── diabetes_binary_health_indicators_BRFSS2015.csv
├── models/
│   ├── heart_model.pkl
│   ├── heart_scaler.pkl
│   ├── heart_feature_cols.pkl
│   ├── heart_metrics.json
│   ├── diabetes_model.pkl
│   ├── diabetes_scaler.pkl
│   ├── diabetes_feature_cols.pkl
│   └── diabetes_metrics.json
└── pages/
    ├── heart.py
    ├── diabetes.py
    ├── chat.py
    ├── compare.py
    ├── history.py
    └── analytics.py
```

---

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Place Datasets in `data/`

```text
data/heart_2022_with_nans.csv
data/diabetes_binary_health_indicators_BRFSS2015.csv
```

### 3. Train Models

```bash
python predict.py
```

### 4. Run the App

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

## 🗄️ MongoDB Setup (Optional)

MongoDB is optional. The application works fully with SQLite.

```bash
mongod --dbpath /data/db
```

The app automatically detects MongoDB on `localhost:27017`.

---

## 📊 Datasets

| Dataset | Source | Samples | Features | Target |
|----------|----------|----------|----------|----------|
| Heart Disease | CDC BRFSS 2022 | ~246,000 | 17 | HeartDisease |
| Diabetes | CDC BRFSS 2015 | ~253,680 | 21 | Diabetes_binary |

---

## 🤖 Models

| Model | Implementer | Configuration |
|----------|----------|----------|
| Random Forest | Mustafa Ali | 100 Trees + SMOTE |
| SVM | Muhammad Arsal | RBF Kernel |
| Decision Tree | Ahmed Hunbal | max_depth = 8 |
| Naive Bayes | Daniyal Khan | GaussianNB |

All models use:

- 80/20 Train-Test Split
- SMOTE for class balancing
- StandardScaler normalization
- 5-Fold Stratified Cross Validation

---

## ⚕️ Disclaimer

MediScan AI is an educational project and not a medical diagnostic system.

Predictions are intended for learning and demonstration purposes only. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.
