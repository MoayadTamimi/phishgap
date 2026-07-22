# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

NEW_FIELDNAMES = [
    "student_id", "timestamp", "student_name", "student_email", "student_major", "student_year",
    "score_AW", "score_DB", "score_SV",
    "risk_AW", "risk_DB", "risk_SV",
    "actual_risk_AW", "actual_risk_DB", "actual_risk_SV",
    "gap_AW", "gap_DB", "gap_SV",
    "gap_type_AW", "gap_type_DB", "gap_type_SV",
    "sim1_score", "sim2_score", "improvement",
    "errors", "response_times",
    "gpt_recommendation", "satisfaction_avg", "open_feedback",
]
# Older rows were written before student_email/student_major/student_year/open_feedback existed.
OLD_FIELDNAMES = [f for f in NEW_FIELDNAMES if f not in ("student_email", "student_major", "student_year", "open_feedback")]
_NUMERIC_COLS = [
    "score_AW", "score_DB", "score_SV",
    "risk_AW", "risk_DB", "risk_SV",
    "actual_risk_AW", "actual_risk_DB", "actual_risk_SV",
    "gap_AW", "gap_DB", "gap_SV",
    "sim1_score", "sim2_score", "improvement", "satisfaction_avg",
]


def load_results(path: Path) -> pd.DataFrame:
    """Read results.csv tolerating rows written under the old (25-field) schema
    mixed with rows written under the current (29-field) schema."""
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    if len(rows) <= 1:
        return pd.DataFrame(columns=NEW_FIELDNAMES)

    normalized = []
    for r in rows[1:]:
        if not r:
            continue
        if len(r) == len(NEW_FIELDNAMES):
            normalized.append(r)
        elif len(r) == len(OLD_FIELDNAMES):
            normalized.append(r[:3] + ["", "", ""] + r[3:] + [""])
        else:
            padded = (r + [""] * len(NEW_FIELDNAMES))[: len(NEW_FIELDNAMES)]
            normalized.append(padded)

    out = pd.DataFrame(normalized, columns=NEW_FIELDNAMES)
    for col in _NUMERIC_COLS:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def normalize_year(val):
    val = str(val).strip()
    mapping = {
        # Preparatory
        "Preparatory Year": "Preparatory Year",
        "שנת מכינה": "Preparatory Year",
        "سنة تحضيرية": "Preparatory Year",
        # 1st Year
        "1st Year": "1st Year",
        "שנה ראשונה": "1st Year",
        "سنة أولى": "1st Year",
        # 2nd Year
        "2nd Year": "2nd Year",
        "שנה שנייה": "2nd Year",
        "سنة ثانية": "2nd Year",
        # 3rd Year
        "3rd Year": "3rd Year",
        "שנה שלישית": "3rd Year",
        "سنة ثالثة": "3rd Year",
        # 4th Year and above
        "4th Year and above": "4th Year+",
        "4th Year": "4th Year+",
        "שנה רביעית ומעלה": "4th Year+",
        "سنة رابعة فما فوق": "4th Year+",
        # Graduate
        "Graduate Studies": "Graduate Studies",
        "לימודי תואר שני": "Graduate Studies",
        "دراسات عليا": "Graduate Studies",
    }
    return mapping.get(val, val)


def normalize_major(val):
    val = str(val).strip()
    mapping = {
        # Engineering
        "Engineering (Electrical, Mechanical, Civil, Chemical, Materials)": "Engineering",
        "הנדסה (חשמל, מכונות, אזרחית, כימית, חומרים)": "Engineering",
        "الهندسة (كهرباء، ميكانيكا، مدنية، كيميائية، مواد)": "Engineering",
        # Software & CS
        "Software Engineering": "Software & CS",
        "Software & Computer Science": "Software & CS",
        "תוכנה ומדעי המחשב": "Software & CS",
        "البرمجيات وعلوم الحاسوب": "Software & CS",
        # Industrial Engineering
        "Industrial Engineering": "Industrial Eng.",
        "Industrial Engineering, Management or Economics": "Industrial Eng.",
        "תעשייה וניהול או כלכלה": "Industrial Eng.",
        "إدارة والصناعة أو اقتصاد": "Industrial Eng.",
        # Social Sciences
        "Social Sciences & Humanities": "Social Sciences",
        "מדעי החברה והרוח": "Social Sciences",
        "علوم اجتماعية وإنسانية": "Social Sciences",
        # Medicine
        "Medicine & Health Professions": "Medicine",
        "רפואה ומקצועות הבריאות": "Medicine",
        "طب ومهن صحية": "Medicine",
        # Education
        "Education & Teaching": "Education",
        "חינוך והוראה": "Education",
        "تربية وتعليم": "Education",
        # Exact Sciences
        "Exact Sciences": "Exact Sciences",
        "מדעים מדויקים": "Exact Sciences",
        "العلوم الدقيقة": "Exact Sciences",
        # Other
        "Other": "Other",
        "תחום אחר": "Other",
        "تخصص آخر": "Other",
    }
    return mapping.get(val, val)


YEAR_ORDER = ["Preparatory Year", "1st Year", "2nd Year", "3rd Year", "4th Year+", "Graduate Studies"]

_logo_path = Path(__file__).resolve().parent.parent / "logo.png"
st.set_page_config(
    page_title="PhishGap Dashboard",
    page_icon=str(_logo_path) if _logo_path.exists() else "📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    .stApp { background-color: #f8fafc; }
    </style>
    """,
    unsafe_allow_html=True,
)

BLUE = "#0ea5e9"
PURPLE = "#805ad5"
TEAL = "#38b2ac"

DIM_LABELS = {
    "AW": "Security Awareness Deficit",
    "DB": "Risky Digital Behavior",
    "SV": "Emotional & Situational Vulnerability",
}

GAP_COLORS = {
    "large": "#ef4444",
    "medium": "#f59e0b",
    "aligned": "#22c55e",
    "better": "#3b82f6",
    "much_better": "#8b5cf6",
}

px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = [BLUE, PURPLE, TEAL]

password = st.text_input("Enter admin password:", type="password")
if password != "PhishGap2026":
    st.info("Enter password to access the dashboard.")
    st.stop()

csv_path = Path(__file__).resolve().parent.parent / "results.csv"
try:
    df = load_results(csv_path)
except FileNotFoundError:
    st.info("No data collected yet. Statistics will appear after the first participant completes the assessment.")
    st.stop()

if df.empty:
    st.info("No data collected yet. Statistics will appear after the first participant completes the assessment.")
    st.stop()

if "student_year" in df.columns:
    df["student_year"] = df["student_year"].apply(normalize_year)
if "student_major" in df.columns:
    df["student_major"] = df["student_major"].apply(normalize_major)

st.title("📊 PhishGap Research Dashboard")
st.caption("Aggregated results • Password protection is for demo purposes only")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Participants", len(df))
with col2:
    if "sim1_score" in df.columns:
        st.metric("Avg Sim 1", f"{df['sim1_score'].mean():.2f} / 6")
    else:
        st.metric("Avg Sim 1", "N/A")
with col3:
    if "sim2_score" in df.columns:
        st.metric("Avg Sim 2", f"{df['sim2_score'].mean():.2f} / 6")
    else:
        st.metric("Avg Sim 2", "N/A")
with col4:
    if "sim1_score" in df.columns and "sim2_score" in df.columns:
        avg1 = df["sim1_score"].mean()
        avg2 = df["sim2_score"].mean()
        improvement_pct = (avg2 - avg1) / max(avg1, 0.01) * 100
        st.metric("Avg Improvement %", f"{improvement_pct:+.1f}%")
    else:
        st.metric("Avg Improvement %", "N/A")

st.divider()

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    with st.container(border=True):
        st.subheader("Score Distribution (Sim 1 vs Sim 2)")
        try:
            if "sim1_score" not in df.columns or "sim2_score" not in df.columns:
                st.caption("Not enough data.")
            elif len(df) < 2:
                st.caption("Not enough data.")
            else:
                melted = pd.melt(
                    df[["sim1_score", "sim2_score"]],
                    var_name="Simulation",
                    value_name="Score",
                )
                melted["Simulation"] = melted["Simulation"].map(
                    {"sim1_score": "Simulation 1", "sim2_score": "Simulation 2"}
                )
                fig = px.histogram(
                    melted,
                    x="Score",
                    color="Simulation",
                    barmode="group",
                    template="plotly_white",
                    color_discrete_map={"Simulation 1": BLUE, "Simulation 2": PURPLE},
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Not enough data.")

with row1_col2:
    with st.container(border=True):
        st.subheader("Error Rate by Dimension")
        try:
            risk_cols = ["actual_risk_AW", "actual_risk_DB", "actual_risk_SV"]
            if not all(c in df.columns for c in risk_cols):
                st.caption("Not enough data.")
            else:
                avg_risk = {
                    DIM_LABELS[dim]: df[f"actual_risk_{dim}"].mean()
                    for dim in ("AW", "DB", "SV")
                }
                chart_df = pd.DataFrame(
                    {"Dimension": list(avg_risk.keys()), "Avg Actual Risk": list(avg_risk.values())}
                )
                fig = px.bar(
                    chart_df,
                    x="Avg Actual Risk",
                    y="Dimension",
                    orientation="h",
                    template="plotly_white",
                    color_discrete_sequence=[BLUE],
                )
                st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Not enough data.")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    with st.container(border=True):
        st.subheader("Gap Type Distribution")
        try:
            gap_cols = [c for c in ("gap_type_AW", "gap_type_DB", "gap_type_SV") if c in df.columns]
            if not gap_cols:
                st.caption("Not enough data.")
            else:
                combined = pd.concat([df[c] for c in gap_cols]).dropna()
                if combined.empty:
                    st.caption("Not enough data.")
                else:
                    counts = combined.value_counts().reset_index()
                    counts.columns = ["Gap Type", "Count"]
                    fig = px.pie(
                        counts,
                        names="Gap Type",
                        values="Count",
                        hole=0.45,
                        template="plotly_white",
                        color="Gap Type",
                        color_discrete_map=GAP_COLORS,
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Not enough data.")

with row2_col2:
    with st.container(border=True):
        st.subheader("Avg Score by Major")
        try:
            if "student_major" not in df.columns or "sim1_score" not in df.columns or "sim2_score" not in df.columns:
                st.caption("Not enough data.")
            else:
                major_df = df[df["student_major"].astype(str).str.strip() != ""]
                by_major = major_df.groupby("student_major")[["sim1_score", "sim2_score"]].mean().reset_index()
                if by_major.empty:
                    st.caption("Not enough data.")
                else:
                    melted = pd.melt(
                        by_major,
                        id_vars="student_major",
                        value_vars=["sim1_score", "sim2_score"],
                        var_name="Simulation",
                        value_name="Avg Score",
                    )
                    melted["Simulation"] = melted["Simulation"].map(
                        {"sim1_score": "Simulation 1", "sim2_score": "Simulation 2"}
                    )
                    fig = px.bar(
                        melted,
                        x="student_major",
                        y="Avg Score",
                        color="Simulation",
                        barmode="group",
                        template="plotly_white",
                        color_discrete_map={"Simulation 1": BLUE, "Simulation 2": PURPLE},
                        labels={"student_major": "Major"},
                    )
                    st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Not enough data.")

st.divider()

try:
    risk_cols = ["actual_risk_AW", "actual_risk_DB", "actual_risk_SV"]
    if not all(c in df.columns for c in risk_cols) or "satisfaction_avg" not in df.columns:
        raise KeyError("missing required columns")

    weakest_dim_raw = df[risk_cols].mean()
    weakest_key = weakest_dim_raw.idxmax()
    dim_names = {
        "actual_risk_AW": f"🔍 {DIM_LABELS['AW']}",
        "actual_risk_DB": f"💻 {DIM_LABELS['DB']}",
        "actual_risk_SV": f"⚡ {DIM_LABELS['SV']}",
    }
    weakest_name = dim_names.get(weakest_key, weakest_key)
    weakest_pct = f"{weakest_dim_raw[weakest_key] * 100:.0f}%"

    avg_sat = df["satisfaction_avg"].mean()
    sat_stars = "⭐" * round(avg_sat) if pd.notna(avg_sat) else ""

    gap_cols = [c for c in ("gap_type_AW", "gap_type_DB", "gap_type_SV") if c in df.columns]
    gap_all = pd.concat([df[c] for c in gap_cols]) if gap_cols else pd.Series(dtype=object)
    gap_all = gap_all[gap_all.astype(str).str.strip() != ""].dropna()
    most_common_gap = gap_all.mode()[0] if len(gap_all) > 0 else "N/A"
    gap_labels = {
        "large": ("🔴 Large Gap", "#ef4444", "Overconfidence detected"),
        "medium": ("🟡 Medium Gap", "#f59e0b", "Slight overconfidence"),
        "aligned": ("🟢 Aligned", "#22c55e", "Self-assessment accurate"),
        "better": ("🔵 Better Than Expected", "#3b82f6", "Underestimated skills"),
        "much_better": ("🟣 Much Better", "#8b5cf6", "Greatly underestimated"),
    }
    gap_display, gap_color, gap_desc = gap_labels.get(most_common_gap, (most_common_gap, "#64748b", ""))

    stats_html = (
        '<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin: 24px 0;">'
        '<div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; '
        'border-top: 4px solid #ef4444; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">'
        '<div style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; '
        'letter-spacing: 1px; margin-bottom: 12px;">⚠️ Weakest Dimension</div>'
        f'<div style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{weakest_name}</div>'
        f'<div style="font-size: 13px; color: #ef4444; font-weight: 600;">Average error rate: {weakest_pct}</div>'
        '<div style="margin-top: 10px; height: 4px; background: #f1f5f9; border-radius: 2px;">'
        f'<div style="height: 4px; background: #ef4444; border-radius: 2px; width: {weakest_pct};"></div>'
        '</div></div>'
        '<div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; '
        'border-top: 4px solid #0ea5e9; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">'
        '<div style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; '
        'letter-spacing: 1px; margin-bottom: 12px;">😊 Avg Satisfaction</div>'
        f'<div style="font-size: 36px; font-weight: 800; color: #0ea5e9; margin-bottom: 6px;">{avg_sat:.2f}'
        '<span style="font-size: 16px; color: #94a3b8; font-weight: 400;">/ 5</span></div>'
        f'<div style="font-size: 18px; letter-spacing: 2px; margin-bottom: 4px;">{sat_stars}</div>'
        '<div style="margin-top: 10px; height: 4px; background: #f1f5f9; border-radius: 2px;">'
        f'<div style="height: 4px; background: #0ea5e9; border-radius: 2px; width: {avg_sat / 5 * 100:.0f}%;"></div>'
        '</div></div>'
        f'<div style="background: white; border-radius: 12px; padding: 24px; border: 1px solid #e2e8f0; '
        f'border-top: 4px solid {gap_color}; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">'
        '<div style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; '
        'letter-spacing: 1px; margin-bottom: 12px;">📊 Most Common Gap</div>'
        f'<div style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{gap_display}</div>'
        f'<div style="font-size: 13px; color: {gap_color}; font-weight: 500;">{gap_desc}</div>'
        f'<div style="margin-top: 10px; display: inline-block; padding: 4px 12px; border-radius: 20px; '
        f'background: {gap_color}20; color: {gap_color}; font-size: 12px; font-weight: 600;">Most frequent pattern</div>'
        '</div></div>'
    )
    st.markdown(stats_html, unsafe_allow_html=True)
except Exception:
    st.caption("Not enough data.")

st.divider()

with st.container(border=True):
    st.subheader("Comparison by Year")
    try:
        if "student_year" not in df.columns or "sim1_score" not in df.columns or "sim2_score" not in df.columns:
            st.caption("Not enough data.")
        else:
            year_df = df[df["student_year"].astype(str).str.strip() != ""]
            if year_df.empty:
                st.caption("Not enough data.")
            else:
                by_year = year_df.groupby("student_year")[["sim1_score", "sim2_score"]].mean().reset_index()
                melted = pd.melt(
                    by_year,
                    id_vars="student_year",
                    value_vars=["sim1_score", "sim2_score"],
                    var_name="Simulation",
                    value_name="Avg Score",
                )
                melted["Simulation"] = melted["Simulation"].map(
                    {"sim1_score": "Simulation 1", "sim2_score": "Simulation 2"}
                )
                fig = px.bar(
                    melted,
                    x="student_year",
                    y="Avg Score",
                    color="Simulation",
                    barmode="group",
                    template="plotly_white",
                    color_discrete_map={"Simulation 1": BLUE, "Simulation 2": PURPLE},
                    category_orders={"student_year": YEAR_ORDER},
                    labels={"student_year": "Year"},
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.caption("Not enough data.")

st.divider()

st.subheader("Raw Data")
hidden_cols = ["gpt_recommendation", "errors", "response_times"]
st.dataframe(df.drop(columns=hidden_cols, errors="ignore"), use_container_width=True)

st.download_button(
    "Download Full CSV",
    df.to_csv(index=False),
    "phishgap_results.csv",
    "text/csv",
)
