"""
MediScan AI — Main App
Run: streamlit run app.py
"""

import streamlit as st
from auth import is_logged_in, get_current_user, logout

st.set_page_config(
    page_title="MediScan AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui.theme import apply_global_theme
apply_global_theme()

# ── Session state ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = {}
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Auth gate ─────────────────────────────────────────────────
if not is_logged_in():
    from pages.login import show as show_login
    show_login()
    st.stop()

user = get_current_user()

# ── Nav items ─────────────────────────────────────────────────
NAV = [
    ("home",      "Home"),
    ("heart",     "Heart Disease"),
    ("diabetes",  "Diabetes"),
    ("chat",      "Symptom Chat"),
    ("compare",   "Models"),
    ("history",   "History"),
    ("analytics", "Analytics"),
]

# ── Handle nav via query params ───────────────────────────────
qp = st.query_params.get("nav", None)
if qp and qp != page:
    st.session_state.page = qp
    st.query_params.clear()
    st.rerun()

# ── Nav buttons (hidden, functional) ─────────────────────────
page = st.session_state.page
st.markdown('<div style="display:flex;gap:6px;padding:8px 0;flex-wrap:wrap">', unsafe_allow_html=True)
cols = st.columns(len(NAV) + 1)
for i, (key, label) in enumerate(NAV):
    with cols[i]:
        btn_type = "primary" if page == key else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state.page = key
            st.rerun()
with cols[-1]:
    if st.button("Logout", key="nav_logout", use_container_width=True, type="secondary"):
        logout()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div style="height:1px;background:rgba(255,255,255,0.05);margin-bottom:1.5rem"></div>', unsafe_allow_html=True)

# ── Page routing ──────────────────────────────────────────────
page = st.session_state.page

if page == "home":
    st.markdown("""
    <div style='padding:2rem 0 1.5rem 0'>
        <div style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
                    color:#F0F6FF;letter-spacing:-0.03em;line-height:1.2'>
            Early Detection,<br>
            <span style='background:linear-gradient(90deg,#38BDF8,#2563EB);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent'>
                Better Outcomes
            </span>
        </div>
        <div style='color:#4A6580;font-size:0.9rem;margin-top:0.6rem'>
            AI-powered screening for Heart Disease and Diabetes — powered by CDC BRFSS data
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown("""
        <div class='ms-card'>
            <div style='font-size:1.8rem;margin-bottom:0.6rem'>❤️</div>
            <div style='font-family:Syne,sans-serif;font-weight:700;
                        color:#F0F6FF;font-size:1rem;margin-bottom:0.4rem'>
                Heart Disease
            </div>
            <div style='color:#4A6580;font-size:0.82rem;line-height:1.5'>
                Assess cardiac risk using 17 lifestyle and clinical indicators
                from the CDC BRFSS 2022 dataset.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Heart Module", key="h_heart", use_container_width=True):
            st.session_state.page = "heart"
            st.rerun()

    with c2:
        st.markdown("""
        <div class='ms-card'>
            <div style='font-size:1.8rem;margin-bottom:0.6rem'>🩸</div>
            <div style='font-family:Syne,sans-serif;font-weight:700;
                        color:#F0F6FF;font-size:1rem;margin-bottom:0.4rem'>
                Diabetes
            </div>
            <div style='color:#4A6580;font-size:0.82rem;line-height:1.5'>
                Predict diabetes risk using 21 survey-based health indicators
                from the CDC BRFSS 2015 dataset.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Diabetes Module", key="h_diab", use_container_width=True):
            st.session_state.page = "diabetes"
            st.rerun()

    with c3:
        st.markdown("""
        <div class='ms-card'>
            <div style='font-size:1.8rem;margin-bottom:0.6rem'>💬</div>
            <div style='font-family:Syne,sans-serif;font-weight:700;
                        color:#F0F6FF;font-size:1rem;margin-bottom:0.4rem'>
                Symptom Chat
            </div>
            <div style='color:#4A6580;font-size:0.82rem;line-height:1.5'>
                Describe symptoms naturally. Gemini AI will identify risk
                patterns and recommend the right screening module.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Chat", key="h_chat", use_container_width=True):
            st.session_state.page = "chat"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.15);
                border-radius:12px;padding:0.8rem 1.2rem;font-size:12px;color:#FCA5A5'>
        ⚕️ MediScan AI is an educational screening tool and does not provide medical diagnosis.
        Always consult a qualified healthcare professional.
    </div>
    """, unsafe_allow_html=True)

elif page == "heart":
    from pages.heart import show
    show()

elif page == "diabetes":
    from pages.diabetes import show
    show()

elif page == "chat":
    from pages.chat import show
    show()

elif page == "compare":
    from pages.compare import show
    show()

elif page == "history":
    from pages.history import show
    show()

elif page == "analytics":
    from pages.analytics import show
    show()