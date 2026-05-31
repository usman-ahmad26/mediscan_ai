import streamlit as st

def apply_global_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@600;700;800&display=swap');

    /* ── Reset & Base ── */
    #MainMenu, footer, header, [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    html, body, [data-testid="stAppViewContainer"] {
        background: #070D1A !important;
        color: #E2EAF4 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .block-container {
        padding: 0 2rem 2rem 2rem !important;
        max-width: 1300px !important;
    }

    /* ── Typography ── */
    h1 {
        font-family: 'Syne', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: #F0F6FF !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.2rem !important;
    }
    h2, h3 {
        font-family: 'Syne', sans-serif !important;
        color: #E2EAF4 !important;
        letter-spacing: -0.01em !important;
    }

    /* ── Navbar ── */
    .ms-nav {
        display: flex;
        align-items: center;
        padding: 0 2rem;
        height: 58px;
        background: rgba(7, 13, 26, 0.95);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        backdrop-filter: blur(12px);
        position: sticky;
        top: 0;
        z-index: 1000;
        gap: 4px;
        margin-bottom: 0;
    }
    .ms-brand {
        font-family: 'Syne', sans-serif;
        font-weight: 800;
        font-size: 16px;
        color: #38BDF8;
        margin-right: 20px;
        white-space: nowrap;
        letter-spacing: -0.02em;
    }
    .ms-nav-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
        color: #7A94B4;
        cursor: pointer;
        border: none;
        background: transparent;
        text-decoration: none;
        transition: all 0.15s ease;
        white-space: nowrap;
    }
    .ms-nav-btn:hover {
        background: rgba(255,255,255,0.06);
        color: #E2EAF4;
    }
    .ms-nav-btn.active {
        background: rgba(56,189,248,0.12);
        color: #38BDF8;
        font-weight: 600;
    }
    .ms-nav-right {
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ms-user-pill {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 5px 12px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 99px;
        font-size: 12px;
        color: #94A3B8;
    }
    .ms-user-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10B981;
    }

    /* ── Page header ── */
    .ms-page-header {
        padding: 1.8rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 1.6rem;
    }
    .ms-page-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        color: #F0F6FF;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .ms-page-caption {
        font-size: 0.85rem;
        color: #4A6580;
        margin-top: 3px;
    }

    /* ── Cards ── */
    .ms-card {
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(10,18,35,0.95));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.4rem;
        transition: all 0.2s ease;
    }
    .ms-card:hover {
        border-color: rgba(56,189,248,0.2);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.4);
    }

    /* ── Stat card ── */
    .ms-stat {
        background: rgba(15,23,42,0.8);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        text-align: center;
    }
    .ms-stat-val {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #F0F6FF;
        line-height: 1;
    }
    .ms-stat-label {
        font-size: 11px;
        color: #4A6580;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }

    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: rgba(15,23,42,0.8) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        padding: 1rem 1.2rem !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Syne', sans-serif !important;
        color: #F0F6FF !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] { color: #4A6580 !important; font-size: 11px !important; }

    /* ── Inputs ── */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    textarea {
        background: rgba(15,23,42,0.9) !important;
        color: #E2EAF4 !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        font-size: 13px !important;
        padding: 0.6rem 0.9rem !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    textarea:focus {
        border-color: rgba(56,189,248,0.4) !important;
        box-shadow: 0 0 0 3px rgba(56,189,248,0.08) !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background: rgba(15,23,42,0.9) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        color: #E2EAF4 !important;
    }
    [data-testid="stSlider"] > div > div > div {
        background: linear-gradient(90deg, #0EA5E9, #2563EB) !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg, #0EA5E9, #1D4ED8) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 4px 15px rgba(14,165,233,0.2) !important;
        transition: all 0.15s ease !important;
        letter-spacing: 0.01em !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(14,165,233,0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        box-shadow: none !important;
        color: #7A94B4 !important;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [role="tablist"] {
        background: rgba(15,23,42,0.6) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        gap: 2px !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 9px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #4A6580 !important;
        padding: 6px 16px !important;
        border: none !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: rgba(56,189,248,0.12) !important;
        color: #38BDF8 !important;
        font-weight: 600 !important;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        font-size: 13px !important;
    }

    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Chat ── */
    [data-testid="stChatMessage"] {
        background: rgba(15,23,42,0.7) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 14px !important;
        padding: 0.9rem 1.2rem !important;
    }

    /* ── Divider ── */
    hr {
        border-color: rgba(255,255,255,0.05) !important;
        margin: 1.2rem 0 !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 99px; }

    /* ── Caption ── */
    [data-testid="stCaptionContainer"] { color: #4A6580 !important; font-size: 12px !important; }

    /* ── Success/Warning/Error ── */
    .stSuccess { background: rgba(16,185,129,0.08) !important; border-color: rgba(16,185,129,0.2) !important; color: #6EE7B7 !important; }
    .stWarning { background: rgba(245,158,11,0.08) !important; border-color: rgba(245,158,11,0.2) !important; color: #FCD34D !important; }
    .stError   { background: rgba(239,68,68,0.08) !important;  border-color: rgba(239,68,68,0.2) !important;  color: #FCA5A5 !important; }
    .stInfo    { background: rgba(56,189,248,0.08) !important; border-color: rgba(56,189,248,0.2) !important; color: #7DD3FC !important; }

    /* ── Loading spinner ── */
    [data-testid="stSpinner"] { color: #38BDF8 !important; }

    /* ── Number input arrows ── */
    [data-testid="stNumberInput"] button {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 6px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    </style>
    """, unsafe_allow_html=True)

# Alias
apply_theme = apply_global_theme