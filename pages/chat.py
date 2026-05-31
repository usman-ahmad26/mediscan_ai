"""pages/chat.py — Symptom Chat powered by Gemini 2.5 Flash"""

import streamlit as st
import google.generativeai as genai

from dotenv import load_dotenv
import os

from db import get_db
from datetime import datetime
from ui.theme import apply_global_theme
apply_global_theme()



# ─────────────────────────────────────────────────────────────
# LOAD ENV VARIABLES
# ─────────────────────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ─────────────────────────────────────────────────────────────
# CONFIGURE GEMINI
# ─────────────────────────────────────────────────────────────

genai.configure(api_key=GEMINI_API_KEY)

# ─────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are MediScan AI, an intelligent medical screening assistant specializing in cardiovascular disease and diabetes risk assessment.

You have deep knowledge of:
- Heart disease risk factors: cholesterol, blood pressure, BMI, smoking, physical activity, age, sex, chest pain types, ECG abnormalities, ST depression
- Diabetes risk factors: blood glucose, HbA1c, insulin resistance, BMI, family history, physical inactivity, diet, age
- CDC BRFSS survey methodology and what each indicator means clinically
- How ML models like Random Forest, SVM, Decision Tree, Naive Bayes and KNN work for disease classification
- How to interpret prediction confidence scores and risk levels

Your capabilities:
1. SYMPTOM ANALYSIS — When a user describes symptoms, identify the most likely risk category, explain what those symptoms indicate medically, and suggest which screening module to run
2. RESULT EXPLANATION — When a user shares their prediction result (e.g. "I got High Risk 82% for diabetes"), explain what that means clinically, what factors likely drove it, and what next steps to take
3. HEALTH EDUCATION — Explain medical terms in plain language (e.g. what is ST depression, what does BMI mean, what is HbA1c)
4. PRE-SCREENING GUIDANCE — Help users understand what inputs they need before running a screening (e.g. "you'll need your fasting glucose reading for the diabetes module")
5. RISK FACTOR DISCUSSION — Have a genuine conversation about the user's lifestyle, diet, exercise habits and explain how each affects their disease risk
6. FOLLOW-UP QUESTIONS — Ask clarifying questions to better understand the user's situation before making recommendations

Tone:
- Empathetic, clear, and professional
- Use plain language — avoid excessive medical jargon unless the user seems medically literate
- Be genuinely helpful, not just a redirect bot
- Give substantive answers, not one-liners

Hard rules:
- Never provide a definitive diagnosis
- Never prescribe or recommend specific medications
- Always recommend consulting a qualified doctor for formal diagnosis
- For emergency symptoms (chest pain, shortness of breath, fainting, severe dizziness, numbness) — immediately advise seeking emergency medical attention
- Keep responses concise — 3 to 5 sentences unless the user asks for more detail
"""

# ─────────────────────────────────────────────────────────────
# GEMINI MODEL
# ─────────────────────────────────────────────────────────────

gemini_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=SYSTEM_PROMPT
)

# ─────────────────────────────────────────────────────────────
# EMERGENCY KEYWORDS
# ─────────────────────────────────────────────────────────────

EMERGENCY_KEYWORDS = [
    "chest pain",
    "shortness of breath",
    "fainting",
    "stroke",
    "numbness",
    "severe dizziness"
]

# ─────────────────────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────────────────────

def show():

    st.markdown(
        "<h1>💬 Symptom Chat</h1>",
        unsafe_allow_html=True
    )

    st.caption(
        "Describe your symptoms in plain language."
    )

    # ─────────────────────────────────────────────────────────
    # CHAT HISTORY
    # ─────────────────────────────────────────────────────────

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # ─────────────────────────────────────────────────────────
    # INTRO CARD
    # ─────────────────────────────────────────────────────────

    if not st.session_state.chat_history:

        st.info("""
        🤖 Describe your symptoms naturally.

        Example:
        - Chest tightness while walking
        - Excessive thirst and fatigue
        - Blurry vision and tingling feet
        """)

    # ─────────────────────────────────────────────────────────
    # DISPLAY HISTORY
    # ─────────────────────────────────────────────────────────

    for msg in st.session_state.chat_history:

        with st.chat_message(
            msg["role"],
            avatar="🧑" if msg["role"] == "user" else "🩺"
        ):

            st.markdown(msg["content"])

    # ─────────────────────────────────────────────────────────
    # USER INPUT
    # ─────────────────────────────────────────────────────────

    user_input = st.chat_input(
        "Describe your symptoms..."
    )

    if user_input:

        # USER MESSAGE

        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("user", avatar="🧑"):

            st.markdown(user_input)

        # ─────────────────────────────────────────────────────
        # EMERGENCY DETECTION
        # ─────────────────────────────────────────────────────

        emergency_detected = any(
            keyword in user_input.lower()
            for keyword in EMERGENCY_KEYWORDS
        )

        # ─────────────────────────────────────────────────────
        # ASSISTANT RESPONSE
        # ─────────────────────────────────────────────────────

        with st.chat_message("assistant", avatar="🩺"):

            with st.spinner("Analysing symptoms..."):

                try:

                    # BUILD CHAT HISTORY

                    history = []

                    for msg in st.session_state.chat_history[:-1]:

                        history.append({
                            "role": "user" if msg["role"] == "user" else "model",
                            "parts": [msg["content"]]
                        })

                    # START CHAT

                    chat = gemini_model.start_chat(
                        history=history
                    )

                    response = chat.send_message(
                        user_input
                    )

                    reply = response.text

                except Exception as e:

                    reply = f"""
                    ⚠️ Unable to connect to Gemini API.

                    Error:
                    {str(e)}

                    Please check:
                    - Internet connection
                    - Gemini API key
                    """

                # ─────────────────────────────────────────────
                # EMERGENCY WARNING
                # ─────────────────────────────────────────────

                if emergency_detected:

                    st.error("""
                    🚨 Possible emergency symptoms detected.

                    Please seek immediate medical attention
                    or contact emergency services.
                    """)

                # ─────────────────────────────────────────────
                # TYPING EFFECT
                # ─────────────────────────────────────────────

                placeholder = st.empty()

                typed_text = ""

                for char in reply:

                    typed_text += char

                    placeholder.markdown(typed_text)

                # ─────────────────────────────────────────────
                # SCREENING RECOMMENDATIONS
                # ─────────────────────────────────────────────

                if "diabetes" in reply.lower():

                    st.info(
                        "🩸 Recommended Screening: Diabetes"
                    )

                if "heart" in reply.lower():

                    st.info(
                        "❤️ Recommended Screening: Heart Disease"
                    )

                # ─────────────────────────────────────────────
                # SAVE TO CHAT HISTORY
                # ─────────────────────────────────────────────

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": reply
                })

                # ─────────────────────────────────────────────
                # SAVE TO MONGODB
                # ─────────────────────────────────────────────

                try:

                    db = get_db()

                    db.chat_logs.insert_one({

                        "user_message": user_input,

                        "assistant_reply": reply,

                        "timestamp": datetime.utcnow()

                    })

                except:
                    pass

    # ─────────────────────────────────────────────────────────
    # CLEAR CHAT
    # ─────────────────────────────────────────────────────────

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()

    # ─────────────────────────────────────────────────────────
    # DISCLAIMER
    # ─────────────────────────────────────────────────────────

    st.caption(
        "⚠️ MediScan AI is an educational AI-assisted symptom triage system and not a substitute for professional medical diagnosis."
    )
