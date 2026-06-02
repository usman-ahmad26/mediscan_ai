"""pages/heart.py — Heart Disease Prediction (Simplified for Users)"""

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
    st.markdown("<h1>❤️ Heart Disease Risk Assessment</h1>", unsafe_allow_html=True)
    st.caption("Answer a few simple questions to understand your heart health risk")

    model, scaler, feature_cols = load_heart_model()
    model_ready = model is not None

    if not model_ready:
        st.warning("⚠️ Model not trained yet — form is shown for preview. Run `python predict.py` to enable predictions.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Patient Name ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        patient_name = st.text_input("Your Name (optional)", placeholder="Enter your name")
    with col2:
        age = st.number_input("Your Age", 18, 100, 45, help="How old are you?")

    st.markdown("---")

    # ── Row 1: Basic Health Info ─────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("##### 👤 About You")
        sex = st.selectbox("Gender", ["Male", "Female"])
        
        weight = st.number_input("Your Weight (kg)", 30, 200, 70, help="Enter your weight in kilograms")
        height = st.number_input("Your Height (cm)", 100, 220, 170, help="Enter your height in centimeters")
        
        if height > 0:
            bmi = weight / ((height/100) ** 2)
        else:
            bmi = 25.0
        st.caption(f"Your BMI: {bmi:.1f}")

    with col2:
        st.markdown("##### 🩺 Medical History")
        smoking = st.selectbox("Do you currently smoke?", ["No", "Yes"])
        high_bp = st.selectbox("Do you have high blood pressure?", ["No", "Yes"])
        diabetic = st.selectbox("Do you have diabetes?", ["No", "Yes"])

    st.markdown("---")

    # ── Row 2: Lifestyle ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("##### 🏃‍♂️ Your Lifestyle")
        physical_activity = st.selectbox(
            "How often do you exercise?",
            ["Rarely or never", "1-2 times per week", "3-4 times per week", "5+ times per week"]
        )
        
        sleep_time = st.selectbox(
            "How many hours do you sleep on average?",
            ["Less than 6 hours", "6-7 hours", "7-8 hours", "More than 8 hours"]
        )

    with col2:
        st.markdown("##### 💪 Your Health")
        gen_health = st.selectbox(
            "How would you rate your general health?",
            ["Poor", "Fair", "Good", "Very good", "Excellent"]
        )
        
        chest_pain = st.selectbox(
            "Do you experience chest discomfort?",
            ["No", "Yes, during exercise", "Yes, at rest", "Yes, randomly"]
        )

    st.markdown("---")

    # ── Symptom notes full width ───────────────────────────────────────────────
    symptom_notes = st.text_area(
        "📝 Symptom Notes (optional)",
        placeholder="e.g. chest tightness, shortness of breath, palpitations, dizziness...",
        height=80
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Check My Heart Risk", type="primary"):
        if not model_ready:
            st.error("Models not trained yet. Run `python predict.py` first.")
            return

        # Map values to model features
        age_cat_list = ["18-24","25-29","30-34","35-39","40-44","45-49",
                        "50-54","55-59","60-64","65-69","70-74","75-79","80 or older"]
        
        # Convert age to age category
        if age < 25:
            age_cat = "18-24"
        elif age < 30:
            age_cat = "25-29"
        elif age < 35:
            age_cat = "30-34"
        elif age < 40:
            age_cat = "35-39"
        elif age < 45:
            age_cat = "40-44"
        elif age < 50:
            age_cat = "45-49"
        elif age < 55:
            age_cat = "50-54"
        elif age < 60:
            age_cat = "55-59"
        elif age < 65:
            age_cat = "60-64"
        elif age < 70:
            age_cat = "65-69"
        elif age < 75:
            age_cat = "70-74"
        elif age < 80:
            age_cat = "75-79"
        else:
            age_cat = "80 or older"
        
        # Map physical activity
        phys_act_map = {
            "Rarely or never": 0,
            "1-2 times per week": 1,
            "3-4 times per week": 2,
            "5+ times per week": 3
        }
        physical_activity_val = phys_act_map[physical_activity]
        
        # Map sleep time
        sleep_map = {
            "Less than 6 hours": 5,
            "6-7 hours": 7,
            "7-8 hours": 7.5,
            "More than 8 hours": 8
        }
        sleep_time_val = sleep_map[sleep_time]
        
        # Map general health (reverse order for model)
        health_map = {
            "Poor": 1,
            "Fair": 2,
            "Good": 3,
            "Very good": 4,
            "Excellent": 5
        }
        gen_health_val = health_map[gen_health]
        
        # Chest pain presence
        chest_pain_val = 1 if chest_pain != "No" else 0

        raw = {
            "BMI": bmi,
            "Smoking": 1 if smoking == "Yes" else 0,
            "AlcoholDrinking": 0,  # Default for simplicity
            "Stroke": 0,  # Default for simplicity
            "PhysicalHealth": 0,  # Default for simplicity
            "MentalHealth": 0,  # Default for simplicity
            "DiffWalking": 0,  # Default for simplicity
            "Sex": 1 if sex == "Male" else 0,
            "AgeCategory": age_cat_list.index(age_cat),
            "Race": 0,
            "Diabetic": 1 if diabetic == "Yes" else 0,
            "PhysicalActivity": physical_activity_val,
            "GenHealth": gen_health_val,
            "SleepTime": sleep_time_val,
            "Asthma": 0,  # Default for simplicity
            "KidneyDisease": 0,  # Default for simplicity
            "SkinCancer": 0,  # Default for simplicity
            "HighBP": 1 if high_bp == "Yes" else 0,  # Add HighBP if needed
        }

        # Create feature vector
        try:
            feat_vec = np.array([[raw.get(f, 0) for f in feature_cols]], dtype=float)
            feat_scaled = scaler.transform(feat_vec)
            prob = model.predict_proba(feat_scaled)[0][1]
            confidence = round(prob * 100, 1)
        except Exception as e:
            st.error(f"Prediction error: {e}")
            confidence = 50

        if prob < 0.35:
            risk = "Low Risk"
            tips = [
                "✅ Keep up the good work with your healthy habits!",
                "🏃‍♂️ Stay active — aim for 30 minutes of exercise, 5 days a week",
                "🥗 Eat a balanced diet with plenty of fruits and vegetables",
                "🩺 Get an annual check-up including blood pressure and cholesterol",
            ]
        elif prob < 0.65:
            risk = "Medium Risk"
            tips = [
                "🩺 Schedule a check-up with your doctor within the next month",
                "🏃‍♂️ Start moving — even 15-20 minutes of daily walking helps",
                "🍎 Cut back on salt, fried foods, and sugary drinks",
                "😴 Prioritize 7-8 hours of sleep each night",
                "📊 Monitor your blood pressure regularly if possible",
            ]
        else:
            risk = "High Risk"
            tips = [
                "🚨 **Please see a doctor within the next 1-2 weeks**",
                "❤️ Don't ignore symptoms like chest pain or shortness of breath",
                "🏃‍♂️ Start with light activity like walking — consult your doctor first",
                "🥗 Immediately reduce salt, saturated fats, and processed foods",
                "😴 Get 7-8 hours of sleep and manage stress levels",
            ]

        risk_card(risk, confidence, tips)

        # Simple radar chart
        try:
            import plotly.graph_objects as go
            labels = ["BMI", "Smoking", "BP", "Diabetes", "Exercise", "Sleep"]
            vals = [
                min((bmi - 10) / 50 * 100, 100),
                100 if smoking == "Yes" else 0,
                100 if high_bp == "Yes" else 0,
                100 if diabetic == "Yes" else 0,
                0 if physical_activity == "Rarely or never" else 60 if physical_activity == "1-2 times per week" else 80,
                min(max((sleep_time_val - 5) / 4 * 100, 0), 100),
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
            st.markdown("**Your Health Profile**")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        save_screening("heart", risk, confidence,
                       age=age,
                       sex=sex.lower(), symptom_notes=symptom_notes)
        st.success("✅ Your results have been saved.")
