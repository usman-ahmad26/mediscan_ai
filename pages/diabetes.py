"""pages/diabetes.py — Diabetes Prediction (BRFSS 2015 dataset)"""

import streamlit as st
import numpy as np
import joblib
import os
from db import save_screening
from ui.theme import apply_global_theme
apply_global_theme()

MODELS_DIR = "models"

@st.cache_resource
def load_diabetes_model():
    mp = os.path.join(MODELS_DIR, "diabetes_model.pkl")
    sp = os.path.join(MODELS_DIR, "diabetes_scaler.pkl")
    fp = os.path.join(MODELS_DIR, "diabetes_feature_cols.pkl")
    if not all(os.path.exists(p) for p in [mp, sp, fp]):
        return None, None, None
    return joblib.load(mp), joblib.load(sp), joblib.load(fp)


def risk_card(risk, confidence, tips):
    colors = {
        "Low Risk":    ("#10B981", "#052e16", "✅"),
        "Medium Risk": ("#F59E0B", "#2d1f00", "⚠️"),
        "High Risk":   ("#EF4444", "#2d0a0a", "🚨"),
    }
    color, bg, icon = colors[risk]
    tips_html = "".join(
        f"<div style='display:flex;gap:0.6rem;align-items:flex-start;margin-bottom:0.5rem'>"
        f"<span style='color:{color};margin-top:2px'>›</span>"
        f"<span style='color:#CBD5E1;font-size:0.88rem'>{t}</span></div>"
        for t in tips
    )
    st.markdown(f"""
    <div style='background:{bg};border:1px solid {color}40;border-radius:14px;
                padding:1.4rem 1.6rem;margin:1rem 0'>
      <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:0.8rem'>
        <div>
          <span style='font-size:1.6rem'>{icon}</span>
          <span style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;
                       color:{color};margin-left:0.5rem'>{risk}</span>
        </div>
        <div style='text-align:right'>
          <div style='color:#7A94B4;font-size:0.75rem'>Model Confidence</div>
          <div style='font-family:Syne,sans-serif;font-size:1.8rem;font-weight:700;
                      color:{color}'>{confidence}%</div>
        </div>
      </div>
      <div style='background:rgba(255,255,255,0.08);border-radius:99px;height:6px;margin-bottom:1rem'>
        <div style='background:{color};border-radius:99px;height:6px;width:{confidence}%'></div>
      </div>
      <div style='font-family:Syne,sans-serif;font-weight:600;color:#E2EAF4;
                  font-size:0.85rem;text-transform:uppercase;letter-spacing:0.08em;
                  margin-bottom:0.7rem'>Recommended Actions</div>
      {tips_html}
      <div style='margin-top:1rem;padding-top:0.8rem;border-top:1px solid rgba(255,255,255,0.07);
                  color:#4A6580;font-size:0.75rem'>
        ⚕️ This is not a medical diagnosis. Always consult a qualified healthcare professional.
      </div>
    </div>
    """, unsafe_allow_html=True)


def show():
    st.markdown("<h1>🩸 Diabetes Risk Prediction</h1>", unsafe_allow_html=True)
    st.caption("Enter your health indicators to assess diabetes risk (CDC BRFSS 2015 model)")

    model, scaler, feature_cols = load_diabetes_model()
    model_ready = model is not None

    if not model_ready:
        st.warning("⚠️ Model not trained yet — form is shown for preview. Run `python predict.py` to enable predictions.")

    st.markdown("<br>", unsafe_allow_html=True)

    yn = lambda v: 1 if v == "Yes" else 0

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("##### 👤 Demographics")
        sex = st.selectbox("Biological Sex", ["Female", "Male"])
        age = st.selectbox("Age Group", [
            "18–24","25–29","30–34","35–39","40–44",
            "45–49","50–54","55–59","60–64","65–69",
            "70–74","75–79","80+"
        ], index=5)
        education = st.selectbox("Highest Education Level", [
            "Never attended school", "Elementary (Grades 1–8)",
            "Some High School", "High School Graduate",
            "Some College", "College Graduate"
        ], index=4)
        income = st.selectbox("Annual Household Income", [
            "< $10,000", "$10,000–$15,000", "$15,000–$20,000",
            "$20,000–$25,000", "$25,000–$35,000", "$35,000–$50,000",
            "$50,000–$75,000", "> $75,000"
        ], index=4)
        bmi = st.number_input("BMI", 10.0, 98.0, 27.0, step=0.1)
        gen_hlth = st.selectbox("General Health", ["Excellent","Very good","Good","Fair","Poor"])
        ment_hlth = st.slider("Days of Poor Mental Health (last 30 days)", 0, 30, 0)
        phys_hlth = st.slider("Days of Poor Physical Health (last 30 days)", 0, 30, 0)

    with col2:
        st.markdown("##### 🏥 Medical & Lifestyle")
        high_bp    = st.selectbox("High Blood Pressure?", ["No", "Yes"])
        high_chol  = st.selectbox("High Cholesterol?", ["No", "Yes"])
        chol_check = st.selectbox("Cholesterol Check in Past 5 Years?", ["Yes", "No"])
        smoker     = st.selectbox("Smoked ≥100 cigarettes in lifetime?", ["No", "Yes"])
        stroke     = st.selectbox("Ever had a Stroke?", ["No", "Yes"])
        heart_dis  = st.selectbox("Heart Disease or Heart Attack?", ["No", "Yes"])
        phys_act   = st.selectbox("Physically Active (past 30 days)?", ["Yes", "No"])
        fruits     = st.selectbox("Consume Fruit ≥1/day?", ["Yes", "No"])
        veggies    = st.selectbox("Consume Vegetables ≥1/day?", ["Yes", "No"])
        hvy_alc    = st.selectbox("Heavy Alcohol Consumption?", ["No", "Yes"])
        any_hc     = st.selectbox("Any Health Coverage / Insurance?", ["Yes", "No"])
        no_doc_cost= st.selectbox("Could not see doctor due to cost (past year)?", ["No", "Yes"])
        diff_walk  = st.selectbox("Difficulty Walking / Climbing Stairs?", ["No", "Yes"])

    symptom_notes = st.text_area(
        "Symptom Notes (optional)",
        placeholder="e.g. frequent urination, extreme thirst, fatigue, blurry vision..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Predict Diabetes Risk", type="primary"):
        if not model_ready:
            st.error("Models not trained yet. Run `python predict.py` first.")
            return

        age_list = ["18–24","25–29","30–34","35–39","40–44",
                    "45–49","50–54","55–59","60–64","65–69",
                    "70–74","75–79","80+"]
        age_val = age_list.index(age) + 1
        edu_val = ["Never attended school","Elementary (Grades 1–8)","Some High School",
                   "High School Graduate","Some College","College Graduate"].index(education) + 1
        inc_val = ["< $10,000","$10,000–$15,000","$15,000–$20,000","$20,000–$25,000",
                   "$25,000–$35,000","$35,000–$50,000","$50,000–$75,000","> $75,000"].index(income) + 1
        gen_map = {"Excellent": 1, "Very good": 2, "Good": 3, "Fair": 4, "Poor": 5}

        raw = {
            "HighBP":               yn(high_bp),
            "HighChol":             yn(high_chol),
            "CholCheck":            yn(chol_check),
            "BMI":                  bmi,
            "Smoker":               yn(smoker),
            "Stroke":               yn(stroke),
            "HeartDiseaseorAttack": yn(heart_dis),
            "PhysActivity":         yn(phys_act),
            "Fruits":               yn(fruits),
            "Veggies":              yn(veggies),
            "HvyAlcoholConsump":    yn(hvy_alc),
            "AnyHealthcare":        yn(any_hc),
            "NoDocbcCost":          yn(no_doc_cost),
            "GenHlth":              gen_map[gen_hlth],
            "MentHlth":             float(ment_hlth),
            "PhysHlth":             float(phys_hlth),
            "DiffWalk":             yn(diff_walk),
            "Sex":                  1 if sex == "Male" else 0,
            "Age":                  float(age_val),
            "Education":            float(edu_val),
            "Income":               float(inc_val),
        }

        feat_vec = np.array([[raw.get(f, 0) for f in feature_cols]], dtype=float)
        feat_scaled = scaler.transform(feat_vec)
        prob = model.predict_proba(feat_scaled)[0][1]
        confidence = round(prob * 100, 1)

        if prob < 0.35:
            risk = "Low Risk"
            tips = [
                "Maintain a balanced diet rich in fibre and low in refined sugars.",
                "Stay physically active — aim for 150 min/week of moderate exercise.",
                "Schedule a routine fasting glucose check annually.",
            ]
        elif prob < 0.65:
            risk = "Medium Risk"
            tips = [
                "Request a fasting blood glucose or HbA1c test from your doctor.",
                "Reduce processed carbohydrates, sugary drinks, and saturated fats.",
                "Increase daily physical activity gradually.",
                "Monitor weight and aim for a healthy BMI (18.5–24.9).",
            ]
        else:
            risk = "High Risk"
            tips = [
                "Consult an endocrinologist or GP for a formal diabetes screening.",
                "Begin a structured diet and exercise programme immediately.",
                "Eliminate sugary beverages and highly processed foods.",
                "Request full metabolic panel: fasting glucose, HbA1c, lipid profile.",
            ]

        risk_card(risk, confidence, tips)

        try:
            import plotly.graph_objects as go
            labels = ["BMI", "BP", "Cholesterol", "Activity", "Age", "Phys Health"]
            vals = [
                min((bmi - 10) / 88 * 100, 100),
                yn(high_bp) * 80,
                yn(high_chol) * 80,
                0 if phys_act == "Yes" else 70,
                age_val / 13 * 100,
                phys_hlth / 30 * 100,
            ]
            fig = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=labels + [labels[0]],
                fill="toself",
                fillcolor="rgba(239,68,68,0.12)",
                line=dict(color="#EF4444", width=2)
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(19,29,50,0.8)",
                    radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1E3050",
                                   tickfont=dict(color="#7A94B4", size=9)),
                    angularaxis=dict(gridcolor="#1E3050", tickfont=dict(color="#CBD5E1", size=11))
                ),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, margin=dict(t=30, b=30, l=40, r=40), height=320,
            )
            st.markdown("**Risk Factor Profile**")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        save_screening("diabetes", risk, confidence,
                       age=age_val * 5 + 18,
                       sex=sex.lower(), symptom_notes=symptom_notes)
        st.success("✅ Result saved to history.")
