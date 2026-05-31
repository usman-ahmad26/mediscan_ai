"""
db.py
=====
Shared database layer for MediScan AI.
Primary  : MongoDB (mediscan-db) with 3 optimised indexes.
Fallback : SQLite  (mediscan_history.db) — used automatically when
           MongoDB is unavailable (Streamlit Cloud, local dev without Mongo).
"""

import sqlite3
import uuid
from datetime import datetime, timezone

import streamlit as st

MONGO_URI = MONGO_URI = "mongodb+srv://usman_db_user:usmanahmad26_@cluster0.kargqq9.mongodb.net/?appName=Cluster0"
SQLITE_PATH = "mediscan_history.db"

# ─────────────────────────────────────────────────────────────
# MongoDB
# ─────────────────────────────────────────────────────────────

@st.cache_resource
def get_db():
    """Returns MongoDB database object, or None if unavailable."""
    try:
        from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
        from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")          # fail fast if no server
        db = client["mediscan-db"]
        _ensure_indexes(db)
        return db
    except Exception:
        return None


def _ensure_indexes(db):
    try:
        from pymongo import ASCENDING, DESCENDING, TEXT
        from pymongo.errors import OperationFailure

        # Index 1: disease + risk + timestamp  (compound)
        db["screenings"].create_index(
            [("disease_type", ASCENDING),
             ("final_risk",   ASCENDING),
             ("timestamp",    DESCENDING)],
            name="idx_disease_risk_timestamp", background=True
        )
        # Index 2: full-text search on symptom_notes
        db["screenings"].create_index(
            [("symptom_notes", TEXT)],
            name="idx_symptom_notes_text", background=True
        )
        # Index 3: TTL on sessions — auto-delete after 24 h
        db["sessions"].create_index(
            [("createdAt", ASCENDING)],
            name="idx_sessions_ttl",
            expireAfterSeconds=86400, background=True
        )
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────
# SQLite helpers (always available)
# ─────────────────────────────────────────────────────────────

def _sqlite_init():
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            disease     TEXT,
            risk        TEXT,
            confidence  REAL,
            age         INTEGER,
            sex         TEXT,
            notes       TEXT,
            timestamp   TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_screening(disease_type: str, final_risk: str, confidence: float,
                   age: int, sex: str, symptom_notes: str = ""):
    """Save a screening result to both MongoDB (if available) and SQLite."""
    ts = datetime.now(timezone.utc)

    # 1. SQLite (always)
    _sqlite_init()
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (disease,risk,confidence,age,sex,notes,timestamp) VALUES (?,?,?,?,?,?,?)",
        (disease_type, final_risk, confidence, age, sex, symptom_notes,
         ts.strftime("%Y-%m-%d %H:%M"))
    )
    conn.commit()
    conn.close()

    # 2. MongoDB (optional)
    db = get_db()
    if db is not None:
        try:
            doc = {
                "screeningId":   str(uuid.uuid4()),
                "disease_type":  disease_type,
                "final_risk":    final_risk,
                "confidence":    confidence,
                "age":           age,
                "sex":           sex,
                "symptom_notes": symptom_notes,
                "timestamp":     ts,
            }
            db["screenings"].insert_one(doc)
            db["sessions"].insert_one({
                "sessionId":    str(uuid.uuid4()),
                "disease_type": disease_type,
                "createdAt":    ts,
            })
        except Exception:
            pass


def load_history_sqlite(limit: int = 200):
    """Load prediction history from SQLite as a list of dicts."""
    _sqlite_init()
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT disease,risk,confidence,age,sex,notes,timestamp "
        "FROM history ORDER BY id DESC LIMIT ?", (limit,)
    )
    rows = c.fetchall()
    conn.close()
    cols = ["Disease", "Risk", "Confidence (%)", "Age", "Sex", "Notes", "Timestamp"]
    return [dict(zip(cols, r)) for r in rows]


def clear_history_sqlite():
    """Wipe all history from SQLite."""
    _sqlite_init()
    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
