"""pages/compare.py — Model Comparison Dashboard"""

import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ui.theme import apply_theme
apply_theme()

MODELS_DIR = "models"

MODEL_DESCRIPTIONS = {
    "Random Forest": (
        "Builds 100 decision trees and averages their predictions. "
        "Highly resistant to overfitting due to bagging and feature randomisation. "
        "Typically achieves the best overall performance on tabular medical data."
    ),
    "SVM": (
        "Uses a Linear Support Vector Machine wrapped in CalibratedClassifierCV. "
        "Finds the optimal hyperplane separating diseased and healthy patients. "
        "LinearSVC scales efficiently to large datasets like BRFSS."
    ),
    "Decision Tree": (
        "Learns a tree of if/else rules from clinical features. "
        "Highly interpretable — each path from root to leaf is a human-readable rule. "
        "Max depth constrained to 8 to prevent overfitting."
    ),
    "Naive Bayes": (
        "Uses Bayes theorem to calculate the probability of disease given each indicator. "
        "Assumes feature independence. Fast training and inference. "
        "Surprisingly effective on small medical datasets."
    ),
}


def load_metrics(disease: str):
    path = os.path.join(MODELS_DIR, f"{disease}_metrics.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def make_bar(data, x_col, y_col, title, color):
    fig = px.bar(
        data, x=x_col, y=y_col, text=y_col,
        color_discrete_sequence=[color],
        title=title
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                      marker_line_width=0)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(19,29,50,0.6)",
        font=dict(color="#E2EAF4", family="DM Sans"),
        title_font=dict(family="Syne", size=14, color="#E2EAF4"),
        yaxis=dict(gridcolor="#1E3050", range=[0, 110]),
        xaxis=dict(gridcolor="#1E3050"),
        showlegend=False, margin=dict(t=50, b=10, l=10, r=10), height=320,
    )
    return fig


def make_radar(metrics_list, title):
    categories = ["Accuracy", "F1 Score", "Precision", "Recall", "CV F1"]
    fig = go.Figure()
    colors_hex = ["#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]
    colors_rgba = [
        "rgba(14,165,233,0.13)",
        "rgba(16,185,129,0.13)",
        "rgba(245,158,11,0.13)",
        "rgba(239,68,68,0.13)",
    ]
    for i, m in enumerate(metrics_list):
        vals = [
            m.get("accuracy", 0), m.get("f1_score", 0),
            m.get("precision", 0), m.get("recall", 0), m.get("cv_f1_mean", 0)
        ]
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=colors_rgba[i],
            line=dict(color=colors_hex[i], width=2),
            name=m["model_name"]
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(19,29,50,0.8)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1E3050",
                            tickfont=dict(color="#7A94B4", size=9)),
            angularaxis=dict(gridcolor="#1E3050", tickfont=dict(color="#CBD5E1", size=11))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#E2EAF4"), bgcolor="rgba(0,0,0,0)"),
        title=dict(text=title, font=dict(family="Syne", size=14, color="#E2EAF4")),
        margin=dict(t=60, b=20, l=20, r=20), height=380,
    )
    return fig


def make_cv_chart(metrics, colors):
    fig = go.Figure()
    for i, m in enumerate(metrics):
        fig.add_trace(go.Bar(
            name=m["model_name"],
            x=[m["model_name"]],
            y=[m["cv_f1_mean"]],
            error_y=dict(
                type="data",
                array=[m["cv_f1_std"]],
                visible=True,
                color="rgba(255,255,255,0.4)"
            ),
            marker_color=colors[i]
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(19,29,50,0.6)",
        font=dict(color="#E2EAF4"), yaxis=dict(gridcolor="#1E3050", range=[0, 110]),
        xaxis=dict(gridcolor="#1E3050"), showlegend=False,
        margin=dict(t=20, b=10, l=10, r=10), height=280
    )
    return fig


def show():
    st.markdown("<h1>📊 Model Comparison Dashboard</h1>", unsafe_allow_html=True)
    st.caption("Performance comparison of all four classifiers across both disease modules")

    heart_metrics    = load_metrics("heart")
    diabetes_metrics = load_metrics("diabetes")

    if not heart_metrics and not diabetes_metrics:
        st.error("No model metrics found. Run `python predict.py` to train all models first.")
        st.info("```\npython predict.py --heart data/heart.csv --diabetes data/diabetes.csv\n```")
        return

    tab1, tab2, tab3 = st.tabs(["❤️ Heart Disease", "🩸 Diabetes", "📖 Model Info"])

    colors = ["#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]

    # ── Heart ─────────────────────────────────────────────────────────────────
    with tab1:
        if not heart_metrics:
            st.info("Heart model not trained yet.")
        else:
            df = pd.DataFrame(heart_metrics)
            best = df.loc[df["f1_score"].idxmax()]

            st.markdown(f"""
            <div style='background:#052e16;border:1px solid #10B98140;border-radius:12px;
                        padding:1rem 1.4rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem'>
              <span style='font-size:1.5rem'>🏆</span>
              <div>
                <span style='font-family:Syne,sans-serif;font-weight:700;color:#10B981;font-size:1rem'>
                  Best Model: {best['model_name']}
                </span>
                <span style='color:#7A94B4;font-size:0.85rem;margin-left:1rem'>
                  Accuracy: {best['accuracy']}% &nbsp;|&nbsp; F1: {best['f1_score']}%
                  &nbsp;|&nbsp; AUC: {best.get('roc_auc', 'N/A')}%
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(
                    make_bar(df, "model_name", "accuracy", "Accuracy (%)", "#0EA5E9"),
                    use_container_width=True
                )
            with c2:
                st.plotly_chart(
                    make_bar(df, "model_name", "f1_score", "F1 Score (%)", "#10B981"),
                    use_container_width=True
                )

            st.plotly_chart(
                make_radar(heart_metrics, "Heart Disease — All Models Radar"),
                use_container_width=True
            )

            st.markdown("##### Full Metrics Table")
            display_cols = ["model_name", "accuracy", "f1_score", "precision",
                            "recall", "roc_auc", "cv_f1_mean", "cv_f1_std"]
            st.dataframe(
                df[[c for c in display_cols if c in df.columns]].rename(columns={
                    "model_name": "Model", "accuracy": "Accuracy %",
                    "f1_score": "F1 %", "precision": "Precision %",
                    "recall": "Recall %", "roc_auc": "AUC %",
                    "cv_f1_mean": "CV F1 Mean %", "cv_f1_std": "CV F1 Std %"
                }),
                use_container_width=True, hide_index=True
            )

            st.markdown("##### Cross-Validation (5-Fold F1) Comparison")
            st.plotly_chart(make_cv_chart(heart_metrics, colors), use_container_width=True)

    # ── Diabetes ──────────────────────────────────────────────────────────────
    with tab2:
        if not diabetes_metrics:
            st.info("Diabetes model not trained yet.")
        else:
            df = pd.DataFrame(diabetes_metrics)
            best = df.loc[df["f1_score"].idxmax()]

            st.markdown(f"""
            <div style='background:#052e16;border:1px solid #10B98140;border-radius:12px;
                        padding:1rem 1.4rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem'>
              <span style='font-size:1.5rem'>🏆</span>
              <div>
                <span style='font-family:Syne,sans-serif;font-weight:700;color:#10B981;font-size:1rem'>
                  Best Model: {best['model_name']}
                </span>
                <span style='color:#7A94B4;font-size:0.85rem;margin-left:1rem'>
                  Accuracy: {best['accuracy']}% &nbsp;|&nbsp; F1: {best['f1_score']}%
                  &nbsp;|&nbsp; AUC: {best.get('roc_auc', 'N/A')}%
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(
                    make_bar(df, "model_name", "accuracy", "Accuracy (%)", "#EF4444"),
                    use_container_width=True
                )
            with c2:
                st.plotly_chart(
                    make_bar(df, "model_name", "f1_score", "F1 Score (%)", "#F59E0B"),
                    use_container_width=True
                )

            st.plotly_chart(
                make_radar(diabetes_metrics, "Diabetes — All Models Radar"),
                use_container_width=True
            )

            st.markdown("##### Full Metrics Table")
            display_cols = ["model_name", "accuracy", "f1_score", "precision",
                            "recall", "roc_auc", "cv_f1_mean", "cv_f1_std"]
            st.dataframe(
                df[[c for c in display_cols if c in df.columns]].rename(columns={
                    "model_name": "Model", "accuracy": "Accuracy %",
                    "f1_score": "F1 %", "precision": "Precision %",
                    "recall": "Recall %", "roc_auc": "AUC %",
                    "cv_f1_mean": "CV F1 Mean %", "cv_f1_std": "CV F1 Std %"
                }),
                use_container_width=True, hide_index=True
            )

            st.markdown("##### Cross-Validation (5-Fold F1) Comparison")
            st.plotly_chart(make_cv_chart(diabetes_metrics, colors), use_container_width=True)

    # ── Model Info ────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("##### 🤖 Model Descriptions")
        for model_name, desc in MODEL_DESCRIPTIONS.items():
            st.markdown(f"""
            <div style='background:#131D32;border:1px solid #1E3050;border-radius:12px;
                        padding:1.1rem 1.4rem;margin-bottom:0.8rem;
                        display:flex;gap:1.2rem;align-items:flex-start'>
              <div style='min-width:130px'>
                <div style='font-family:Syne,sans-serif;font-weight:700;color:#38BDF8;
                            font-size:0.95rem'>{model_name}</div>
              </div>
              <div style='color:#7A94B4;font-size:0.85rem;line-height:1.6'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)