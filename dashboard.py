import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import io
import base64
import urllib.parse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# ══════════════════════════════════════════════
# CONFIG PAGE
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="CyberWatch — Insider Threat Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ══════════════════════════════════════════════
# CSS PROFESSIONNEL
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Syne:wght@400;600;700;800&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}
.stApp {
    background: #080c14;
    color: #c8d6e8;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1421 !important;
    border-right: 1px solid #1e2d45;
}
[data-testid="stSidebar"] * { color: #8fa8c8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] strong { color: #e0ecff !important; }

/* ── Header Banner ── */
.cyber-header {
    background: linear-gradient(135deg, #0d1f3c 0%, #091628 50%, #0a1a2e 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.cyber-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #3b82f6, #06b6d4, transparent);
}
.cyber-header::after {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.cyber-title {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #e0ecff;
    margin: 0;
    letter-spacing: -0.5px;
}
.cyber-title span { color: #3b82f6; }
.cyber-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #4a7ab5;
    margin-top: 6px;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.cyber-badge {
    display: inline-block;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3);
    color: #60a5fa;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
    margin-right: 6px;
    margin-top: 10px;
}

/* ── KPI Cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}
.kpi-card {
    background: #0d1828;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    padding: 16px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-blue::before   { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.kpi-red::before    { background: linear-gradient(90deg, #ef4444, #f97316); }
.kpi-green::before  { background: linear-gradient(90deg, #10b981, #3b82f6); }
.kpi-yellow::before { background: linear-gradient(90deg, #f59e0b, #ef4444); }
.kpi-purple::before { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
.kpi-label {
    font-size: 0.68rem;
    color: #4a7ab5;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 800;
    color: #e0ecff;
    line-height: 1;
    font-family: 'Syne', sans-serif;
}
.kpi-delta {
    font-size: 0.72rem;
    color: #4a7ab5;
    margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1a2d45;
}
.section-header-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #4a7ab5;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-family: 'JetBrains Mono', monospace;
}
.section-dot {
    width: 6px; height: 6px;
    background: #3b82f6;
    border-radius: 50%;
    box-shadow: 0 0 6px #3b82f6;
}

/* ── Verdict Badges ── */
.verdict-normal   { background: rgba(16,185,129,0.12); color: #10b981; border: 1px solid rgba(16,185,129,0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }
.verdict-low      { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }
.verdict-medium   { background: rgba(249,115,22,0.12); color: #f97316; border: 1px solid rgba(249,115,22,0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }
.verdict-high     { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3);  padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }
.verdict-critical { background: rgba(139,92,246,0.12); color: #8b5cf6; border: 1px solid rgba(139,92,246,0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-family: 'JetBrains Mono', monospace; }

/* ── Alert Box ── */
.alert-box {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.25);
    border-left: 3px solid #ef4444;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.85rem;
    color: #fca5a5;
}
.alert-box-warning {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.25);
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.85rem;
    color: #fcd34d;
}
.alert-box-success {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.25);
    border-left: 3px solid #10b981;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 0.85rem;
    color: #6ee7b7;
}

/* ── Score Bar ── */
.score-bar-container { margin: 8px 0; }
.score-bar-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.72rem;
    color: #4a7ab5;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 4px;
}
.score-bar-track {
    background: #0d1828;
    border-radius: 4px;
    height: 6px;
    border: 1px solid #1a2d45;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* ── Info Card ── */
.info-card {
    background: #0d1828;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    padding: 20px;
    height: 100%;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: #0d1421 !important;
    border-bottom: 1px solid #1a2d45 !important;
    gap: 4px;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #4a7ab5 !important;
    border: none !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
    padding: 10px 16px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #60a5fa !important;
    border-bottom: 2px solid #3b82f6 !important;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    background: #0d1828 !important;
    border: 2px dashed #1e3a5f !important;
    border-radius: 12px !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #0d1828 !important;
    border: 1px solid #1e3a5f !important;
    color: #c8d6e8 !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0d1828;
    border: 1px solid #1a2d45;
    border-radius: 10px;
    padding: 14px 18px;
}
[data-testid="stMetricLabel"] { color: #4a7ab5 !important; font-size: 0.72rem !important; }
[data-testid="stMetricValue"] { color: #e0ecff !important; }

/* ── Divider ── */
hr { border-color: #1a2d45 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1a2d45 !important; border-radius: 8px; }

/* ── Pulse animation ── */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.pulse { animation: pulse 2s infinite; }

/* ── Scan line ── */
.scan-line {
    height: 1px;
    background: linear-gradient(90deg, transparent, #3b82f6, transparent);
    animation: scan 3s linear infinite;
    margin: 2px 0;
}
@keyframes scan {
    0%   { transform: translateX(-100%); }
    100% { transform: translateX(200%); }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
PLOTLY_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8fa8c8", family="JetBrains Mono"),
    xaxis=dict(gridcolor="#1a2d45", linecolor="#1a2d45", tickcolor="#4a7ab5"),
    yaxis=dict(gridcolor="#1a2d45", linecolor="#1a2d45", tickcolor="#4a7ab5"),
    margin=dict(t=30, b=20, l=10, r=10),
)

MODEL_COLORS = {
    "score_IF": "#3b82f6", "score_AE": "#10b981",
    "score_LSTM": "#f59e0b", "score_DBSCAN": "#ef4444"
}
VERDICT_COLORS = {
    0: "#10b981", 1: "#f59e0b", 2: "#f97316", 3: "#ef4444", 4: "#8b5cf6"
}

def verdict_html(v):
    cls = {"Normal": "verdict-normal",
           "Suspect (1 modèle)": "verdict-low",
           "Suspect (2 modèles)": "verdict-medium",
           "Suspect (3 modèles)": "verdict-high",
           "Suspect (4 modèles)": "verdict-critical"}.get(v, "verdict-normal")
    return f'<span class="{cls}">{v}</span>'

def section_title(text, icon=""):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-dot"></div>
        <span class="section-header-title">{icon} {text}</span>
    </div>""", unsafe_allow_html=True)

def score_bar(label, value, threshold, color):
    pct = min(value / (threshold * 2) * 100, 100) if threshold > 0 else 0
    flagged = value > threshold
    bar_color = "#ef4444" if flagged else color
    st.markdown(f"""
    <div class="score-bar-container">
        <div class="score-bar-label">
            <span>{label}</span>
            <span style="color:{'#ef4444' if flagged else '#c8d6e8'}">{value:.4f} {'⚠' if flagged else '✓'}</span>
        </div>
        <div class="score-bar-track">
            <div class="score-bar-fill" style="width:{pct}%; background:{bar_color};"></div>
        </div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# CHARGEMENT DES DONNÉES
# ══════════════════════════════════════════════
@st.cache_data
def load_data():
    consensus = pd.read_csv("pfe_final_consensus.csv")
    scores    = pd.read_csv("pfe_scores_fenetres.csv", parse_dates=["Date"])
    with open("pfe_config.json") as f:
        config = json.load(f)
    return consensus, scores, config

@st.cache_data
def load_shap():
    import os
    if os.path.exists("shap_vals_if.npy") and os.path.exists("feature_cols.json"):
        shap_vals = np.load("shap_vals_if.npy")
        with open("feature_cols.json") as f:
            feat_cols = json.load(f)
        return shap_vals, feat_cols
    return None, None

consensus, scores, config = load_data()
shap_vals_if, shap_feature_cols = load_shap()
seuils = config["seuils"]

enc_to_label = {}
if "UserID" in consensus.columns:
    enc_to_label = dict(zip(consensus["UserID_enc"], consensus["UserID"]))
else:
    enc_to_label = {e: f"User_{e}" for e in consensus["UserID_enc"].unique()}

scores["UserLabel"] = scores["UserID_enc"].map(enc_to_label)

# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 20px 0 10px;">
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:800; color:#e0ecff;">
            🛡️ CYBER<span style="color:#3b82f6;">WATCH</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#4a7ab5; letter-spacing:2px; margin-top:4px;">
            INSIDER THREAT DETECTION
        </div>
        <div class="scan-line" style="margin-top:12px;"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace; font-size:0.65rem; color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">⚙ Seuils du pipeline</p>', unsafe_allow_html=True)

    tooltips = {
        "IF":     "q90 du train — comportement isolé de la population",
        "AE":     "q96 du train — profil difficile à reconstruire",
        "LSTM":   "q88 du train — séquence temporelle anormale sur 7j",
        "DBSCAN": "q99 du train — outlier dans l'espace de volume",
    }
    for model, val in seuils.items():
        col_a, col_b = st.columns([2, 1])
        col_a.markdown(
            f'<span style="font-family:\'JetBrains Mono\',monospace; font-size:0.75rem; color:#8fa8c8;">{model}</span>',
            unsafe_allow_html=True
        )
        col_b.markdown(
            f'<span style="font-family:\'JetBrains Mono\',monospace; font-size:0.75rem; color:#3b82f6; font-weight:600;">{val:.4f}</span>',
            unsafe_allow_html=True
        )
        st.sidebar.caption(f"↳ {tooltips.get(model, '')}")

    st.markdown("---")
    min_consensus = st.slider("Filtre consensus minimum", 0, 4, 0,
                               help="Afficher uniquement les users avec ce niveau de consensus")
    st.markdown("---")
    st.markdown(f"""
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#2d4a6e; text-align:center; padding:10px;">
        PFE 2025-2026<br>Ibtissem Tounsi<br>ENSI / Université Laval
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════
now = datetime.now().strftime("%Y-%m-%d %H:%M")
total_users    = len(consensus)
total_suspects = (consensus["consensus"] >= 1).sum()
suspects_4     = (consensus["consensus"] == 4).sum()
total_windows  = len(scores)
windows_alerted = (scores["consensus"] >= 1).sum()

st.markdown(f"""
<div class="cyber-header">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <h1 class="cyber-title">🛡️ Cyber<span>Watch</span></h1>
            <p class="cyber-subtitle">Behavioural Anomaly Detection System — v2.0</p>
            <div style="margin-top:12px;">
                <span class="cyber-badge">PIPELINE 4 MODÈLES</span>
                <span class="cyber-badge">XAI ENABLED</span>
                <span class="cyber-badge">NO DATA LEAKAGE</span>
                <span class="cyber-badge">{config['dataset']}</span>
            </div>
        </div>
        <div style="text-align:right;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4a7ab5;">LAST SCAN</div>
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.85rem; color:#60a5fa;">{now}</div>
            <div style="margin-top:8px; display:flex; gap:6px; justify-content:flex-end; align-items:center;">
                <div class="pulse" style="width:8px; height:8px; background:#10b981; border-radius:50%;"></div>
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#10b981;">SYSTÈME ACTIF</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-card kpi-blue">
        <div class="kpi-label">Utilisateurs</div>
        <div class="kpi-value">{total_users}</div>
        <div class="kpi-delta">analysés au total</div>
    </div>
    <div class="kpi-card kpi-red">
        <div class="kpi-label">Suspects ≥1</div>
        <div class="kpi-value">{total_suspects}</div>
        <div class="kpi-delta">{total_suspects/total_users*100:.0f}% de la population</div>
    </div>
    <div class="kpi-card kpi-purple">
        <div class="kpi-label">Consensus 4/4</div>
        <div class="kpi-value">{suspects_4}</div>
        <div class="kpi-delta">insiders confirmés</div>
    </div>
    <div class="kpi-card kpi-green">
        <div class="kpi-label">Fenêtres</div>
        <div class="kpi-value">{total_windows}</div>
        <div class="kpi-delta">fenêtres journalières</div>
    </div>
    <div class="kpi-card kpi-yellow">
        <div class="kpi-label">Alertes</div>
        <div class="kpi-value">{windows_alerted}</div>
        <div class="kpi-delta">{windows_alerted/total_windows*100:.1f}% taux d'alerte</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# FONCTION GÉNÉRATION PDF
# ══════════════════════════════════════════════
def generate_pdf_report(user_name, verdict, consensus, pct_alerte,
                         scores_dict, seuils_dict, feat_df, anom_type, anom_desc):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                             rightMargin=2*cm, leftMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Title'],
        fontSize=18, textColor=rl_colors.HexColor('#1e3a5f'),
        spaceAfter=6, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=9, textColor=rl_colors.HexColor('#4a7ab5'),
        spaceAfter=12, fontName='Helvetica')
    section_style = ParagraphStyle('Section', parent=styles['Normal'],
        fontSize=11, textColor=rl_colors.HexColor('#1e3a5f'),
        spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=9, textColor=rl_colors.HexColor('#2d3748'),
        spaceAfter=6, fontName='Helvetica', leading=14)

    risk_color_map = {
        "🟢 Normal": '#10b981', "🟡 Légèrement atypique": '#f59e0b',
        "🟠 Suspect (modéré)": '#f97316', "🔴 Suspect (confirmé)": '#ef4444',
        "Normal": '#10b981', "Légèrement atypique": '#f59e0b',
        "Suspect (modéré)": '#f97316', "Suspect (confirmé)": '#ef4444',
    }
    risk_hex = risk_color_map.get(verdict, '#4a7ab5')

    story = []

    # Header
    story.append(Paragraph("CyberWatch — Rapport d'Alerte", title_style))
    story.append(Paragraph(
        f"Généré le {datetime.now().strftime('%Y-%m-%d à %H:%M')} | "
        f"Pipeline : IF · AE · LSTM-AE · DBSCAN", sub_style))
    story.append(HRFlowable(width="100%", thickness=2,
                              color=rl_colors.HexColor('#1e3a5f'), spaceAfter=12))

    # Verdict
    story.append(Paragraph("VERDICT FINAL", section_style))
    verdict_data = [
        ["Utilisateur", user_name],
        ["Verdict", verdict],
        ["Consensus", f"{consensus} / 4 modèles déclenchés"],
        ["Taux d'alerte", f"{pct_alerte:.1f}%"],
        ["Type d'anomalie", anom_type],
    ]
    t = Table(verdict_data, colWidths=[4*cm, 13*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (0,-1), rl_colors.HexColor('#f0f4f8')),
        ('TEXTCOLOR',   (0,0), (0,-1), rl_colors.HexColor('#1e3a5f')),
        ('FONTNAME',    (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,0), (-1,-1),
         [rl_colors.HexColor('#f8fafc'), rl_colors.white]),
        ('GRID',        (0,0), (-1,-1), 0.5, rl_colors.HexColor('#e2e8f0')),
        ('PADDING',     (0,0), (-1,-1), 6),
        ('TEXTCOLOR',   (1,1), (1,1), rl_colors.HexColor(risk_hex)),
        ('FONTNAME',    (1,1), (1,1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    story.append(Paragraph(anom_desc, body_style))

    # Scores
    story.append(Paragraph("SCORES PAR MODÈLE", section_style))
    score_data = [["Modèle", "Score", "Seuil", "Statut"]]
    for model, score in scores_dict.items():
        seuil = seuils_dict.get(model, 0)
        statut = "FLAGGE" if score > seuil else "NORMAL"
        score_data.append([model, f"{score:.4f}", f"{seuil:.4f}", statut])

    t2 = Table(score_data, colWidths=[4*cm, 4*cm, 4*cm, 5*cm])
    t2.setStyle(TableStyle([
        ('BACKGROUND',  (0,0), (-1,0), rl_colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR',   (0,0), (-1,0), rl_colors.white),
        ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,-1), 9),
        ('ROWBACKGROUNDS', (0,1), (-1,-1),
         [rl_colors.HexColor('#f8fafc'), rl_colors.white]),
        ('GRID',        (0,0), (-1,-1), 0.5, rl_colors.HexColor('#e2e8f0')),
        ('PADDING',     (0,0), (-1,-1), 6),
        ('ALIGN',       (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(t2)

    # Features
    if feat_df is not None and len(feat_df) > 0:
        story.append(Paragraph("TOP FEATURES ANORMALES", section_style))
        feat_data = [["Feature", "Valeur", "Moyenne", "Z-score"]]
        for _, row in feat_df.iterrows():
            feat_data.append([str(row["Feature"]), str(row["Valeur"]),
                               str(row["Moyenne"]), str(row["Z-score"])])
        t3 = Table(feat_data, colWidths=[7*cm, 3*cm, 3*cm, 4*cm])
        t3.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0), rl_colors.HexColor('#1e3a5f')),
            ('TEXTCOLOR',   (0,0), (-1,0), rl_colors.white),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 8),
            ('ROWBACKGROUNDS', (0,1), (-1,-1),
             [rl_colors.HexColor('#f8fafc'), rl_colors.white]),
            ('GRID',        (0,0), (-1,-1), 0.5, rl_colors.HexColor('#e2e8f0')),
            ('PADDING',     (0,0), (-1,-1), 5),
        ]))
        story.append(t3)

    # Recommandation
    story.append(Paragraph("RECOMMANDATION", section_style))
    rec_map = {
        "🟢 Normal": "Aucune action requise. Comportement conforme au profil normal.",
        "Légèrement atypique": "Surveillance passive recommandée. Quelques jours atypiques isolés.",
        "Suspect (modéré)": "Surveillance active recommandée. Investigation à planifier sous 48h.",
        "Suspect (confirmé)": "ALERTE HAUTE PRIORITÉ — Revue manuelle immédiate requise. Escalader au responsable sécurité."
    }
    story.append(Paragraph(rec_map.get(verdict, "Analyse manuelle recommandée."), body_style))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1,
                              color=rl_colors.HexColor('#e2e8f0')))
    story.append(Paragraph(
        "CyberWatch v2.0 — Pipeline de détection d'anomalies comportementales | "
        "PFE 2025-2026 · Ibtissem Tounsi · ENSI / Université Laval",
        ParagraphStyle('Footer', parent=styles['Normal'],
                       fontSize=7, textColor=rl_colors.HexColor('#9ca3af'),
                       alignment=TA_CENTER)))

    doc.build(story)
    buffer.seek(0)
    return buffer

# ══════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📊  Vue Globale",
    "👤  Profil Utilisateur",
    "📈  Scores & Modèles",
    "🕐  Évolution Temporelle",
    "🔬  Analyser un Journal",
    "ℹ️   Critères de Détection",
    "📉  Métriques Pipeline",
    "🧪  MLflow — Expériences",
    "📡  Data Drift — Evidently",
])

# ══════════════════════════════════════════════
# TAB 1 — VUE GLOBALE
# ══════════════════════════════════════════════
with tab1:
    col_a, col_b = st.columns([1, 1])

    with col_a:
        section_title("Distribution des verdicts", "◈")
        verdict_counts = consensus["verdict"].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=verdict_counts.index,
            values=verdict_counts.values,
            hole=0.6,
            marker=dict(
                colors=["#10b981", "#f59e0b", "#f97316", "#ef4444", "#8b5cf6"],
                line=dict(color="#080c14", width=2)
            ),
            textfont=dict(family="JetBrains Mono", size=11),
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_users}</b><br><span style='font-size:10px'>users</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#e0ecff", family="Syne")
        )
        fig_donut.update_layout(**PLOTLY_THEME, height=300,
                                 legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_b:
        section_title("Consensus par utilisateur", "◈")
        consensus_counts = consensus["consensus"].value_counts().sort_index()
        fig_bar = go.Figure(go.Bar(
            x=[f"C{i}" for i in consensus_counts.index],
            y=consensus_counts.values,
            marker=dict(
                color=[VERDICT_COLORS.get(i, "#4a7ab5") for i in consensus_counts.index],
                line=dict(color="#080c14", width=1)
            ),
            text=consensus_counts.values,
            textposition="outside",
            textfont=dict(color="#c8d6e8", family="JetBrains Mono", size=11)
        ))
        fig_bar.update_layout(**PLOTLY_THEME, height=300,
                               xaxis_title="Niveau de consensus",
                               yaxis_title="Nb utilisateurs")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    section_title("Classement des utilisateurs", "◈")

    df_display = consensus[consensus["consensus"] >= min_consensus].copy()
    if "UserID" in df_display.columns:
        df_display = df_display.rename(columns={"UserID": "Utilisateur"})
    else:
        df_display["Utilisateur"] = df_display["UserID_enc"].map(enc_to_label)
    df_display = df_display.sort_values("consensus", ascending=False)

    cols_show = ["Utilisateur", "consensus", "verdict",
                 "max_score_IF", "max_score_AE", "max_score_LSTM", "max_score_DBSCAN"]
    cols_show = [c for c in cols_show if c in df_display.columns]

    def color_row(val):
        if isinstance(val, str):
            if "4 modèles" in val: return "background-color:#1a0a2e; color:#c084fc"
            if "3 modèles" in val: return "background-color:#2d0a0a; color:#f87171"
            if "2 modèles" in val: return "background-color:#2d1a0a; color:#fb923c"
            if "1 modèle"  in val: return "background-color:#2d250a; color:#fbbf24"
            if "Normal"    in val: return "background-color:#0a2d1a; color:#34d399"
        return ""

    styled = (df_display[cols_show].style
              .map(color_row, subset=["verdict"])
              .format({c: "{:.4f}" for c in ["max_score_IF","max_score_AE",
                                               "max_score_LSTM","max_score_DBSCAN"]
                       if c in cols_show})
              .set_properties(**{"font-family": "JetBrains Mono", "font-size": "12px"}))
    st.dataframe(styled, use_container_width=True, height=380)

    # Export CSV
    st.markdown("---")
    col_exp1, col_exp2 = st.columns([1, 3])
    with col_exp1:
        csv_data = df_display[cols_show].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Exporter en CSV",
            data=csv_data,
            file_name="suspects_export.csv",
            mime="text/csv",
        )

# ══════════════════════════════════════════════
# TAB 2 — PROFIL UTILISATEUR
# ══════════════════════════════════════════════
with tab2:
    user_labels_list = sorted(scores["UserLabel"].unique())
    selected_user = st.selectbox("Sélectionner un utilisateur", user_labels_list,
                                  key="user_select")

    user_data = scores[scores["UserLabel"] == selected_user].sort_values("Date")
    user_enc  = user_data["UserID_enc"].iloc[0]
    user_row  = consensus[consensus["UserID_enc"] == user_enc].iloc[0]
    v         = user_row["verdict"]
    cons      = int(user_row["consensus"])

    # Header profil
    verdict_cls = {0:"🟢 Normal", 1:"🟡 Suspect (1 modèle)", 2:"🟠 Suspect (2 modèles)",
                   3:"🔴 Suspect (3 modèles)", 4:"🟣 Suspect (4 modèles)"}.get(cons, "⚪")
    risk_color  = ["#10b981","#f59e0b","#f97316","#ef4444","#8b5cf6"][min(cons, 4)]
    risk_pct    = cons / 4 * 100

    st.markdown(f"""
    <div class="info-card" style="margin-bottom:20px; border-color:{risk_color}33;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                            color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
                    PROFIL UTILISATEUR
                </div>
                <div style="font-family:'Syne',sans-serif; font-size:1.6rem;
                            font-weight:800; color:#e0ecff; margin-top:4px;">
                    {selected_user}
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'JetBrains Mono',monospace; font-size:1rem;
                            color:{risk_color}; font-weight:600;">{verdict_cls}</div>
                <div style="font-family:'JetBrains Mono',monospace; font-size:0.7rem;
                            color:#4a7ab5; margin-top:4px;">
                    {len(user_data)} fenêtres analysées
                </div>
            </div>
        </div>
        <div style="margin-top:16px; background:#080c14; border-radius:6px;
                    height:8px; overflow:hidden; border:1px solid #1a2d45;">
            <div style="height:100%; width:{risk_pct}%; background:{risk_color};
                        border-radius:6px; transition:width 0.5s;"></div>
        </div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; margin-top:6px;">
            NIVEAU DE RISQUE : {cons}/4 modèles déclenchés
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Score bars
    col_scores, col_stats = st.columns([1, 1])
    with col_scores:
        section_title("Scores max par modèle", "◈")
        score_bar("Isolation Forest", float(user_row["max_score_IF"]),
                  seuils["IF"], "#3b82f6")
        score_bar("Autoencoder", float(user_row["max_score_AE"]),
                  seuils["AE"], "#10b981")
        score_bar("LSTM-AE", float(user_row["max_score_LSTM"]),
                  seuils["LSTM"], "#f59e0b")
        score_bar("DBSCAN", float(user_row["max_score_DBSCAN"]),
                  seuils["DBSCAN"], "#ef4444")

    with col_stats:
        section_title("Statistiques d'alerte", "◈")
        n_alertes = (user_data["consensus"] >= 1).sum()
        pct_alertes = n_alertes / len(user_data) * 100
        st.metric("Fenêtres alertées", f"{n_alertes} / {len(user_data)}")
        st.metric("Taux d'alerte", f"{pct_alertes:.1f}%")
        if cons == 0:
            st.markdown('<div class="alert-box-success">✅ Comportement normal — aucun modèle déclenché</div>',
                        unsafe_allow_html=True)
        elif cons <= 1 and pct_alertes < 10:
            st.markdown('<div class="alert-box-warning">⚠️ Quelques jours atypiques isolés — surveillance passive</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box">🚨 Comportement suspect — investigation recommandée</div>',
                        unsafe_allow_html=True)


        # Bouton alerte email
        if cons >= 2:
            st.markdown("---")
            section_title("Envoyer une alerte email", "")
            email_to = st.text_input(
                "Adresse du responsable securite",
                placeholder="responsable@organisation.com",
                key="email_to_profile"
            )
            if email_to:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                GMAIL_USER = "ibtissem99tounsi@gmail.com"
                GMAIL_PWD  = "tbri dytr vnvt dtuw"
                rec_txt = {2:"Surveillance active. Investigation sous 48h.",
                           3:"Investigation sous 24h.",
                           4:"ALERTE HAUTE PRIORITE - Revue immediate."}.get(min(cons,4),"")
                verdict_txt = {2:"Suspect modere",3:"Suspect fort",
                               4:"Insider confirme"}.get(min(cons,4),"Suspect")
                sujet = f"[ALERTE CYBERWATCH] Utilisateur suspect : {selected_user}"
                corps_txt = (
                    "Bonjour,\n\n"
                    "CyberWatch a detecte un comportement suspect.\n\n"
                    f"Utilisateur   : {selected_user}\n"
                    f"Verdict       : {verdict_txt}\n"
                    f"Consensus     : {cons}/4 modeles\n"
                    f"Taux alerte   : {pct_alertes:.1f}%\n\n"
                    "SCORES :\n"
                    f"  IF     : {user_row['max_score_IF']:.4f} (seuil {seuils['IF']:.4f})\n"
                    f"  AE     : {user_row['max_score_AE']:.4f} (seuil {seuils['AE']:.4f})\n"
                    f"  LSTM   : {user_row['max_score_LSTM']:.4f} (seuil {seuils['LSTM']:.4f})\n"
                    f"  DBSCAN : {user_row['max_score_DBSCAN']:.4f} (seuil {seuils['DBSCAN']:.4f})\n\n"
                    f"RECOMMANDATION : {rec_txt}\n\n"
                    f"--\nCyberWatch v2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    "PFE 2025-2026 - Ibtissem Tounsi - ENSI / Universite Laval"
                )
                st.markdown(
                    f'<div style="background:#0d1828;border:1px solid #1a2d45;border-radius:8px;'
                    f'padding:14px 16px;margin-bottom:12px;">'
                    f'<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
                    f'color:#4a7ab5;text-transform:uppercase;margin-bottom:8px;">APERCU EMAIL</div>'
                    f'<div style="color:#60a5fa;font-size:0.72rem;">A : {email_to}</div>'
                    f'<div style="color:#e0ecff;font-size:0.72rem;margin:4px 0;">Sujet : {sujet}</div>'
                    f'<pre style="color:#8fa8c8;font-size:0.68rem;line-height:1.5;'
                    f'white-space:pre-wrap;margin-top:8px;">{corps_txt[:300]}...</pre></div>',
                    unsafe_allow_html=True
                )
                if st.button("Envoyer alerte email", type="primary", key="send_email_btn"):
                    with st.spinner("Envoi en cours..."):
                        try:
                            msg = MIMEMultipart("alternative")
                            msg["Subject"] = sujet
                            msg["From"]    = GMAIL_USER
                            msg["To"]      = email_to
                            msg.attach(MIMEText(corps_txt, "plain", "utf-8"))
                            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                server.login(GMAIL_USER, GMAIL_PWD)
                                server.sendmail(GMAIL_USER, email_to, msg.as_string())
                            st.markdown('<div class="alert-box-success">Email envoye avec succes !</div>', unsafe_allow_html=True)
                        except Exception as mail_err:
                            st.markdown(f'<div class="alert-box">Erreur : {mail_err}</div>', unsafe_allow_html=True)
            else:
                st.caption("Entrez une adresse email pour envoyer l alerte")
    st.markdown("---")
    section_title(f"Évolution temporelle — {selected_user}", "◈")

    fig_user = make_subplots(
        rows=4, cols=1, shared_xaxes=True,
        subplot_titles=["Isolation Forest", "Autoencoder", "LSTM-AE", "DBSCAN"],
        vertical_spacing=0.05
    )
    model_cols = ["score_IF", "score_AE", "score_LSTM", "score_DBSCAN"]
    thr_keys   = ["IF", "AE", "LSTM", "DBSCAN"]

    for i, (col, tkey) in enumerate(zip(model_cols, thr_keys), 1):
        thr = seuils[tkey]
        color = list(MODEL_COLORS.values())[i-1]

        fig_user.add_trace(go.Scatter(
            x=user_data["Date"], y=user_data[col],
            mode="lines", name=col.replace("score_", ""),
            line=dict(color=color, width=1.5),
            fill="tozeroy", fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[j:j+2], 16) for j in (0,2,4)) + [0.06])}",
        ), row=i, col=1)

        # Seuil
        fig_user.add_hline(y=thr, line_dash="dot", line_color=color,
                            line_width=1, opacity=0.5, row=i, col=1)

        # Alertes
        alerts = user_data[user_data[col] > thr]
        if len(alerts) > 0:
            fig_user.add_trace(go.Scatter(
                x=alerts["Date"], y=alerts[col], mode="markers",
                marker=dict(color="#ef4444", size=7, symbol="x",
                            line=dict(color="#ef4444", width=2)),
                showlegend=False
            ), row=i, col=1)

    # Overlay profil moyen global
    mean_scores = {
        "score_IF":     float(scores["score_IF"].mean()),
        "score_AE":     float(scores["score_AE"].mean()),
        "score_LSTM":   float(scores["score_LSTM"].mean()),
        "score_DBSCAN": float(scores["score_DBSCAN"].mean()),
    }
    for i, col in enumerate(model_cols, 1):
        fig_user.add_hline(
            y=mean_scores[col], line_dash="longdash",
            line_color="#4a7ab5", line_width=1, opacity=0.4,
            annotation_text="moy.", annotation_font_size=9,
            annotation_font_color="#4a7ab5", row=i, col=1
        )
    fig_user.update_layout(
        **PLOTLY_THEME, height=560, showlegend=False,
    )
    for i in range(1, 5):
        fig_user.update_yaxes(gridcolor="#1a2d45", row=i, col=1)
        fig_user.update_xaxes(gridcolor="#1a2d45", row=i, col=1)
    st.markdown('<div style="font-family:JetBrains Mono,monospace; font-size:0.65rem; color:#4a7ab5; margin-bottom:6px;">--- Moyenne globale &nbsp;&nbsp; - - - Seuil alerte &nbsp;&nbsp; x Fenetre alertee</div>', unsafe_allow_html=True)
    st.plotly_chart(fig_user, use_container_width=True)

    # Fenêtres alertées
    alertes_user = user_data[user_data["consensus"] >= 1][
        ["Date","score_IF","score_AE","score_LSTM","score_DBSCAN","consensus"]
    ].sort_values("consensus", ascending=False)

    if len(alertes_user) > 0:
        section_title(f"Fenêtres alertées — {len(alertes_user)} jours", "◈")
        st.dataframe(alertes_user.style.format({
            "score_IF":"{:.4f}","score_AE":"{:.4f}",
            "score_LSTM":"{:.4f}","score_DBSCAN":"{:.4f}"
        }).set_properties(**{"font-family":"JetBrains Mono","font-size":"11px"}),
                     use_container_width=True)

    # SHAP Section
    st.markdown("---")
    section_title("Explicabilite SHAP - Isolation Forest", "")

    if shap_vals_if is not None and shap_feature_cols is not None:
        shap_importance = np.abs(shap_vals_if).mean(axis=0)
        top_n   = 12
        top_idx = np.argsort(shap_importance)[::-1][:top_n]
        top_feats = [shap_feature_cols[i] for i in top_idx]
        top_vals  = [float(shap_importance[i]) for i in top_idx]

        fig_shap = go.Figure(go.Bar(
            x=top_vals[::-1], y=top_feats[::-1], orientation="h",
            marker=dict(
                color=top_vals[::-1],
                colorscale=[[0,"#1a2d45"],[0.3,"#3b82f6"],[1,"#e0ecff"]],
                line=dict(color="#080c14", width=0.5)
            ),
            text=[f"{v:.4f}" for v in top_vals[::-1]],
            textposition="outside",
            textfont=dict(color="#8fa8c8", size=9, family="JetBrains Mono"),
        ))
        fig_shap.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=20, b=20, l=10, r=60), height=380,
        )
        fig_shap.update_xaxes(title="Importance SHAP moyenne", gridcolor="#1a2d45")
        fig_shap.update_yaxes(gridcolor="#1a2d45", tickfont=dict(size=10))
        st.plotly_chart(fig_shap, use_container_width=True)

        top3 = top_feats[:3]
        st.markdown(
            f'<div class="info-card" style="border-color:#3b82f633; margin-top:10px;">' +
            f'<div style="font-family:JetBrains Mono,monospace; font-size:0.62rem; ' +
            f'color:#4a7ab5; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">' +
            f'INTERPRETATION XAI</div>' +
            f'<div style="font-size:0.82rem; color:#8fa8c8; line-height:1.6;">' +
            f'Top 3 features discriminantes : <b style="color:#60a5fa">{top3[0]}</b>, ' +
            f'<b style="color:#60a5fa">{top3[1]}</b>, <b style="color:#60a5fa">{top3[2]}</b>. ' +
            f'Ces features contribuent le plus a isoler les utilisateurs suspects.' +
            f'</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="alert-box-warning">Fichiers SHAP non trouves. ' +
            'Placez shap_vals_if.npy et feature_cols.json dans le dossier Dashboard.</div>',
            unsafe_allow_html=True
        )

# ══════════════════════════════════════════════
# TAB 3 — SCORES & MODÈLES
# ══════════════════════════════════════════════
with tab3:
    section_title("Distribution des scores max par modèle", "◈")

    models_info = [
        ("max_score_IF",     "Isolation Forest", "#3b82f6", "IF"),
        ("max_score_AE",     "Autoencoder",      "#10b981", "AE"),
        ("max_score_LSTM",   "LSTM-AE",          "#f59e0b", "LSTM"),
        ("max_score_DBSCAN", "DBSCAN",           "#ef4444", "DBSCAN"),
    ]

    fig_dist = make_subplots(rows=2, cols=2,
                              subplot_titles=[m[1] for m in models_info],
                              vertical_spacing=0.12, horizontal_spacing=0.08)

    for idx, (col, name, color, key) in enumerate(models_info):
        r, c = divmod(idx, 2)
        fig_dist.add_trace(go.Histogram(
            x=consensus[col], nbinsx=15,
            marker=dict(color=color, opacity=0.8,
                        line=dict(color="#080c14", width=1)),
            name=name
        ), row=r+1, col=c+1)
        fig_dist.add_vline(x=seuils[key], line_dash="dot",
                            line_color="white", opacity=0.5, row=r+1, col=c+1)

    fig_dist.update_layout(**PLOTLY_THEME, height=480, showlegend=False)
    for i in range(1, 3):
        for j in range(1, 3):
            fig_dist.update_yaxes(gridcolor="#1a2d45", row=i, col=j)
            fig_dist.update_xaxes(gridcolor="#1a2d45", row=i, col=j)
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown("---")
    section_title("Radar des suspects (consensus ≥ 2)", "◈")

    top_suspects = consensus[consensus["consensus"] >= 2].copy()
    if "UserID" in top_suspects.columns:
        top_suspects["label"] = top_suspects["UserID"]
    else:
        top_suspects["label"] = top_suspects["UserID_enc"].map(enc_to_label)

    categories = ["IF", "AE", "LSTM", "DBSCAN"]
    fig_radar   = go.Figure()

    colors_radar = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6","#ec4899"]
    for idx, (_, row) in enumerate(top_suspects.iterrows()):
        vals = [row["max_score_IF"], row["max_score_AE"],
                row["max_score_LSTM"], row["max_score_DBSCAN"]]
        maxv = max(vals) if max(vals) > 0 else 1
        vals_norm = [v/maxv for v in vals] + [[v/maxv for v in vals][0]]
        c = colors_radar[idx % len(colors_radar)]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_norm, theta=categories + [categories[0]],
            fill="toself", name=str(row["label"]),
            line=dict(color=c, width=2),
            fillcolor=f"rgba{tuple(list(int(c.lstrip('#')[j:j+2], 16) for j in (0,2,4)) + [0.08])}"
        ))

    fig_radar.update_layout(
        polar=dict(
            bgcolor="#0d1828",
            radialaxis=dict(visible=True, range=[0,1],
                            gridcolor="#1a2d45", linecolor="#1a2d45",
                            tickcolor="#4a7ab5", tickfont=dict(color="#4a7ab5", size=9)),
            angularaxis=dict(gridcolor="#1a2d45", linecolor="#1a2d45",
                             tickfont=dict(color="#8fa8c8", size=10))
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8fa8c8", family="JetBrains Mono"),
        height=400, margin=dict(t=30, b=20),
        legend=dict(font=dict(size=10, color="#8fa8c8"))
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 4 — ÉVOLUTION TEMPORELLE
# ══════════════════════════════════════════════
with tab4:
    # Filtre temporel
    col_f1, col_f2, col_f3 = st.columns([1,1,2])
    with col_f1:
        date_min = scores["Date"].min().date()
        date_max = scores["Date"].max().date()
        start_date = st.date_input("📅 Début", value=date_min, min_value=date_min, max_value=date_max)
    with col_f2:
        end_date = st.date_input("📅 Fin", value=date_max, min_value=date_min, max_value=date_max)
    with col_f3:
        period_preset = st.selectbox("⚡ Période rapide",
            ["Personnalisé","3 derniers mois","6 derniers mois","Toute la période"])
        if period_preset == "3 derniers mois":
            start_date = (scores["Date"].max() - pd.DateOffset(months=3)).date()
            end_date   = date_max
        elif period_preset == "6 derniers mois":
            start_date = (scores["Date"].max() - pd.DateOffset(months=6)).date()
            end_date   = date_max
        elif period_preset == "Toute la période":
            start_date = date_min
            end_date   = date_max

    scores_filtered = scores[
        (scores["Date"].dt.date >= start_date) &
        (scores["Date"].dt.date <= end_date)
    ]
    st.caption(f"Période sélectionnée : **{start_date}** → **{end_date}** | {len(scores_filtered)} fenêtres")
    st.markdown("---")

    section_title("Alertes par jour — tous utilisateurs", "◈")

    daily_alerts = (scores_filtered.groupby("Date")["consensus"]
                    .apply(lambda x: (x >= 1).sum())
                    .reset_index())
    daily_alerts.columns = ["Date", "nb_alertes"]

    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Bar(
        x=daily_alerts["Date"], y=daily_alerts["nb_alertes"],
        marker=dict(color="#ef4444", opacity=0.7,
                    line=dict(color="#080c14", width=0.5)),
        name="Alertes/jour"
    ))
    fig_timeline.add_trace(go.Scatter(
        x=daily_alerts["Date"],
        y=daily_alerts["nb_alertes"].rolling(7, min_periods=1).mean(),
        line=dict(color="#f59e0b", width=2),
        name="Moyenne 7j"
    ))
    fig_timeline.update_layout(**PLOTLY_THEME, height=280,
                                xaxis_title="Date", yaxis_title="Nb alertes")
    st.plotly_chart(fig_timeline, use_container_width=True)

    st.markdown("---")
    section_title("Heatmap consensus — utilisateurs × temps", "◈")

    pivot = scores_filtered.pivot_table(
        index="UserLabel", columns="Date",
        values="consensus", aggfunc="max", fill_value=0
    )
    pivot_suspects = pivot[pivot.max(axis=1) >= 1]

    if len(pivot_suspects) > 0:
        fig_heat = go.Figure(go.Heatmap(
            z=pivot_suspects.values,
            x=[str(d.date()) for d in pivot_suspects.columns],
            y=pivot_suspects.index.tolist(),
            colorscale=[
                [0,    "#0d1828"],
                [0.25, "#1e3a5f"],
                [0.5,  "#f59e0b"],
                [0.75, "#ef4444"],
                [1,    "#8b5cf6"]
            ],
            colorbar=dict(
                title=dict(text="Consensus", font=dict(color="#8fa8c8", family="JetBrains Mono", size=10)),
                tickfont=dict(color="#8fa8c8", family="JetBrains Mono", size=9),
                bgcolor="#0d1828",
                bordercolor="#1a2d45"
            ),
            zmin=0, zmax=4
        ))
        fig_heat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=30, b=20, l=10, r=10),
            height=max(280, len(pivot_suspects) * 45),
        )
        fig_heat.update_xaxes(tickangle=45, tickfont=dict(size=8),
                               gridcolor="#1a2d45", linecolor="#1a2d45")
        st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 5 — ANALYSER UN JOURNAL
# ══════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="info-card" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">
            ◈ ANALYSE EN TEMPS RÉEL
        </div>
        <p style="color:#8fa8c8; font-size:0.85rem; margin:0;">
            Uploadez un fichier CSV contenant les 29 features journalières d'un utilisateur.
            Le pipeline applique automatiquement les 4 modèles et retourne le verdict avec explication.
        </p>
    </div>
    """, unsafe_allow_html=True)

    FEATURE_COLS = [
        'Duration_mean','Duration_max','Duration_std',
        'delta_t_mean','delta_t_min','delta_t_std',
        'Hour_mean','Hour_std','VisitsPerDay_last',
        'Duration_change_rate_mean','Duration_change_rate_std',
        'relative_Duration_mean','relative_Duration_std',
        'VisitIntensity_mean','VisitIntensity_max',
        'VisitRate_change_mean','VisitRate_change_std',
        'CumulativeVisits_last','CumulativeDuration_last','AvgVisitDuration_last',
        'RollingVisitsPerDay_last','Rolling_mean_delta_t_last','Rolling_std_delta_t_last',
        'zscore_Duration_mean','zscore_VisitsPerDay_last',
        'Domain_freq_mean','Domain_freq_nunique',
        'PeakHour_first','DayOfWeek_first'
    ]

    uploaded_file = st.file_uploader("📂 Charger le journal utilisateur (CSV)",
                                      type=["csv"])

    if uploaded_file is not None:
        try:
            import tensorflow as tf
            from tensorflow import keras

            df_new = pd.read_csv(uploaded_file, parse_dates=["Date"])
            st.markdown(f'<div class="alert-box-success">✅ Fichier chargé — {len(df_new)} fenêtres journalières</div>',
                        unsafe_allow_html=True)

            missing = [c for c in FEATURE_COLS if c not in df_new.columns]
            if missing:
                st.markdown(f'<div class="alert-box">❌ Colonnes manquantes : {missing}</div>',
                            unsafe_allow_html=True)
            else:
                progress_bar = st.progress(0, text="⚙️ Initialisation...")
                with st.spinner("Application du pipeline en cours..."):
                    import pickle
                    with open("scaler.pkl", "rb") as f:
                        sc = pickle.load(f)
                    with open("model_if.pkl", "rb") as f:
                        clf_new = pickle.load(f)
                    with open("nbrs_train.pkl", "rb") as f:
                        nbrs_train = pickle.load(f)
                    with open("train_scores.pkl", "rb") as f:
                        train_scores = pickle.load(f)
                    ae_new   = keras.models.load_model("model_ae.keras",   compile=False)
                    lstm_new = keras.models.load_model("model_lstm.keras", compile=False)

                X = df_new[FEATURE_COLS].values
                X_scaled = sc.transform(X)

                # Seuils depuis percentiles train
                th_if   = float(np.percentile(train_scores["if"],     84))
                th_ae   = float(np.percentile(train_scores["ae"],     96))
                th_lstm = float(np.percentile(train_scores["lstm"],   88))
                th_db   = float(np.percentile(train_scores["dbscan"], 99))

                progress_bar.progress(20, text="🔵 Isolation Forest en cours...")
                # IF
                sc_if = -clf_new.score_samples(X_scaled)

                progress_bar.progress(40, text="🟢 Autoencoder en cours...")
                # AE
                recon_ae = ae_new.predict(X_scaled, verbose=0)
                sc_ae    = np.mean((X_scaled - recon_ae) ** 2, axis=1)

                progress_bar.progress(60, text="🟡 LSTM-AE en cours...")
                # LSTM
                TIMESTEPS = 7
                if len(X_scaled) >= TIMESTEPS:
                    seqs = np.array([X_scaled[i:i+TIMESTEPS]
                                     for i in range(len(X_scaled)-TIMESTEPS+1)])
                    recon_lstm  = lstm_new.predict(seqs, verbose=0)
                    errs        = np.mean((seqs - recon_lstm) ** 2, axis=(1,2))
                    sc_lstm_raw = np.concatenate([np.zeros(TIMESTEPS-1), errs])
                else:
                    sc_lstm_raw = np.zeros(len(X_scaled))
                sc_lstm = sc_lstm_raw

                progress_bar.progress(80, text="🔴 DBSCAN en cours...")
                # DBSCAN
                dists, _ = nbrs_train.kneighbors(X_scaled)
                sc_db    = dists[:, -1]

                progress_bar.progress(100, text="✅ Analyse terminée !")
                progress_bar.empty()
                # Flags
                flag_if   = (sc_if   > th_if).astype(int)
                flag_ae   = (sc_ae   > th_ae).astype(int)
                flag_lstm = (sc_lstm > th_lstm).astype(int)
                flag_db   = (sc_db   > th_db).astype(int)
                consensus_w = flag_if + flag_ae + flag_lstm + flag_db
                th = {"IF": th_if, "AE": th_ae, "LSTM": th_lstm, "DBSCAN": th_db}

                df_res = df_new[["Date"]].copy()
                df_res["score_IF"]     = sc_if
                df_res["score_AE"]     = sc_ae
                df_res["score_LSTM"]   = sc_lstm
                df_res["score_DBSCAN"] = sc_db
                df_res["flag_IF"]      = flag_if
                df_res["flag_AE"]      = flag_ae
                df_res["flag_LSTM"]    = flag_lstm
                df_res["flag_DBSCAN"]  = flag_db
                df_res["consensus"]    = consensus_w

                max_cons  = int(consensus_w.max())
                n_alertes = int((consensus_w >= 1).sum())
                pct       = n_alertes / len(df_res) * 100

                # Nouveau verdict basé sur taux d'alerte
                if pct < 10 and max_cons <= 1:
                    verdict_final = "🟢 Normal"
                    vcolor = "#10b981"
                    vclass = "alert-box-success"
                elif pct < 20 and max_cons <= 2:
                    verdict_final = "🟡 Légèrement atypique"
                    vcolor = "#f59e0b"
                    vclass = "alert-box-warning"
                elif pct < 35 and max_cons <= 3:
                    verdict_final = "🟠 Suspect (modéré)"
                    vcolor = "#f97316"
                    vclass = "alert-box"
                else:
                    verdict_final = "🔴 Suspect (confirmé)"
                    vcolor = "#ef4444"
                    vclass = "alert-box"

                risk_pct_bar = min(pct / 100 * 100, 100)

                st.markdown("---")

                # Verdict card
                st.markdown(f"""
                <div class="info-card" style="border-color:{vcolor}33; margin-bottom:20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem;
                                        color:#4a7ab5; text-transform:uppercase; letter-spacing:2px;">
                                VERDICT FINAL
                            </div>
                            <div style="font-family:'Syne',sans-serif; font-size:1.8rem;
                                        font-weight:800; color:{vcolor}; margin-top:4px;">
                                {verdict_final}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:'JetBrains Mono',monospace; font-size:2rem;
                                        font-weight:800; color:{vcolor};">
                                {pct:.1f}%
                            </div>
                            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                                        color:#4a7ab5;">taux d'alerte</div>
                        </div>
                    </div>
                    <div style="margin-top:14px; background:#080c14; border-radius:4px;
                                height:6px; overflow:hidden; border:1px solid #1a2d45;">
                        <div style="height:100%; width:{risk_pct_bar}%; background:{vcolor};
                                    border-radius:4px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # KPIs
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("Consensus max",     f"{max_cons} / 4")
                k2.metric("Fenêtres alertées", f"{n_alertes} / {len(df_res)}")
                k3.metric("Taux d'alerte",     f"{pct:.1f}%")
                k4.metric("Modèles déclenchés",
                          f"IF:{int(flag_if.max())} AE:{int(flag_ae.max())} "
                          f"L:{int(flag_lstm.max())} DB:{int(flag_db.max())}")

                st.markdown("---")

                # Score bars
                col_sb, col_exp = st.columns([1, 1])
                with col_sb:
                    section_title("Scores vs seuils", "◈")
                    score_bar("Isolation Forest", float(sc_if.max()),  th_if,   "#3b82f6")
                    score_bar("Autoencoder",      float(sc_ae.max()),  th_ae,   "#10b981")
                    score_bar("LSTM-AE",          float(sc_lstm.max()),th_lstm, "#f59e0b")
                    score_bar("DBSCAN",           float(sc_db.max()),  th_db,   "#ef4444")

                with col_exp:
                    section_title("Explication du verdict", "◈")

                    # ── Identifier le type d'anomalie dominant
                    worst_idx  = int(df_res["consensus"].idxmax())
                    X_worst    = df_new[FEATURE_COLS].iloc[worst_idx].values
                    X_mean     = df_new[FEATURE_COLS].mean().values
                    X_std      = df_new[FEATURE_COLS].std().values + 1e-6
                    zscores    = (X_worst - X_mean) / X_std
                    abs_z      = np.abs(zscores)
                    top1_feat  = FEATURE_COLS[int(np.argmax(abs_z))]
                    top1_z     = float(zscores[np.argmax(abs_z)])

                    # Détecter le type d'anomalie à partir des features dominantes
                    night_feats   = ["Hour_mean","Hour_std","PeakHour_first"]
                    burst_feats   = ["VisitsPerDay_last","RollingVisitsPerDay_last",
                                     "zscore_VisitsPerDay_last","VisitIntensity_max",
                                     "VisitRate_change_mean","delta_t_min"]
                    session_feats = ["Duration_mean","Duration_max","zscore_Duration_mean",
                                     "AvgVisitDuration_last","CumulativeDuration_last"]

                    top5_feats = [FEATURE_COLS[i] for i in np.argsort(abs_z)[::-1][:5]]
                    night_score   = sum(1 for f in top5_feats if f in night_feats)
                    burst_score   = sum(1 for f in top5_feats if f in burst_feats)
                    session_score = sum(1 for f in top5_feats if f in session_feats)

                    if night_score >= burst_score and night_score >= session_score:
                        anom_type  = "🌙 Navigation nocturne"
                        anom_color = "#8b5cf6"
                        anom_desc  = "L'utilisateur présente une activité inhabituelle hors des heures de bureau (nuit, week-end). Les heures de connexion s'écartent significativement de son profil normal."
                    elif burst_score >= session_score:
                        anom_type  = "⚡ Burst d'activité"
                        anom_color = "#ef4444"
                        anom_desc  = "Un pic anormal du volume de visites a été détecté. Le nombre de requêtes par jour dépasse largement la moyenne habituelle de l'utilisateur."
                    else:
                        anom_type  = "⏱ Sessions prolongées"
                        anom_color = "#f59e0b"
                        anom_desc  = "Des sessions de navigation anormalement longues ont été détectées. Les durées de visite dépassent significativement le profil habituel de l'utilisateur."

                    # Carte type d'anomalie
                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.3); border:1px solid {anom_color}44;
                                border-left:3px solid {anom_color}; border-radius:8px;
                                padding:14px 16px; margin-bottom:12px;">
                        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase; margin-bottom:6px;">
                            TYPE D'ANOMALIE DÉTECTÉ
                        </div>
                        <div style="font-family:'Syne',sans-serif; font-size:1.1rem;
                                    font-weight:700; color:{anom_color}; margin-bottom:8px;">
                            {anom_type}
                        </div>
                        <div style="font-size:0.82rem; color:#8fa8c8; line-height:1.5;">
                            {anom_desc}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Feature la plus discriminante
                    feat_direction = "au-dessus" if top1_z > 0 else "en-dessous"
                    st.markdown(f"""
                    <div style="background:#0d1828; border:1px solid #1a2d45; border-radius:8px;
                                padding:12px 16px; margin-bottom:12px;">
                        <div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem;
                                    color:#4a7ab5; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px;">
                            SIGNAL PRINCIPAL
                        </div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:0.85rem; color:#60a5fa;">
                            {top1_feat}
                        </div>
                        <div style="font-size:0.78rem; color:#8fa8c8; margin-top:4px;">
                            Valeur <b style="color:#e0ecff">{abs(top1_z):.1f}σ</b> {feat_direction} de la normale
                            de cet utilisateur — écart le plus significatif détecté.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Détail par modèle déclenché
                    model_details = []
                    if flag_if.max() == 1:
                        top_day = df_res.loc[df_res["score_IF"].idxmax(), "Date"]
                        model_details.append(("IF", "#3b82f6", "Isolation Forest",
                            f"Comportement statistiquement isolé le {str(top_day)[:10]} — ses features le placent loin du cluster normal.",
                            f"{df_res['score_IF'].max():.4f}", f"{th_if:.4f}"))
                    if flag_ae.max() == 1:
                        top_day = df_res.loc[df_res["score_AE"].idxmax(), "Date"]
                        model_details.append(("AE", "#10b981", "Autoencoder",
                            f"Profil de navigation difficile à reconstruire le {str(top_day)[:10]} — les patterns s'écartent de ce qui est considéré normal.",
                            f"{df_res['score_AE'].max():.4f}", f"{th_ae:.4f}"))
                    if flag_lstm.max() == 1:
                        top_day = df_res.loc[df_res["score_LSTM"].idxmax(), "Date"]
                        model_details.append(("LSTM", "#f59e0b", "LSTM-AE",
                            f"Séquence temporelle anormale détectée autour du {str(top_day)[:10]} — la progression sur 7 jours consécutifs est inhabituelle.",
                            f"{df_res['score_LSTM'].max():.4f}", f"{th_lstm:.4f}"))
                    if flag_db.max() == 1:
                        top_day = df_res.loc[df_res["score_DBSCAN"].idxmax(), "Date"]
                        model_details.append(("DB", "#ef4444", "DBSCAN",
                            f"Point outlier détecté le {str(top_day)[:10]} — l'utilisateur est isolé dans l'espace des features de volume.",
                            f"{df_res['score_DBSCAN'].max():.4f}", f"{th_db:.4f}"))

                    if model_details:
                        st.markdown('<div style="font-family:JetBrains Mono,monospace; font-size:0.62rem; color:#4a7ab5; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">MODÈLES DÉCLENCHÉS</div>', unsafe_allow_html=True)
                        for tag, color, name, desc, score, seuil in model_details:
                            st.markdown(f"""
                            <div style="background:#0d1828; border:1px solid {color}33;
                                        border-left:2px solid {color}; border-radius:6px;
                                        padding:10px 14px; margin-bottom:6px; display:flex;
                                        gap:12px; align-items:flex-start;">
                                <div style="background:{color}22; color:{color}; border:1px solid {color}44;
                                            border-radius:4px; padding:2px 7px; font-family:'JetBrains Mono',monospace;
                                            font-size:0.65rem; font-weight:700; white-space:nowrap; margin-top:2px;">
                                    {tag}
                                </div>
                                <div style="flex:1;">
                                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.72rem;
                                                color:#e0ecff; font-weight:600; margin-bottom:3px;">{name}</div>
                                    <div style="font-size:0.78rem; color:#8fa8c8; line-height:1.4;">{desc}</div>
                                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                                                color:{color}; margin-top:5px;">
                                        score={score} &nbsp;›&nbsp; seuil={seuil}
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="alert-box-success">✅ Aucun modèle déclenché — comportement normal.</div>', unsafe_allow_html=True)

                    # Top features anormales
                    st.markdown("---")
                    section_title("Top 5 features anormales", "◈")
                    top5_idx = np.argsort(abs_z)[::-1][:5]
                    feat_df  = pd.DataFrame({
                        "Feature":  [FEATURE_COLS[i] for i in top5_idx],
                        "Valeur":   [round(X_worst[i], 4) for i in top5_idx],
                        "Moyenne":  [round(X_mean[i], 4)  for i in top5_idx],
                        "Z-score":  [round(zscores[i], 2)  for i in top5_idx],
                    })
                    st.dataframe(feat_df.style.set_properties(
                        **{"font-family":"JetBrains Mono","font-size":"11px"}
                    ).bar(subset=["Z-score"], color=["#1a2d45","#ef4444"]),
                    use_container_width=True)

                # Graphique temporel
                st.markdown("---")
                section_title("Évolution temporelle des scores", "◈")

                fig_new = make_subplots(rows=4, cols=1, shared_xaxes=True,
                                         subplot_titles=["IF","AE","LSTM-AE","DBSCAN"],
                                         vertical_spacing=0.05)
                for i, (col, name, color, thr_key) in enumerate([
                    ("score_IF","IF","#3b82f6","IF"),
                    ("score_AE","AE","#10b981","AE"),
                    ("score_LSTM","LSTM","#f59e0b","LSTM"),
                    ("score_DBSCAN","DBSCAN","#ef4444","DBSCAN")
                ], 1):
                    thr_v = th[thr_key]
                    fig_new.add_trace(go.Scatter(
                        x=df_res["Date"], y=df_res[col],
                        mode="lines", line=dict(color=color, width=1.5),
                        fill="tozeroy",
                        fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[j:j+2],16) for j in (0,2,4))+[0.05])}",
                        name=name
                    ), row=i, col=1)
                    fig_new.add_hline(y=thr_v, line_dash="dot",
                                      line_color=color, opacity=0.4, row=i, col=1)
                    alerts_n = df_res[df_res[col] > thr_v]
                    if len(alerts_n) > 0:
                        fig_new.add_trace(go.Scatter(
                            x=alerts_n["Date"], y=alerts_n[col], mode="markers",
                            marker=dict(color="#ef4444", size=7, symbol="x"),
                            showlegend=False
                        ), row=i, col=1)

                fig_new.update_layout(**PLOTLY_THEME, height=540, showlegend=False)
                st.plotly_chart(fig_new, use_container_width=True)

                # ── Bouton export PDF
                st.markdown("---")
                section_title("Exporter le rapport", "◈")

                if st.button("📄 Générer le rapport PDF", type="primary"):
                    with st.spinner("Génération du PDF..."):
                        scores_for_pdf = {
                            "IF":     float(sc_if.max()),
                            "AE":     float(sc_ae.max()),
                            "LSTM":   float(sc_lstm.max()),
                            "DBSCAN": float(sc_db.max()),
                        }
                        seuils_for_pdf = {
                            "IF": th_if, "AE": th_ae,
                            "LSTM": th_lstm, "DBSCAN": th_db
                        }
                        # Récupérer feat_df si défini
                        try:
                            pdf_buf = generate_pdf_report(
                                user_name  = uploaded_file.name.replace(".csv",""),
                                verdict    = verdict_final,
                                consensus  = max_cons,
                                pct_alerte = pct,
                                scores_dict = scores_for_pdf,
                                seuils_dict = seuils_for_pdf,
                                feat_df    = feat_df,
                                anom_type  = anom_type,
                                anom_desc  = anom_desc,
                            )
                            st.download_button(
                                label="⬇️ Télécharger le rapport PDF",
                                data=pdf_buf,
                                file_name=f"rapport_{uploaded_file.name.replace('.csv','')}.pdf",
                                mime="application/pdf",
                            )
                            st.markdown('<div class="alert-box-success">✅ Rapport PDF généré avec succès !</div>',
                                        unsafe_allow_html=True)
                        except Exception as pdf_err:
                            st.error(f"Erreur PDF : {pdf_err}")

        except Exception as e:
            st.markdown(f'<div class="alert-box">❌ Erreur : {e}</div>',
                        unsafe_allow_html=True)
            import traceback
            st.code(traceback.format_exc())

# ══════════════════════════════════════════════
# TAB 6 — CRITÈRES DE DÉTECTION
# ══════════════════════════════════════════════
with tab6:
    st.markdown("""
    <div class="cyber-header" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
            DOCUMENTATION DU PIPELINE
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                    font-weight:800; color:#e0ecff; margin-top:6px;">
            Critères de détection — 4 modèles complémentaires
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="info-card" style="border-color:#3b82f633; margin-bottom:12px;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        color:#3b82f6; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                ◈ ISOLATION FOREST — seuil {seuils['IF']:.4f}
            </div>
            <p style="color:#8fa8c8; font-size:0.82rem;">
                Détecte les utilisateurs dont les features sont <b style="color:#e0ecff">très éloignées</b>
                du comportement moyen de la population.
            </p>
            <div style="margin-top:10px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#4a7ab5;">
                TOP FEATURES :<br>
                · VisitIntensity_max — pic d'intensité<br>
                · delta_t_min — cadence frénétique<br>
                · zscore_VisitsPerDay_last — volume anormal
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="border-color:#f59e0b33; margin-bottom:12px;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        color:#f59e0b; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                ◈ LSTM-AE — seuil {seuils['LSTM']:.4f}
            </div>
            <p style="color:#8fa8c8; font-size:0.82rem;">
                Détecte les <b style="color:#e0ecff">changements brusques sur 7 jours consécutifs</b>
                via reconstruction de séquences temporelles.
            </p>
            <div style="margin-top:10px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#4a7ab5;">
                TOP FEATURES :<br>
                · VisitRate_change_std — variation rythme<br>
                · Rolling_mean_delta_t_last — intervalles<br>
                · Duration_change_rate_std — durée variable
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="info-card" style="border-color:#10b98133; margin-bottom:12px;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        color:#10b981; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                ◈ AUTOENCODER — seuil {seuils['AE']:.4f}
            </div>
            <p style="color:#8fa8c8; font-size:0.82rem;">
                Détecte les profils que le modèle <b style="color:#e0ecff">ne peut pas reconstruire</b>
                fidèlement — trop différents des profils normaux.
            </p>
            <div style="margin-top:10px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#4a7ab5;">
                TOP FEATURES :<br>
                · zscore_Duration_mean — durée anormale<br>
                · Hour_std — variabilité horaire<br>
                · Hour_mean — navigation nocturne
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="info-card" style="border-color:#ef444433; margin-bottom:12px;">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        color:#ef4444; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px;">
                ◈ DBSCAN — seuil {seuils['DBSCAN']:.4f}
            </div>
            <p style="color:#8fa8c8; font-size:0.82rem;">
                Détecte les utilisateurs <b style="color:#e0ecff">isolés dans l'espace des features</b>,
                loin de tous les clusters normaux.
            </p>
            <div style="margin-top:10px; font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#4a7ab5;">
                TOP FEATURES :<br>
                · VisitsPerDay_last — burst de visites<br>
                · Hour_mean — sessions nocturnes<br>
                · Domain_freq_nunique — nouveaux domaines
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    section_title("Tableau de consensus et actions", "◈")

    consensus_table = pd.DataFrame({
        "Consensus": ["0 modèle", "1 modèle", "2 modèles", "3 modèles", "4 modèles"],
        "Verdict":   ["🟢 Normal", "🟡 Légèrement atypique",
                      "🟠 Suspect modéré", "🔴 Suspect fort", "🟣 Insider confirmé"],
        "Taux d'alerte typique": ["< 10%", "10–15%", "15–25%", "25–40%", "> 40%"],
        "Action recommandée": [
            "Aucune action",
            "Surveillance passive",
            "Surveillance active",
            "Investigation planifiée",
            "Alerte immédiate — escalade"
        ]
    })
    st.dataframe(consensus_table.style.set_properties(
        **{"font-family":"JetBrains Mono","font-size":"12px"}
    ), use_container_width=True, hide_index=True)

    st.markdown("---")
    section_title("Format CSV attendu — 29 features", "◈")
    st.code("""Date, Duration_mean, Duration_max, Duration_std,
delta_t_mean, delta_t_min, delta_t_std,
Hour_mean, Hour_std, VisitsPerDay_last,
Duration_change_rate_mean, Duration_change_rate_std,
relative_Duration_mean, relative_Duration_std,
VisitIntensity_mean, VisitIntensity_max,
VisitRate_change_mean, VisitRate_change_std,
CumulativeVisits_last, CumulativeDuration_last, AvgVisitDuration_last,
RollingVisitsPerDay_last, Rolling_mean_delta_t_last, Rolling_std_delta_t_last,
zscore_Duration_mean, zscore_VisitsPerDay_last,
Domain_freq_mean, Domain_freq_nunique, PeakHour_first, DayOfWeek_first""",
            language="text")


# ══════════════════════════════════════════════
# TAB 7 — MÉTRIQUES PIPELINE
# ══════════════════════════════════════════════
with tab7:
    st.markdown("""
    <div class="cyber-header" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
            PERFORMANCE DU PIPELINE
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                    font-weight:800; color:#e0ecff; margin-top:6px;">
            Métriques de détection — 4 modèles
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Métriques par modèle
    metrics_data = {
        "Modèle":     ["Isolation Forest", "Autoencoder", "LSTM-AE", "DBSCAN", "Consensus"],
        "Recall":     [0.385, 1.000, 0.889, 0.630, 1.000],
        "Précision":  [1.000, 1.000, 0.571, 0.739, 0.593],
        "F1-Score":   [0.556, 1.000, 0.690, 0.680, 0.745],
        "AUC-ROC":    [0.917, 0.935, 0.750, 0.834, 0.948],
        "Spécialité": ["Burst/Intensité", "Night/Long session",
                        "Long session", "Burst/Volume", "Tous types"],
    }
    df_metrics = pd.DataFrame(metrics_data)

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Recall Consensus",    "100%",  "27/27 anomalies")
    col_m2.metric("F1 Consensus",        "0.745", "+34% vs IF seul")
    col_m3.metric("AUC-ROC Consensus",   "0.948", "Meilleur modèle")
    col_m4.metric("Faux positifs",       "0",     "Sur test set")

    st.markdown("---")
    section_title("Performance par modèle", "◈")

    model_colors_metrics = {
        "Isolation Forest": "#3b82f6",
        "Autoencoder":      "#10b981",
        "LSTM-AE":          "#f59e0b",
        "DBSCAN":           "#ef4444",
        "Consensus":        "#8b5cf6",
    }

    fig_metrics = go.Figure()
    metrics_cols = ["Recall", "Précision", "F1-Score", "AUC-ROC"]
    for _, row in df_metrics.iterrows():
        color = model_colors_metrics.get(row["Modèle"], "#4a7ab5")
        fig_metrics.add_trace(go.Bar(
            name=row["Modèle"],
            x=metrics_cols,
            y=[row[c] for c in metrics_cols],
            marker=dict(color=color, opacity=0.85,
                        line=dict(color="#080c14", width=1)),
        ))

    fig_metrics.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8fa8c8", family="JetBrains Mono"),
        margin=dict(t=30, b=20, l=10, r=10),
        height=380, barmode="group",
        legend=dict(font=dict(size=10, color="#8fa8c8")),
    )
    fig_metrics.update_yaxes(range=[0, 1.1], gridcolor="#1a2d45")
    fig_metrics.update_xaxes(gridcolor="#1a2d45")
    st.plotly_chart(fig_metrics, use_container_width=True)

    st.markdown("---")
    section_title("Recall par type d'anomalie", "◈")

    recall_data = {
        "Type":             ["Burst", "Night", "Long Session"],
        "Isolation Forest": [0.900, 0.000, 1.000],
        "Autoencoder":      [0.000, 1.000, 1.000],
        "LSTM-AE":          [0.000, 0.000, 1.000],
        "DBSCAN":           [0.800, 0.000, 1.000],
        "Consensus (≥1)":   [1.000, 1.000, 1.000],
    }
    df_recall = pd.DataFrame(recall_data)

    fig_recall = go.Figure()
    model_cols_r = ["Isolation Forest","Autoencoder","LSTM-AE","DBSCAN","Consensus (≥1)"]
    colors_r     = ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6"]
    for col, color in zip(model_cols_r, colors_r):
        fig_recall.add_trace(go.Bar(
            name=col, x=df_recall["Type"], y=df_recall[col],
            marker=dict(color=color, opacity=0.85,
                        line=dict(color="#080c14", width=1)),
        ))
    fig_recall.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8fa8c8", family="JetBrains Mono"),
        margin=dict(t=30, b=20, l=10, r=10),
        height=320, barmode="group",
        legend=dict(font=dict(size=10, color="#8fa8c8")),
    )
    fig_recall.update_yaxes(range=[0, 1.15], gridcolor="#1a2d45")
    fig_recall.update_xaxes(gridcolor="#1a2d45")
    st.plotly_chart(fig_recall, use_container_width=True)

    st.markdown("""
    <div class="alert-box-success" style="margin-top:12px;">
        ✅ <b>Recall global = 100%</b> — Les 27/27 fenêtres injectées sont détectées
        par au moins 1 modèle. Chaque type d'anomalie est couvert par au moins
        un modèle spécialisé.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    section_title("Tableau comparatif complet", "◈")
    def color_metric(val):
        try:
            v = float(val)
            if v >= 0.9:  return "background-color:#0a2d1a; color:#34d399"
            if v >= 0.7:  return "background-color:#0a2520; color:#6ee7b7"
            if v >= 0.5:  return "background-color:#2d250a; color:#fbbf24"
            if v >  0.0:  return "background-color:#2d1a0a; color:#fb923c"
        except:
            pass
        return ""

    st.dataframe(
        df_metrics.style
        .map(color_metric, subset=["Recall","Précision","F1-Score","AUC-ROC"])
        .set_properties(**{"font-family":"JetBrains Mono","font-size":"12px"}),
        use_container_width=True, hide_index=True
    )


# ══════════════════════════════════════════════
# TAB 8 — MLFLOW EXPÉRIENCES
# ══════════════════════════════════════════════
with tab8:
    st.markdown("""
    <div class="cyber-header" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
            MLOPS — TRAÇABILITÉ DES EXPÉRIENCES
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                    font-weight:800; color:#e0ecff; margin-top:6px;">
            MLflow — Suivi des modèles et hyperparamètres
        </div>
        <div style="margin-top:10px;">
            <span class="cyber-badge">VERSIONING</span>
            <span class="cyber-badge">REPRODUCTIBILITÉ</span>
            <span class="cyber-badge">TRAÇABILITÉ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tentative chargement MLflow ──────────────────────────
    import os
    mlflow_available = False
    mlflow_runs_data = []

    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        tracking_uri = "./mlruns"
        if os.path.exists(tracking_uri):
            mlflow.set_tracking_uri(tracking_uri)
            client = MlflowClient()
            experiments = client.search_experiments()

            for exp in experiments:
                runs = client.search_runs(
                    experiment_ids=[exp.experiment_id],
                    order_by=["start_time DESC"]
                )
                for run in runs:
                    mlflow_runs_data.append({
                        "Run ID":      run.info.run_id[:8] + "...",
                        "Modèle":      run.data.params.get("model", run.info.run_name),
                        "Dataset":     run.data.params.get("dataset", "—"),
                        "Quantile":    run.data.params.get("quantile", "—"),
                        "Seuil":       run.data.params.get("threshold", "—"),
                        "Recall":      round(float(run.data.metrics.get("recall", 0)), 3),
                        "Précision":   round(float(run.data.metrics.get("precision", 0)), 3),
                        "F1":          round(float(run.data.metrics.get("f1", 0)), 3),
                        "AUC-ROC":     round(float(run.data.metrics.get("auc_roc", 0)), 3),
                        "AUC-PR":      round(float(run.data.metrics.get("auc_pr", 0)), 3),
                        "Status":      run.info.status,
                    })
            mlflow_available = len(mlflow_runs_data) > 0

    except Exception as e:
        mlflow_available = False

    # ── Si MLflow disponible ─────────────────────────────────
    if mlflow_available:
        df_runs = pd.DataFrame(mlflow_runs_data)

        # KPIs MLflow
        col_ml1, col_ml2, col_ml3, col_ml4 = st.columns(4)
        col_ml1.metric("Runs enregistrés", len(df_runs))
        col_ml2.metric("Meilleur F1",
                       f"{df_runs['F1'].max():.3f}",
                       df_runs.loc[df_runs['F1'].idxmax(), 'Modèle'])
        col_ml3.metric("Meilleur Recall",
                       f"{df_runs['Recall'].max():.3f}",
                       df_runs.loc[df_runs['Recall'].idxmax(), 'Modèle'])
        col_ml4.metric("Meilleur AUC-ROC",
                       f"{df_runs['AUC-ROC'].max():.3f}",
                       df_runs.loc[df_runs['AUC-ROC'].idxmax(), 'Modèle'])

        st.markdown("---")
        section_title("Tableau des runs MLflow", "◈")

        def color_f1(val):
            try:
                v = float(val)
                if v >= 0.9:  return "background-color:#0a2d1a; color:#34d399"
                if v >= 0.7:  return "background-color:#0a2520; color:#6ee7b7"
                if v >= 0.5:  return "background-color:#2d250a; color:#fbbf24"
                if v >  0.0:  return "background-color:#2d1a0a; color:#fb923c"
            except: pass
            return ""

        st.dataframe(
            df_runs.style
            .map(color_f1, subset=["Recall", "Précision", "F1", "AUC-ROC"])
            .set_properties(**{"font-family": "JetBrains Mono", "font-size": "12px"}),
            use_container_width=True, hide_index=True
        )

        st.markdown("---")
        section_title("Comparaison visuelle des runs", "◈")

        # Graphique comparaison
        metrics_to_plot = ["Recall", "Précision", "F1", "AUC-ROC"]
        model_colors_ml = {
            "IsolationForest":   "#3b82f6",
            "Autoencoder":       "#10b981",
            "LSTM_Autoencoder":  "#f59e0b",
            "DBSCAN":            "#ef4444",
            "Consensus":         "#8b5cf6",
        }

        fig_ml = go.Figure()
        for _, row in df_runs.iterrows():
            color = model_colors_ml.get(row["Modèle"], "#4a7ab5")
            fig_ml.add_trace(go.Bar(
                name=row["Modèle"],
                x=metrics_to_plot,
                y=[row[m] for m in metrics_to_plot],
                marker=dict(color=color, opacity=0.85,
                            line=dict(color="#080c14", width=1)),
            ))
        fig_ml.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=30, b=20, l=10, r=10),
            height=380, barmode="group",
            legend=dict(font=dict(size=10, color="#8fa8c8")),
        )
        fig_ml.update_yaxes(range=[0, 1.1], gridcolor="#1a2d45")
        fig_ml.update_xaxes(gridcolor="#1a2d45")
        st.plotly_chart(fig_ml, use_container_width=True)

        st.markdown("---")
        section_title("Lien vers l'interface MLflow complète", "◈")
        st.markdown("""
        <div class="alert-box-success">
            ✅ MLflow UI disponible — Lance dans ton terminal :
            <code style="font-family:'JetBrains Mono',monospace; font-size:0.85rem;">
            mlflow ui --backend-store-uri ./mlruns --port 5000
            </code>
            puis ouvre <b>http://localhost:5000</b>
        </div>
        """, unsafe_allow_html=True)

    # ── Si MLflow non disponible : données statiques ─────────
    else:
        st.markdown("""
        <div class="alert-box-warning" style="margin-bottom:20px;">
            ⚠️ Dossier <code>mlruns/</code> non trouvé — affichage des métriques statiques du pipeline.
            <br>Pour activer MLflow : place le dossier <code>mlruns/</code> téléchargé depuis Kaggle
            dans le même répertoire que ce dashboard.
        </div>
        """, unsafe_allow_html=True)

        # ── Données statiques du pipeline ────────────────────
        static_runs = pd.DataFrame({
            "Modèle":    ["Isolation Forest", "Autoencoder", "LSTM-AE", "DBSCAN", "Consensus"],
            "Dataset":   ["internal_13users"] * 5,
            "Quantile":  ["q90", "q98", "q92", "q99", "≥1 modèle"],
            "Seuil":     [0.5682, 1.3018, 1.6656, 0.5219, "—"],
            "Recall":    [0.385, 1.000, 0.409, 0.704, 1.000],
            "Précision": [1.000, 1.000, 0.409, 0.576, 0.047],
            "F1":        [0.556, 1.000, 0.409, 0.633, 0.083],
            "AUC-ROC":   [0.923, 0.921, 0.734, 0.846, 0.959],
            "AUC-PR":    [0.049, 0.204, 0.039, 0.087, 0.168],
            "Spécialité":["Burst/Intensité", "Night/Long session",
                          "Long session", "Burst/Volume", "Tous types"],
        })

        # KPIs statiques
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        col_s1.metric("Runs documentés", "5")
        col_s2.metric("Meilleur F1",     "1.000", "Autoencoder")
        col_s3.metric("Meilleur Recall", "1.000", "AE + Consensus")
        col_s4.metric("Recall Global",   "100%",  "27/27 fenêtres")

        st.markdown("---")
        section_title("Paramètres et métriques par modèle", "◈")

        def color_metric_ml(val):
            try:
                v = float(val)
                if v >= 0.9:  return "background-color:#0a2d1a; color:#34d399"
                if v >= 0.7:  return "background-color:#0a2520; color:#6ee7b7"
                if v >= 0.5:  return "background-color:#2d250a; color:#fbbf24"
                if v >  0.0:  return "background-color:#2d1a0a; color:#fb923c"
            except: pass
            return ""

        st.dataframe(
            static_runs.style
            .map(color_metric_ml, subset=["Recall", "Précision", "F1", "AUC-ROC"])
            .set_properties(**{"font-family": "JetBrains Mono", "font-size": "12px"}),
            use_container_width=True, hide_index=True
        )

        st.markdown("---")
        section_title("Comparaison visuelle — 5 modèles", "◈")

        metrics_static = ["Recall", "Précision", "F1", "AUC-ROC"]
        colors_static  = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]

        fig_static = go.Figure()
        for i, row in static_runs.iterrows():
            fig_static.add_trace(go.Bar(
                name=row["Modèle"],
                x=metrics_static,
                y=[row[m] for m in metrics_static],
                marker=dict(color=colors_static[i], opacity=0.85,
                            line=dict(color="#080c14", width=1)),
            ))
        fig_static.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=30, b=20, l=10, r=10),
            height=380, barmode="group",
            legend=dict(font=dict(size=10, color="#8fa8c8")),
        )
        fig_static.update_yaxes(range=[0, 1.15], gridcolor="#1a2d45")
        fig_static.update_xaxes(gridcolor="#1a2d45")
        st.plotly_chart(fig_static, use_container_width=True)

        st.markdown("---")
        section_title("Recall par type d'anomalie — Spécialisation des modèles", "◈")

        recall_type = pd.DataFrame({
            "Type":             ["Burst", "Night", "Long Session"],
            "Isolation Forest": [0.000,   0.000,   1.000],
            "Autoencoder":      [0.000,   1.000,   1.000],
            "LSTM-AE":          [0.000,   0.000,   1.000],
            "DBSCAN":           [1.000,   0.000,   1.000],
            "Consensus (≥1)":   [1.000,   1.000,   1.000],
        })

        fig_recall_ml = go.Figure()
        cols_r  = ["Isolation Forest", "Autoencoder", "LSTM-AE", "DBSCAN", "Consensus (≥1)"]
        clrs_r  = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        for col, clr in zip(cols_r, clrs_r):
            fig_recall_ml.add_trace(go.Bar(
                name=col, x=recall_type["Type"], y=recall_type[col],
                marker=dict(color=clr, opacity=0.85,
                            line=dict(color="#080c14", width=1)),
            ))
        fig_recall_ml.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#8fa8c8", family="JetBrains Mono"),
            margin=dict(t=30, b=20, l=10, r=10),
            height=320, barmode="group",
            legend=dict(font=dict(size=10, color="#8fa8c8")),
        )
        fig_recall_ml.update_yaxes(range=[0, 1.15], gridcolor="#1a2d45")
        fig_recall_ml.update_xaxes(gridcolor="#1a2d45")
        st.plotly_chart(fig_recall_ml, use_container_width=True)

        st.markdown("""
        <div class="alert-box-success" style="margin-top:12px;">
            ✅ <b>Recall global = 100%</b> — Chaque type d'anomalie est couvert
            par au moins un modèle spécialisé. La complémentarité des 4 modèles
            garantit une détection exhaustive.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        section_title("Instructions — Activer MLflow", "◈")
        st.markdown("""
        <div class="info-card">
            <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                        color:#4a7ab5; letter-spacing:2px; margin-bottom:14px;">
                ÉTAPES D'ACTIVATION
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.code("""# 1. Sur Kaggle — logger les expériences
import mlflow
mlflow.set_tracking_uri("file:///kaggle/working/mlruns")
mlflow.set_experiment("insider_threat_detection")

with mlflow.start_run(run_name="Isolation_Forest"):
    mlflow.log_param("model", "IsolationForest")
    mlflow.log_param("threshold", 0.5682)
    mlflow.log_metric("recall", 0.385)
    mlflow.log_metric("f1", 0.556)

# Zipper et télécharger
import shutil
shutil.make_archive('/kaggle/working/mlruns_pfe', 'zip',
                    '/kaggle/working/', 'mlruns')

# 2. En local — extraire le zip dans le dossier du dashboard
# 3. Lancer MLflow UI
# mlflow ui --backend-store-uri ./mlruns --port 5000
# Ouvrir http://localhost:5000""", language="python")


# ══════════════════════════════════════════════
# TAB 9 — DATA DRIFT + MONITORING CONTINU
# ══════════════════════════════════════════════
with tab9:
    # ── Import monitoring ────────────────────────────────
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from retrain_monitor import ContinuousMonitor, KaggleRetrainer
        monitor_available = True
    except ImportError:
        monitor_available = False

    st.markdown("""
    <div class="cyber-header" style="margin-bottom:20px;">
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    color:#4a7ab5; letter-spacing:2px; text-transform:uppercase;">
            MLOPS — MONITORING CONTINU + RE-ENTRAÎNEMENT
        </div>
        <div style="font-family:'Syne',sans-serif; font-size:1.3rem;
                    font-weight:800; color:#e0ecff; margin-top:6px;">
            Data Drift · Evidently · Kaggle API
        </div>
        <div style="margin-top:10px;">
            <span class="cyber-badge">TRAIN vs TEST</span>
            <span class="cyber-badge">WASSERSTEIN</span>
            <span class="cyber-badge">KAGGLE API</span>
            <span class="cyber-badge">AUTO-RETRAIN</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if monitor_available:
        monitor   = ContinuousMonitor()
        retrainer = KaggleRetrainer()

        # ── Résumé dernier check ──────────────────────────
        summary = monitor.get_drift_summary()
        if summary:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Features driftées",  f"{summary['n_drifted']}/4")
            col_m2.metric("Features critiques", f"{summary['n_critical']}/4")
            col_m3.metric("Total checks",       summary["total_checks"])
            col_m4.metric("Alertes totales",    summary["total_alerts"])
            st.caption(f"Dernier check : {summary['last_check'][:19]}")
        else:
            st.info("Aucun check effectué — lance un monitoring ci-dessous.")

        st.markdown("---")
        section_title("Actions MLOps", "◈")

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("📡 Lancer monitoring drift", use_container_width=True):
                with st.spinner("Calcul du drift en cours..."):
                    result = monitor.run_monitoring_check(auto_retrain=True)
                if result:
                    st.success(f"✅ {result['n_drifted']}/4 features driftées")
                    if result["retrain_triggered"]:
                        st.warning("🔄 Re-entraînement déclenché automatiquement !")
                    if result.get("report_path"):
                        with open(result["report_path"], "rb") as rf:
                            st.download_button(
                                "⬇️ Télécharger rapport",
                                data=rf.read(),
                                file_name="drift_report.html",
                                mime="text/html"
                            )

        with col_b:
            if st.button("🔄 Forcer re-entraînement", use_container_width=True):
                with st.spinner("Déclenchement Kaggle..."):
                    ok = retrainer.trigger_retrain(reason="force_manuel_dashboard")
                if ok:
                    st.success("✅ Re-entraînement déclenché sur Kaggle !")
                    st.info("Notebook en cours sur Kaggle GPU T4. ~30 min.")
                else:
                    st.error("❌ Erreur déclenchement — vérifie la connexion.")

        with col_c:
            if st.button("📋 Historique re-entraînements", use_container_width=True):
                history = retrainer.get_retrain_history()
                if history["runs"]:
                    df_hist = pd.DataFrame(history["runs"])
                    st.dataframe(df_hist, use_container_width=True, hide_index=True)
                else:
                    st.info("Aucun re-entraînement effectué.")

        st.markdown("---")
        section_title("Drift actuel — Distance de Wasserstein", "◈")

        if summary and summary.get("drift_results"):
            dr = summary["drift_results"]
            df_drift_tab = pd.DataFrame([{
                "Feature":            feat,
                "Score Wasserstein":  res["score"],
                "Drift":              "⚠️ Détecté" if res["drift"] else "✅ Stable",
                "Critique":           "🔴 OUI"      if res["critical"] else "NON",
            } for feat, res in dr.items()])

            st.dataframe(
                df_drift_tab.style.set_properties(
                    **{"font-family":"JetBrains Mono","font-size":"12px"}
                ),
                use_container_width=True, hide_index=True
            )

            colors_bar_tab = [
                "#ef4444" if dr[f]["critical"] else
                "#f59e0b" if dr[f]["drift"]    else "#10b981"
                for f in dr
            ]
            fig_mon = go.Figure(go.Bar(
                x=list(dr.keys()),
                y=[dr[f]["score"] for f in dr],
                marker=dict(color=colors_bar_tab, opacity=0.85),
                text=[f"{dr[f]['score']:.3f}" for f in dr],
                textposition="outside",
            ))
            fig_mon.add_hline(y=0.5, line_dash="dash", line_color="#60a5fa",
                              annotation_text="Seuil drift (0.5)")
            fig_mon.add_hline(y=1.0, line_dash="dash", line_color="#ef4444",
                              annotation_text="Seuil critique (1.0)")
            fig_mon.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8fa8c8", family="JetBrains Mono"),
                margin=dict(t=40, b=20, l=10, r=10), height=320,
                yaxis=dict(gridcolor="#1a2d45",
                           title="Distance de Wasserstein normalisée"),
            )
            st.plotly_chart(fig_mon, use_container_width=True)

        st.markdown("---")
        section_title("Évolution temporelle du drift", "◈")
        trend_df = monitor.get_drift_trend()
        if not trend_df.empty:
            fig_trend = go.Figure()
            for feat in trend_df["feature"].unique():
                fdf = trend_df[trend_df["feature"] == feat]
                fig_trend.add_trace(go.Scatter(
                    x=fdf["timestamp"], y=fdf["score"],
                    mode="lines+markers", name=feat,
                ))
            fig_trend.add_hline(y=0.5, line_dash="dash", line_color="#60a5fa",
                                annotation_text="Seuil drift")
            fig_trend.add_hline(y=1.0, line_dash="dash", line_color="#ef4444",
                                annotation_text="Seuil critique")
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#8fa8c8", family="JetBrains Mono"),
                margin=dict(t=30, b=20, l=10, r=10), height=300,
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Lance plusieurs checks pour voir l'évolution temporelle du drift.")

        st.markdown("---")
        section_title("Recommandations de recalibrage", "◈")
        rec_df_tab = pd.DataFrame([
            {"Modèle":"DBSCAN","Wasserstein":"1.510",
             "Action":"Recalibrage prioritaire","Fréquence":"Tous les 3 mois"},
            {"Modèle":"IF",    "Wasserstein":"1.320",
             "Action":"Recalibrage prioritaire","Fréquence":"Tous les 3 mois"},
            {"Modèle":"LSTM",  "Wasserstein":"0.705",
             "Action":"Surveillance active",    "Fréquence":"Tous les 6 mois"},
            {"Modèle":"AE",    "Wasserstein":"0.445",
             "Action":"Surveillance passive",   "Fréquence":"Tous les 6 mois"},
        ])
        st.dataframe(
            rec_df_tab.style.set_properties(
                **{"font-family":"JetBrains Mono","font-size":"12px"}
            ),
            use_container_width=True, hide_index=True
        )

        st.markdown("---")
        section_title("Rapport Evidently complet", "◈")
        import os as _os
        if _os.path.exists("drift_report_train_vs_test.html"):
            with open("drift_report_train_vs_test.html", "rb") as f:
                st.download_button(
                    "⬇️ Télécharger rapport Evidently",
                    data=f.read(),
                    file_name="drift_report_train_vs_test.html",
                    mime="text/html",
                )
            st.markdown("""
            <div class="alert-box-success">
                ✅ Rapport HTML disponible.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-box-warning">
                ⚠️ Lance d'abord : <code>python generate_drift.py</code>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Module retrain_monitor.py non trouvé dans le dossier dashboard.")
        st.code("# Place retrain_monitor.py dans le même dossier que dashboard_mlflow.py", language="bash")

# ══════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════
st.markdown("---")
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center;
            font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#2d4a6e;
            padding:8px 0;">
    <span>CyberWatch v2.0 — Pipeline IF · AE · LSTM-AE · DBSCAN</span>
    <span>PFE 2025-2026 · Ibtissem Tounsi · ENSI / Université Laval</span>
</div>
""", unsafe_allow_html=True)

# ── SHAP patch (ajouté séparément)