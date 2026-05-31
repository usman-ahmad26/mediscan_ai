"""pages/heart.py — Heart Disease Prediction (BRFSS 2022 dataset)"""

import streamlit as st
import numpy as np
import joblib
import os
try:
    from db import save_screening
except:
    save_screening = lambda *args, **kwargs: None
from ui.theme import apply_global_theme
apply_global_theme()

MODELS_DIR = "models"

@st.cache_resource
def load_heart_model():
    mp = os.path.join(MODELS_DIR, "heart_model.pkl")
    sp = os.path.join(MODELS_DIR, "heart_scaler.pkl")
    fp = os.path.join(MODELS_DIR, "heart_feature_cols.pkl")
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
    st.markdown("<h1>❤️ Heart Disease Prediction</h1>", unsafe_allow_html=True)
    st.caption("Enter your health indicators to assess cardiac disease risk (CDC BRFSS 2022 model)")

    model, scaler, feature_cols = load_heart_model()
    model_ready = model is not None

    if not model_ready:
        st.warning("⚠️ Model not trained yet — form is shown for preview. Run `python predict.py` to enable predictions.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 1: Demographics & Medical History ─────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("##### 👤 Demographics & Lifestyle")
        sex = st.selectbox("Biological Sex", ["Male", "Female"])
        age_cat = st.selectbox("Age Category", [
            "18-24","25-29","30-34","35-39","40-44","45-49",
            "50-54","55-59","60-64","65-69","70-74","75-79","80 or older"
        ], index=8)
        bmi = st.number_input("BMI", 10.0, 60.0, 27.0, step=0.1, help="Body Mass Index")
        physical_activity = st.selectbox("Physically Active (past 30 days)?", ["Yes", "No"])
        sleep_time = st.slider("Average Sleep per Night (hours)", 1, 24, 7)
        gen_health = st.selectbox("General Health", ["Excellent", "Very good", "Good", "Fair", "Poor"])
        physical_health = st.slider("Days of Poor Physical Health (last 30 days)", 0, 30, 0)
        mental_health = st.slider("Days of Poor Mental Health (last 30 days)", 0, 30, 0)

    with col2:
        st.markdown("##### 🫀 Medical History")
        smoking     = st.selectbox("Smoked ≥100 cigarettes in lifetime?", ["No", "Yes"])
        alcohol     = st.selectbox("Heavy Alcohol Use?", ["No", "Yes"],
                                   help="Men >14 drinks/week, Women >7 drinks/week")
        stroke      = st.selectbox("Ever had a Stroke?", ["No", "Yes"])
        diff_walking= st.selectbox("Difficulty Walking / Climbing Stairs?", ["No", "Yes"])
        diabetic    = st.selectbox("Diabetic Status",
                                   ["No", "Yes", "No, borderline diabetes", "Yes (during pregnancy)"])
        asthma      = st.selectbox("Asthma?", ["No", "Yes"])
        kidney_dis  = st.selectbox("Kidney Disease?", ["No", "Yes"])
        skin_cancer = st.selectbox("Skin Cancer?", ["No", "Yes"])

    # ── Symptom notes full width ───────────────────────────────────────────────
    symptom_notes = st.text_area(
        "Symptom Notes (optional)",
        placeholder="e.g. chest tightness, shortness of breath, palpitations..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Predict Heart Disease Risk", type="primary"):
        if not model_ready:
            st.error("Models not trained yet. Run `python predict.py` first.")
            return

        age_order = ["18-24","25-29","30-34","35-39","40-44","45-49",
                     "50-54","55-59","60-64","65-69","70-74","75-79","80 or older"]
        gen_order = ["Poor", "Fair", "Good", "Very good", "Excellent"]
        diabetic_map = {"No": 0, "Yes": 1,
                        "No, borderline diabetes": 2, "Yes (during pregnancy)": 3}

        raw = {
            "BMI":              bmi,
            "Smoking":          1 if smoking == "Yes" else 0,
            "AlcoholDrinking":  1 if alcohol == "Yes" else 0,
            "Stroke":           1 if stroke == "Yes" else 0,
            "PhysicalHealth":   float(physical_health),
            "MentalHealth":     float(mental_health),
            "DiffWalking":      1 if diff_walking == "Yes" else 0,
            "Sex":              1 if sex == "Male" else 0,
            "AgeCategory":      age_order.index(age_cat),
            "Race":             0,
            "Diabetic":         diabetic_map.get(diabetic, 0),
            "PhysicalActivity": 1 if physical_activity == "Yes" else 0,
            "GenHealth":        gen_order.index(gen_health),
            "SleepTime":        float(sleep_time),
            "Asthma":           1 if asthma == "Yes" else 0,
            "KidneyDisease":    1 if kidney_dis == "Yes" else 0,
            "SkinCancer":       1 if skin_cancer == "Yes" else 0,
        }

        feat_vec = np.array([[raw.get(f, 0) for f in feature_cols]], dtype=float)
        feat_scaled = scaler.transform(feat_vec)
        prob = model.predict_proba(feat_scaled)[0][1]
        confidence = round(prob * 100, 1)

        if prob < 0.35:
            risk = "Low Risk"
            tips = [
                "Maintain your current heart-healthy habits.",
                "Get an annual BP and cholesterol check.",
                "Continue 150+ min/week of moderate aerobic activity.",
            ]
        elif prob < 0.65:
            risk = "Medium Risk"
            tips = [
                "Schedule a cardiac checkup within the next 2–4 weeks.",
                "Monitor blood pressure daily.",
                "Reduce sodium, saturated fat, and processed sugar intake.",
                "Aim for 7–9 hours sleep per night.",
            ]
        else:
            risk = "High Risk"
            tips = [
                "Consult a cardiologist for a formal ECG evaluation promptly.",
                "Do not delay — high-risk indicators require clinical assessment.",
                "Avoid strenuous exercise until cleared by a physician.",
                "Strictly reduce sodium, alcohol, and tobacco if applicable.",
            ]

        risk_card(risk, confidence, tips)

        try:
            import plotly.graph_objects as go
            age_order_list = ["18-24","25-29","30-34","35-39","40-44","45-49",
                              "50-54","55-59","60-64","65-69","70-74","75-79","80 or older"]
            labels = ["BMI", "Phys Health", "Mental Health", "Sleep", "Age", "Activity"]
            vals = [
                min((bmi - 10) / 50 * 100, 100),
                physical_health / 30 * 100,
                mental_health / 30 * 100,
                max(0, (8 - sleep_time) / 8 * 100),
                age_order_list.index(age_cat) / 12 * 100,
                0 if physical_activity == "Yes" else 60,
            ]
            fig = go.Figure(go.Scatterpolar(
                r=vals + [vals[0]], theta=labels + [labels[0]],
                fill="toself",
                fillcolor="rgba(14,165,233,0.15)",
                line=dict(color="#0EA5E9", width=2)
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

        save_screening("heart", risk, confidence,
                       age=age_order.index(age_cat) * 5 + 21,
                       sex=sex.lower(), symptom_notes=symptom_notes)
        st.success("✅ Result saved to history.")
