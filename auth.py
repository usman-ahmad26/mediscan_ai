"""auth.py — Authentication layer for MediScan AI"""

import bcrypt
import streamlit as st
from db import get_db
from datetime import datetime


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def register_user(name: str, email: str, password: str) -> dict:
    db = get_db()
    if db is None:
        return {"success": False, "message": "Database unavailable."}

    existing = db.users.find_one({"email": email.lower().strip()})
    if existing:
        return {"success": False, "message": "An account with this email already exists."}

    db.users.insert_one({
        "name":       name.strip(),
        "email":      email.lower().strip(),
        "password":   hash_password(password),
        "created_at": datetime.utcnow(),
        "role":       "patient"
    })
    return {"success": True, "message": "Account created successfully."}


def login_user(email: str, password: str) -> dict:
    db = get_db()
    if db is None:
        return {"success": False, "message": "Database unavailable."}

    user = db.users.find_one({"email": email.lower().strip()})
    if not user:
        return {"success": False, "message": "No account found with this email."}

    if not verify_password(password, user["password"]):
        return {"success": False, "message": "Incorrect password."}

    return {
        "success": True,
        "user": {
            "name":  user["name"],
            "email": user["email"],
            "role":  user.get("role", "patient")
        }
    }


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_current_user() -> dict:
    return st.session_state.get("user", {})


def logout():
    st.session_state.logged_in = False
    st.session_state.user = {}
    st.rerun()


def require_login():
    """Call this at the top of any page that requires authentication."""
    if not is_logged_in():
        st.warning("Please log in to access this page.")
        st.stop()