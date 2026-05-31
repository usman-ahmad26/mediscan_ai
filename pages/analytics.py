"""pages/analytics.py — Analytics Dashboard (MongoDB pipelines + SQLite fallback)"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timezone
from db import get_db, load_history_sqlite
from ui.theme import apply_theme
apply_theme()

ASCENDING = 1
DESCENDING = -1

# ─────────────────────────────────────────────────────────────
# MongoDB Aggregation Pipelines
# ─────────────────────────────────────────────────────────────

def pipeline_risk_distribution(db):
    return list(db["screenings"].aggregate([
        {"$group": {
            "_id": {"disease_type": "$disease_type", "final_risk": "$final_risk"},
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "disease_type": "$_id.disease_type",
            "final_risk":   "$_id.final_risk",
            "count":        1
        }},
        {"$sort": {"disease_type": ASCENDING, "count": DESCENDING}}
    ]))


def pipeline_avg_confidence(db):
    return list(db["screenings"].aggregate([
        {"$group": {
            "_id":             "$disease_type",
            "avgConfidence":   {"$avg": "$confidence"},
            "totalScreenings": {"$sum": 1}
        }},
        {"$project": {
            "_id":             0,
            "disease_type":    "$_id",
            "avgConfidence":   {"$round": ["$avgConfidence", 2]},
            "totalScreenings": 1
        }},
        {"$sort": {"disease_type": ASCENDING}}
    ]))


def pipeline_daily_trend(db):
    return list(db["screenings"].aggregate([
        {"$group": {
            "_id": {
                "year":         {"$year": "$timestamp"},
                "month":        {"$month": "$timestamp"},
                "day":          {"$dayOfMonth": "$timestamp"},
                "disease_type": "$disease_type"
            },
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "year":         "$_id.year",
            "month":        "$_id.month",
            "day":          "$_id.day",
            "disease_type": "$_id.disease_type",
            "count":        1
        }},
        {"$sort": {"year": ASCENDING, "month": ASCENDING, "day": ASCENDING}}
    ]))


def pipeline_model_leaderboard(db):
    return list(db["model_performance"].aggregate([
        {"$lookup": {
            "from":         "screenings",
            "localField":   "disease_type",
            "foreignField": "disease_type",
            "as":           "relatedScreenings"
        }},
        {"$project": {
            "_id":            0,
            "model_name":     1,
            "disease_type":   1,
            "accuracy":       1,
            "f1_score":       1,
            "screeningCount": {"$size": "$relatedScreenings"}
        }},
        {"$sort": {"disease_type": ASCENDING, "accuracy": DESCENDING}}
    ]))


def pipeline_confidence_buckets(db):
    return list(db["screenings"].aggregate([
        {"$bucket": {
            "groupBy":    "$confidence",
            "boundaries": [0, 40, 60, 80, 100],
            "default":    "Out of Range",
            "output": {
                "count":         {"$sum": 1},
                "diseases":      {"$addToSet": "$disease_type"},
                "highRiskCount": {
                    "$sum": {"$cond": [{"$eq": ["$final_risk", "High Risk"]}, 1, 0]}
                }
            }
        }},
        {"$project": {
            "confidenceRange": {"$switch": {
                "branches": [
                    {"case": {"$eq": ["$_id", 0]},  "then": "0–40% (Low)"},
                    {"case": {"$eq": ["$_id", 40]}, "then": "40–60% (Moderate)"},
                    {"case": {"$eq": ["$_id", 60]}, "then": "60–80% (High)"},
                    {"case": {"$eq": ["$_id", 80]}, "then": "80–100% (Very High)"},
                ],
                "default": "Out of Range"
            }},
            "count": 1, "highRiskCount": 1, "diseases": 1, "_id": 0
        }}
    ]))


def pipeline_symptom_search(db, query):
    return list(db["screenings"].find(
        {"$text": {"$search": query}},
        {
            "score":         {"$meta": "textScore"},
            "disease_type":  1,
            "final_risk":    1,
            "confidence":    1,
            "symptom_notes": 1,
            "timestamp":     1,
            "_id":           0
        }
    ).sort([("score", {"$meta": "textScore"})]).limit(20))


# ─────────────────────────────────────────────────────────────
# SQLite-based charts (fallback)
# ─────────────────────────────────────────────────────────────

def sqlite_risk_distribution(history):
    rows = []
    for r in history:
        rows.append({"disease_type": r["Disease"], "final_risk": r["Risk"]})
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    return df.groupby(["disease_type", "final_risk"]).size().reset_index(name="count")


def sqlite_confidence_buckets(history):
    if not history:
        return pd.DataFrame()
    df = pd.DataFrame(history)
    df["conf"] = pd.to_numeric(df["Confidence (%)"], errors="coerce")
    bins   = [0, 40, 60, 80, 101]
    labels = ["0–40% (Low)", "40–60% (Moderate)", "60–80% (High)", "80–100% (Very High)"]
    df["bucket"] = pd.cut(df["conf"], bins=bins, labels=labels, right=False)
    out = df.groupby("bucket", observed=True).agg(
        count=("conf", "size"),
        highRiskCount=("Risk", lambda x: (x == "High Risk").sum())
    ).reset_index().rename(columns={"bucket": "confidenceRange"})
    return out


def sqlite_daily_trend(history):
    if not history:
        return pd.DataFrame()
    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["Timestamp"], errors="coerce").dt.date
    return df.groupby(["date", "Disease"]).size().reset_index(name="count")


# ─────────────────────────────────────────────────────────────
# Chart helpers
# ─────────────────────────────────────────────────────────────

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(19,29,50,0.6)",
    font=dict(color="#E2EAF4", family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#E2EAF4")),
    margin=dict(t=40, b=30, l=20, r=20),
)


def show():
    st.markdown("<h1>📈 Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.caption("Population-level insights from screening history")

    # Try MongoDB first; fall back to SQLite
    db        = get_db()
    use_mongo = db is not None

    if use_mongo:
        try:
            db.command("ping")
        except Exception:
            use_mongo = False
            db = None

    if use_mongo:
        st.success("✅ Connected to MongoDB", icon="🍃")
    else:
        st.info("📋 Using local SQLite history (MongoDB not connected)", icon="💾")

    # ── Summary Metrics ───────────────────────────────────────────────────────
    history = load_history_sqlite()
    df_all  = pd.DataFrame(history) if history else pd.DataFrame()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Screenings", len(df_all))
    m2.metric("High Risk",   len(df_all[df_all["Risk"] == "High Risk"]) if not df_all.empty else 0)
    m3.metric("Medium Risk", len(df_all[df_all["Risk"] == "Medium Risk"]) if not df_all.empty else 0)
    m4.metric("Low Risk",    len(df_all[df_all["Risk"] == "Low Risk"]) if not df_all.empty else 0)

    if df_all.empty:
        st.markdown("""
        <div style='background:#131D32;border:1px solid #1E3050;border-radius:14px;
                    padding:2rem;text-align:center;margin-top:2rem'>
          <div style='font-size:2rem;margin-bottom:0.6rem'>📊</div>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#E2EAF4;margin-bottom:0.4rem'>
            No Data Yet
          </div>
          <div style='color:#7A94B4;font-size:0.9rem'>
            Run predictions in the Heart Disease or Diabetes tabs to populate analytics.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.divider()

    # ── Pipeline 1 / SQLite: Risk Distribution ────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("##### Risk Distribution by Disease")
        if use_mongo:
            dist = pipeline_risk_distribution(db)
            df_dist = pd.DataFrame(dist) if dist else pd.DataFrame()
        else:
            df_dist = sqlite_risk_distribution(history)

        if not df_dist.empty:
            risk_colors = {"High Risk": "#EF4444", "Medium Risk": "#F59E0B", "Low Risk": "#10B981"}
            fig = go.Figure()
            for risk in df_dist["final_risk"].unique():
                sub = df_dist[df_dist["final_risk"] == risk]
                fig.add_trace(go.Bar(
                    name=risk, x=sub["disease_type"].str.capitalize(),
                    y=sub["count"], marker_color=risk_colors.get(risk, "#999"),
                ))
            fig.update_layout(**CHART_LAYOUT, barmode="group", height=320,
                              yaxis=dict(gridcolor="#1E3050"),
                              xaxis=dict(gridcolor="#1E3050"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data yet.")

    # ── Pipeline 5 / SQLite: Confidence Buckets ───────────────────────────────
    with col_b:
        st.markdown("##### Confidence Score Distribution")
        if use_mongo:
            buckets = pipeline_confidence_buckets(db)
            df_b = pd.DataFrame(buckets) if buckets else pd.DataFrame()
        else:
            df_b = sqlite_confidence_buckets(history)

        if not df_b.empty:
            bucket_colors = ["#7BB8E8","#4A90D9","#2E6DA4","#1B3A6B"]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=df_b["confidenceRange"], y=df_b["count"],
                name="Total", marker_color=bucket_colors[:len(df_b)]
            ))
            fig2.add_trace(go.Bar(
                x=df_b["confidenceRange"], y=df_b["highRiskCount"],
                name="High Risk", marker_color="#EF4444", opacity=0.7
            ))
            fig2.update_layout(**CHART_LAYOUT, barmode="overlay", height=320,
                               yaxis=dict(gridcolor="#1E3050"),
                               xaxis=dict(tickangle=-20))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data yet.")

    st.divider()

    # ── Pipeline 3 / SQLite: Daily Trend ─────────────────────────────────────
    st.markdown("##### Daily Screening Volume Trend")
    if use_mongo:
        trend = pipeline_daily_trend(db)
        if trend:
            df_t = pd.DataFrame(trend)
            df_t["date"] = pd.to_datetime(df_t[["year","month","day"]])
        else:
            df_t = pd.DataFrame()
    else:
        df_t = sqlite_daily_trend(history)
        if not df_t.empty:
            df_t = df_t.rename(columns={"Disease":"disease_type","date":"date"})
            df_t["date"] = pd.to_datetime(df_t["date"])

    if not df_t.empty:
        fig3 = go.Figure()
        colors = ["#0EA5E9","#EF4444","#10B981","#F59E0B"]
        for i, dt in enumerate(df_t["disease_type"].unique()):
            sub = df_t[df_t["disease_type"] == dt].sort_values("date")
            fig3.add_trace(go.Scatter(
                x=sub["date"], y=sub["count"],
                mode="lines+markers", name=str(dt).capitalize(),
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=6)
            ))
        fig3.update_layout(**CHART_LAYOUT, height=280,
                           xaxis=dict(gridcolor="#1E3050"),
                           yaxis=dict(gridcolor="#1E3050", dtick=1))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No time-series data yet.")

    st.divider()

    # ── Pipeline 4: Model Leaderboard (MongoDB only) ──────────────────────────
    if use_mongo:
        st.markdown("##### Model Performance Leaderboard")
        leaderboard = pipeline_model_leaderboard(db)
        if leaderboard:
            df_l = pd.DataFrame(leaderboard)
            st.dataframe(
                df_l[["disease_type","model_name","accuracy","f1_score","screeningCount"]
                ].sort_values(["disease_type","accuracy"], ascending=[True, False]),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("model_performance collection is empty.")
        st.divider()

    # ── Pipeline 6: Symptom Full-Text Search (MongoDB only) ───────────────────
    if use_mongo:
        st.markdown("##### Symptom Keyword Search")
        st.caption("Full-text search across symptom_notes (requires text index on MongoDB)")
        query = st.text_input("Enter symptom keyword (e.g. chest pain, fatigue, thirst)")
        if query:
            try:
                results = pipeline_symptom_search(db, query)
                if results:
                    df_s = pd.DataFrame(results)
                    df_s["score"] = df_s["score"].round(3)
                    st.dataframe(df_s, use_container_width=True)
                    st.caption(f"{len(results)} matching record(s) — sorted by relevance")
                else:
                    st.info("No records matched that keyword.")
            except Exception as e:
                st.warning(f"Text search error: {e}")
    else:
        # SQLite-based keyword search fallback
        st.markdown("##### Symptom Keyword Search")
        st.caption("Searching local SQLite history")
        query = st.text_input("Enter keyword to search symptom notes")
        if query and not df_all.empty:
            mask = df_all["Notes"].str.contains(query, case=False, na=False)
            results = df_all[mask]
            if not results.empty:
                st.dataframe(results, use_container_width=True)
                st.caption(f"{len(results)} matching record(s)")
            else:
                st.info("No records matched that keyword.")
