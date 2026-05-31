"""pages/history.py — Prediction History & PDF Report Download"""

import streamlit as st
import pandas as pd
from db import load_history_sqlite, clear_history_sqlite
import io
import os
from auth import get_current_user
from ui.theme import apply_theme
apply_theme()


def generate_pdf_report(df: pd.DataFrame, user_name: str = "", user_age: str = "") -> bytes:
    """Generate a structured PDF health report using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=20, textColor=colors.HexColor("#0369A1"),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#475569"),
        spaceAfter=16
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#1E293B"),
        spaceBefore=12, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9, textColor=colors.HexColor("#334155"),
        leading=14
    )

    story = []

    # Header
    # Header
    story.append(Paragraph("MediScan AI", title_style))
    story.append(Paragraph("Health Screening Report — Prediction History", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1")))
    story.append(Spacer(1, 10))

    # Patient info
    if user_name:
        patient_line = f"Patient: {user_name}"
        if user_age:
            patient_line += f"   |   Age: {user_age}"
        story.append(Paragraph(patient_line, ParagraphStyle(
            "Patient", parent=styles["Normal"],
            fontSize=10, textColor=colors.HexColor("#0F172A"),
            fontName="Helvetica-Bold", spaceAfter=4
        )))
    story.append(Spacer(1, 8))

    # Summary stats
    total = len(df)
    high  = len(df[df["Risk"] == "High Risk"])
    med   = len(df[df["Risk"] == "Medium Risk"])
    low   = len(df[df["Risk"] == "Low Risk"])

    story.append(Paragraph("Summary", section_style))
    summary_data = [
        ["Total Screenings", str(total)],
        ["High Risk Results",   str(high)],
        ["Medium Risk Results", str(med)],
        ["Low Risk Results",    str(low)],
    ]
    summary_table = Table(summary_data, colWidths=[5*cm, 4*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,-1), colors.HexColor("#F8FAFC")),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [colors.HexColor("#F8FAFC"), colors.HexColor("#F1F5F9")]),
        ("TEXTCOLOR",      (0,0),(0,-1),  colors.HexColor("#475569")),
        ("TEXTCOLOR",      (1,0),(1,-1),  colors.HexColor("#0F172A")),
        ("FONTSIZE",       (0,0),(-1,-1), 9),
        ("GRID",           (0,0),(-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING",    (0,0),(-1,-1), 8),
        ("RIGHTPADDING",   (0,0),(-1,-1), 8),
        ("TOPPADDING",     (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 16))

    # Detailed history table
    story.append(Paragraph("Detailed Screening History", section_style))

    table_data = [["Disease", "Risk", "Confidence", "Age", "Sex", "Timestamp"]]
    for _, row in df.iterrows():
        table_data.append([
            str(row.get("Disease", "")),
            str(row.get("Risk", "")),
            f"{row.get('Confidence (%)', '')}%",
            str(row.get("Age", "")),
            str(row.get("Sex", "")),
            str(row.get("Timestamp", "")),
        ])

    col_widths = [3.5*cm, 3.5*cm, 3*cm, 2*cm, 2*cm, 4.5*cm]
    hist_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    hist_table.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0),  colors.HexColor("#0369A1")),
        ("TEXTCOLOR",      (0,0),(-1,0),  colors.white),
        ("FONTNAME",       (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0,0),(-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.HexColor("#F8FAFC"), colors.HexColor("#F1F5F9")]),
        ("TEXTCOLOR",      (0,1),(-1,-1), colors.HexColor("#1E293B")),
        ("GRID",           (0,0),(-1,-1), 0.4, colors.HexColor("#E2E8F0")),
        ("LEFTPADDING",    (0,0),(-1,-1), 6),
        ("RIGHTPADDING",   (0,0),(-1,-1), 6),
        ("TOPPADDING",     (0,0),(-1,-1), 4),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 4),
    ]))
    story.append(hist_table)
    story.append(Spacer(1, 20))

    # Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1")))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Disclaimer: This report is generated by MediScan AI, an educational screening tool. "
        "Results are not a medical diagnosis. Always consult a qualified healthcare professional "
        "for medical advice, diagnosis, or treatment.",
        body_style
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


def show():
    st.markdown("<h1>📋 Prediction History</h1>", unsafe_allow_html=True)
    st.caption("All past screening results stored locally")

    history = load_history_sqlite()

    if not history:
        st.markdown("""
        <div style='background:#131D32;border:1px solid #1E3050;border-radius:14px;
                    padding:2rem;text-align:center;margin-top:2rem'>
          <div style='font-size:2.5rem;margin-bottom:0.8rem'>📋</div>
          <div style='font-family:Syne,sans-serif;font-weight:700;color:#E2EAF4;margin-bottom:0.4rem'>
            No History Yet
          </div>
          <div style='color:#7A94B4;font-size:0.9rem'>
            Run a Heart Disease or Diabetes prediction to see results here.
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(history)

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Screenings", len(df))
    m2.metric("High Risk",   len(df[df["Risk"] == "High Risk"]))
    m3.metric("Medium Risk", len(df[df["Risk"] == "Medium Risk"]))
    m4.metric("Low Risk",    len(df[df["Risk"] == "Low Risk"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        disease_filter = st.selectbox("Filter by Disease", ["All", "heart", "diabetes"])
    with fc2:
        risk_filter = st.selectbox("Filter by Risk", ["All", "High Risk", "Medium Risk", "Low Risk"])
    with fc3:
        sort_col = st.selectbox("Sort by", ["Timestamp", "Confidence (%)"])

    filtered = df.copy()
    if disease_filter != "All":
        filtered = filtered[filtered["Disease"] == disease_filter]
    if risk_filter != "All":
        filtered = filtered[filtered["Risk"] == risk_filter]
    filtered = filtered.sort_values(sort_col, ascending=False)

    def highlight_risk(val):
        c = {"High Risk": "color: #EF4444", "Medium Risk": "color: #F59E0B", "Low Risk": "color: #10B981"}
        return c.get(val, "")

    st.dataframe(
        filtered.style.map(highlight_risk, subset=["Risk"]),
        use_container_width=True, hide_index=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    col_dl, col_cl = st.columns([2, 1])

    with col_dl:
        try:
            user = get_current_user()
            user_name = user.get("name", "")
            user_age = ""
            pdf_bytes = generate_pdf_report(filtered, user_name, user_age)
            st.download_button(
                label="📥 Download PDF Health Report",
                data=pdf_bytes,
                file_name="mediscan_ai_report.pdf",
                mime="application/pdf",
                type="primary"
            )
        except ImportError:
            st.warning("ReportLab not installed. Run `pip install reportlab` to enable PDF export.")
        except Exception as e:
            st.warning(f"PDF generation error: {e}")

    with col_cl:
        if st.button("🗑️ Clear All History", type="secondary"):
            clear_history_sqlite()
            st.success("History cleared.")
            st.rerun()
