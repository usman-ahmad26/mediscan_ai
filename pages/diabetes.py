"""pages/diabetes.py — Diabetes Risk Prediction (Simplified for Users)"""

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
    st.markdown("<h1>🩸 Diabetes Risk Assessment</h1>", unsafe_allow_html=True)
    st.caption("Answer a few simple questions to understand your diabetes risk")

    model, scaler, feature_cols = load_diabetes_model()
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
        st.markdown("##### 🏥 Medical History")
        high_bp = st.selectbox("Do you have high blood pressure?", ["No", "Yes"])
        high_chol = st.selectbox("Do you have high cholesterol?", ["No", "Yes"])
        family_diabetes = st.selectbox(
            "Does anyone in your immediate family have diabetes?",
            ["No", "Yes, parent", "Yes, sibling", "Yes, both parent and sibling"]
        )

    st.markdown("---")

    # ── Row 2: Lifestyle ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("##### 🏃‍♂️ Your Lifestyle")
        phys_act = st.selectbox(
            "How often do you exercise?",
            ["Rarely or never", "1-2 times per week", "3-4 times per week", "5+ times per week"]
        )
        
        diet = st.selectbox(
            "How would you describe your diet?",
            ["Very healthy (lots of vegetables, whole grains)",
             "Somewhat healthy",
             "Average",
             "Somewhat unhealthy (lots of sugar, processed food)",
             "Very unhealthy (regular sugary drinks, fast food)"]
        )

    with col2:
        st.markdown("##### 💪 Your Health")
        gen_hlth = st.selectbox(
            "How would you rate your general health?",
            ["Excellent", "Very good", "Good", "Fair", "Poor"]
        )
        
        smoking = st.selectbox("Do you currently smoke?", ["No", "Yes"])

    st.markdown("---")

    # ── Row 3: Symptoms ──────────────────────────────────────────────────────
    st.markdown("##### 🩸 Common Symptoms")

    col1, col2 = st.columns(2)

    with col1:
        thirsty = st.selectbox(
            "Do you feel unusually thirsty often?",
            ["No", "Yes, sometimes", "Yes, frequently"]
        )
        urination = st.selectbox(
            "Do you need to urinate frequently (especially at night)?",
            ["No", "Yes, sometimes", "Yes, frequently"]
        )

    with col2:
        blurred_vision = st.selectbox(
            "Do you experience blurred vision?",
            ["No", "Yes, sometimes", "Yes, frequently"]
        )
        fatigue = st.selectbox(
            "Do you feel unusually tired or fatigued?",
            ["No", "Yes, sometimes", "Yes, frequently"]
        )

    st.markdown("---")

    # ── Symptom notes ─────────────────────────────────────────────────────────
    symptom_notes = st.text_area(
        "📝 Symptom Notes (optional)",
        placeholder="e.g. frequent urination, extreme thirst, fatigue, blurry vision, slow-healing cuts...",
        height=80
    )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔍 Check My Diabetes Risk", type="primary"):
        if not model_ready:
            st.error("Models not trained yet. Run `python predict.py` first.")
            return

        # Map values to model features
        yn = lambda v: 1 if v == "Yes" else 0
        
        # Age group for model (1-13 scale)
        age_list = ["18–24","25–29","30–34","35–39","40–44",
                    "45–49","50–54","55–59","60–64","65–69",
                    "70–74","75–79","80+"]
        
        # Convert age to age group
        if age < 25:
            age_grp = "18–24"
        elif age < 30:
            age_grp = "25–29"
        elif age < 35:
            age_grp = "30–34"
        elif age < 40:
            age_grp = "35–39"
        elif age < 45:
            age_grp = "40–44"
        elif age < 50:
            age_grp = "45–49"
        elif age < 55:
            age_grp = "50–54"
        elif age < 60:
            age_grp = "55–59"
        elif age < 65:
            age_grp = "60–64"
        elif age < 70:
            age_grp = "65–69"
        elif age < 75:
            age_grp = "70–74"
        elif age < 80:
            age_grp = "75–79"
        else:
            age_grp = "80+"
        
        age_val = age_list.index(age_grp) + 1
        
        # Map physical activity
        phys_act_map = {
            "Rarely or never": 0,
            "1-2 times per week": 1,
            "3-4 times per week": 2,
            "5+ times per week": 3
        }
        phys_act_val = phys_act_map[phys_act]
        
        # Map diet to fruits/veggies
        if diet in ["Very healthy (lots of vegetables, whole grains)", "Somewhat healthy"]:
            fruits_val = 1
            veggies_val = 1
        else:
            fruits_val = 0
            veggies_val = 0
        
        # Map general health
        gen_map = {"Excellent": 1, "Very good": 2, "Good": 3, "Fair": 4, "Poor": 5}
        gen_hlth_val = gen_map[gen_hlth]
        
        # Map family history
        family_map = {
            "No": 0,
            "Yes, parent": 1,
            "Yes, sibling": 1,
            "Yes, both parent and sibling": 2
        }
        family_val = family_map[family_diabetes]
        
        # Calculate symptom score
        symptom_score = 0
        if thirsty == "Yes, sometimes": symptom_score += 1
        elif thirsty == "Yes, frequently": symptom_score += 2
        if urination == "Yes, sometimes": symptom_score += 1
        elif urination == "Yes, frequently": symptom_score += 2
        if blurred_vision == "Yes, sometimes": symptom_score += 1
        elif blurred_vision == "Yes, frequently": symptom_score += 2
        if fatigue == "Yes, sometimes": symptom_score += 1
        elif fatigue == "Yes, frequently": symptom_score += 2

        raw = {
            "HighBP": yn(high_bp),
            "HighChol": yn(high_chol),
            "CholCheck": 1,  # Assume most have had it checked
            "BMI": bmi,
            "Smoker": yn(smoking),
            "Stroke": 0,
            "HeartDiseaseorAttack": 0,
            "PhysActivity": phys_act_val,
            "Fruits": fruits_val,
            "Veggies": veggies_val,
            "HvyAlcoholConsump": 0,
            "AnyHealthcare": 1,
            "NoDocbcCost": 0,
            "GenHlth": gen_hlth_val,
            "MentHlth": 0,
            "PhysHlth": 0,
            "DiffWalk": 0,
            "Sex": 1 if sex == "Male" else 0,
            "Age": float(age_val),
            "Education": 4,  # Default some college
            "Income": 6,  # Default middle income
        }

        try:
            feat_vec = np.array([[raw.get(f, 0) for f in feature_cols]], dtype=float)
            feat_scaled = scaler.transform(feat_vec)
            prob = model.predict_proba(feat_scaled)[0][1]
            confidence = round(prob * 100, 1)
        except Exception as e:
            st.error(f"Prediction error: {e}")
            confidence = 50

        # Adjust confidence based on symptoms
        if symptom_score >= 4:
            confidence = min(confidence + 10, 95)
        elif symptom_score >= 2:
            confidence = min(confidence + 5, 95)

        if prob < 0.35:
            risk = "Low Risk"
            tips = [
                "✅ Great job! Keep maintaining your healthy habits",
                "🥗 Eat balanced meals with plenty of vegetables and whole grains",
                "🏃‍♂️ Stay active — 30 minutes of walking, 5 days a week",
                "🍎 Limit sugary drinks and processed foods",
                "🩺 Get your blood sugar checked during annual check-ups"
            ]
        elif prob < 0.65:
            risk = "Medium Risk"
            tips = [
                "🩺 Ask your doctor about getting a simple blood sugar test",
                "🍎 Cut back on sugary drinks, white bread, and sweets",
                "🏃‍♂️ Start moving — even 15 minutes of daily walking helps",
                "🥗 Add more vegetables and fiber to your meals",
                "😴 Aim for 7-8 hours of quality sleep each night",
                "📉 If overweight, losing 5-10% of body weight can help significantly"
            ]
        else:
            risk = "High Risk"
            tips = [
                "🚨 **Please see a doctor for a blood sugar test within 2 weeks**",
                "🍎 **IMMEDIATELY** reduce sugar intake — no sodas, sweets, or juices",
                "🏃‍♂️ Start with daily walking — even 10-15 minutes helps",
                "🥗 Eat vegetables with every meal, choose whole grains",
                "💧 Drink water instead of sugary beverages",
                "📉 Weight loss of 5-10% can dramatically reduce your risk"
            ]

        risk_card(risk, confidence, tips)

        # Simple radar chart
        try:
            import plotly.graph_objects as go
            labels = ["BMI", "BP", "Cholesterol", "Activity", "Diet", "Age"]
            vals = [
                min((bmi - 10) / 88 * 100, 100),
                80 if high_bp == "Yes" else 0,
                80 if high_chol == "Yes" else 0,
                0 if phys_act == "Rarely or never" else 70,
                0 if "Very healthy" in diet else 50 if diet == "Average" else 80,
                age_val / 13 * 100,
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
            st.markdown("**Your Health Profile**")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

        save_screening("diabetes", risk, confidence,
                       age=age,
                       sex=sex.lower(), symptom_notes=symptom_notes)
        st.success("✅ Your results have been saved.")