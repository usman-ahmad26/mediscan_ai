"""pages/login.py — Login and Register page"""

import streamlit as st
from auth import register_user, login_user

def show():
    from ui.theme import apply_global_theme
    apply_global_theme()

    st.markdown("<h1>🩺 MediScan AI</h1>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    # ── LOGIN ─────────────────────────────────────────────────
    with tab1:
        st.markdown("##### Welcome back")

        email    = st.text_input("Email", key="login_email",
                                  placeholder="your@email.com")
        password = st.text_input("Password", type="password",
                                  key="login_password",
                                  placeholder="Enter your password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Login", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                result = login_user(email, password)
                if result["success"]:
                    st.session_state.logged_in = True
                    st.session_state.user = result["user"]
                    st.success(f"Welcome back, {result['user']['name']}!")
                    st.rerun()
                else:
                    st.error(result["message"])

    # ── REGISTER ──────────────────────────────────────────────
    with tab2:
        st.markdown("##### Create an account")

        name      = st.text_input("Full Name", key="reg_name",
                                   placeholder="Your full name")
        email_r   = st.text_input("Email", key="reg_email",
                                   placeholder="your@email.com")
        password_r = st.text_input("Password", type="password",
                                    key="reg_password",
                                    placeholder="Min. 6 characters")
        confirm   = st.text_input("Confirm Password", type="password",
                                   key="reg_confirm",
                                   placeholder="Repeat password")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Create Account", type="primary", use_container_width=True):
            if not all([name, email_r, password_r, confirm]):
                st.error("Please fill in all fields.")
            elif len(password_r) < 6:
                st.error("Password must be at least 6 characters.")
            elif password_r != confirm:
                st.error("Passwords do not match.")
            else:
                result = register_user(name, email_r, password_r)
                if result["success"]:
                    st.success("Account created! Please log in.")
                else:
                    st.error(result["message"])