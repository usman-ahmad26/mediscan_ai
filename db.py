"""
db.py
=====
Shared database layer for MediScan AI.
Primary  : MongoDB
Fallback : SQLite (FULL REPLACEMENT INTERFACE)
"""

import streamlit as st
import sqlite3
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient, ASCENDING, TEXT

MONGO_URI = "mongodb+srv://usman_db_user:usmanahmad26_@cluster0.kargqq9.mongodb.net/?retryWrites=true&w=majority"
SQLITE_PATH = "mediscan_history.db"


# ─────────────────────────────────────────────
# SQLITE IMPLEMENTATION (FULL FALLBACK DB)
# ─────────────────────────────────────────────

class SQLiteUsersCollection:
    def __init__(self, conn):
        self.conn = conn
        self._init()

    def _init(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                password TEXT,
                created_at TEXT,
                role TEXT
            )
        """)
        self.conn.commit()

    def find_one(self, query):
        cur = self.conn.cursor()
        cur.execute("SELECT name,email,password,role FROM users WHERE email=?",
                    (query.get("email"),))
        row = cur.fetchone()
        if not row:
            return None

        return {
            "name": row[0],
            "email": row[1],
            "password": row[2],
            "role": row[3]
        }

    def insert_one(self, doc):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO users (name,email,password,created_at,role)
            VALUES (?,?,?,?,?)
        """, (
            doc["name"],
            doc["email"],
            doc["password"],
            doc.get("created_at"),
            doc.get("role", "patient")
        ))
        self.conn.commit()


class SQLiteDB:
    def __init__(self):
        self.conn = sqlite3.connect(SQLITE_PATH, check_same_thread=False)
        self.users = SQLiteUsersCollection(self.conn)


# ─────────────────────────────────────────────
# MONGO CONNECTION
# ─────────────────────────────────────────────

def _ensure_indexes(db):
    try:
        db["screenings"].create_index(
            [("disease_type", ASCENDING),
             ("final_risk", ASCENDING),
             ("timestamp", ASCENDING)]
        )
        db["screenings"].create_index([("symptom_notes", TEXT)])
    except:
        pass


@st.cache_resource
def get_db():
    """
    ALWAYS RETURNS A VALID DB OBJECT:
    - MongoDB if healthy
    - SQLite fallback if not
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        db = client["mediscan-db"]
        _ensure_indexes(db)
        return db
    except Exception:
        return SQLiteDB()


# ─────────────────────────────────────────────
# SCREENING STORAGE (works for both DBs)
# ─────────────────────────────────────────────

def save_screening(disease_type, final_risk, confidence, age, sex, symptom_notes=""):
    ts = datetime.now(timezone.utc)

    db = get_db()

    # ── SQLITE PATH ─────────────────────────
    if isinstance(db, SQLiteDB):
        cur = db.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease TEXT,
                risk TEXT,
                confidence REAL,
                age INTEGER,
                sex TEXT,
                notes TEXT,
                timestamp TEXT
            )
        """)
        cur.execute("""
            INSERT INTO history (disease,risk,confidence,age,sex,notes,timestamp)
            VALUES (?,?,?,?,?,?,?)
        """, (disease_type, final_risk, confidence, age, sex,
              symptom_notes, ts.strftime("%Y-%m-%d %H:%M")))
        db.conn.commit()
        return

    # ── MONGO PATH ─────────────────────────
    try:
        db["screenings"].insert_one({
            "screeningId": str(uuid.uuid4()),
            "disease_type": disease_type,
            "final_risk": final_risk,
            "confidence": confidence,
            "age": age,
            "sex": sex,
            "symptom_notes": symptom_notes,
            "timestamp": ts
        })
    except:
        pass


# ─────────────────────────────────────────────
# HISTORY LOAD (SQLite only fallback view)
# ─────────────────────────────────────────────

def load_history_sqlite(limit=200):
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT disease,risk,confidence,age,sex,notes,timestamp
        FROM history ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()

    cols = ["Disease", "Risk", "Confidence (%)", "Age", "Sex", "Notes", "Timestamp"]
    return [dict(zip(cols, r)) for r in rows]

def clear_history_sqlite():
    conn = sqlite3.connect(SQLITE_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()