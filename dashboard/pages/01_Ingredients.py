"""
01_Ingredients.py
-----------------
Sillage — Ingredient Intelligence
5탭 구조: Material | Sensory | Usage | Occurrence | Intelligence
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import re

st.set_page_config(
    page_title="Ingredients — Sillage",
    page_icon="◈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display&display=swap');

:root {
    --ink:    #1a1a18;
    --paper:  #faf9f7;
    --muted:  #6b6860;
    --rule:   #e4e0d8;
    --active: #2d6a4f;
    --gold:   #b5935a;
    --warn:   #92400e;
    --danger: #991b1b;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}

[data-testid="stSidebar"] { background-color: var(--ink) !important; }
[data-testid="stSidebarNav"] span {
    color: #c8c4bc !important;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.pg-eyebrow {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.4rem;
}
.pg-title {
    font-family: 'DM Serif Display', serif;
    font-size: 40px;
    color: var(--ink);
    margin-bottom: 0.3rem;
    line-height: 1;
}
.pg-sub {
    font-size: 14px;
    color: var(--muted);
    margin-bottom: 2rem;
}

.filter-rule {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 1.2rem 0 1.5rem 0;
}

.ing-header {
    padding: 1.8rem 0 1.2rem 0;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 1.5rem;
}
.ing-name {
    font-family: 'DM Serif Display', serif;
    font-size: 44px;
    color: var(--ink);
    line-height: 1;
    margin-bottom: 6px;
}
.ing-sci {
    font-size: 16px;
    color: var(--muted);
    font-style: italic;
    margin-bottom: 1rem;
}

.badge-wrap { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 1rem; }
.badge {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 2px;
    border: 1px solid;
}
.badge-curated   { color: var(--active); border-color: var(--active); background: #f0faf5; }
.badge-mapped    { color: var(--gold);   border-color: var(--gold);   background: #fdf8f0; }
.badge-registered{ color: var(--muted); border-color: var(--rule);   background: white; }
.badge-meta { font-size: 12px; color: var(--muted); }

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem; }
.chip {
    font-size: 12px;
    font-weight: 500;
    padding: 5px 14px;
    border-radius: 2px;
    border: 1px solid var(--rule);
    background: white;
    color: var(--ink);
    letter-spacing: 0.03em;
}
.chip-family { background: #fef3e2; border-color: #fcd9a0; color: #92400e; }
.chip-note   { background: #f0faf5; border-color: #a7f3d0; color: #065f46; }
.chip-role   { background: #eff6ff; border-color: #bfdbfe; color: #1e40af; }

.star-row { display: flex; gap: 3px; }
.star-filled { color: var(--gold); font-size: 18px; }
.star-empty  { color: var(--rule); font-size: 18px; }
.pref-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 4px;
}

.sec-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.8rem;
    margin-top: 2rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--rule);
}

.data-box {
    background: white;
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    font-size: 14px;
    color: #3a3a36;
    line-height: 1.85;
}

.grid4 {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    margin-bottom: 1.5rem;
}
.gcell {
    background: white;
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
}
.gcell-val {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: var(--ink);
    margin-bottom: 4px;
    line-height: 1.2;
}
.gcell-key {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

.otag {
    display: inline-block;
    font-size: 12px;
    padding: 4px 12px;
    border: 1px solid var(--rule);
    border-radius: 2px;
    margin: 3px 3px;
    background: white;
    color: var(--ink);
}

.quote-box {
    background: var(--ink);
    border-radius: 3px;
    padding: 1.8rem 2rem;
    margin-top: 1.5rem;
}
.quote-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b6860;
    margin-bottom: 0.8rem;
}
.quote-sub {
    font-size: 12px;
    color: #6b6860;
    margin-top: 0.6rem;
}
.quote-text {
    font-size: 15px;
    color: #f0ece6;
    line-height: 1.9;
    font-weight: 300;
}

.ifra-compliant  { color: var(--active); font-weight: 600; }
.ifra-restricted { color: var(--warn);   font-weight: 600; }
.ifra-prohibited { color: var(--danger); font-weight: 600; }

.reg-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 1rem; }
.reg-table th {
    text-align: left;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    padding: 6px 12px;
    border-bottom: 1px solid var(--rule);
}
.reg-table td {
    padding: 8px 12px;
    border-bottom: 1px solid var(--rule);
    color: var(--ink);
}
.reg-table tr:last-child td { border-bottom: none; }

.ind-bar-wrap { margin-bottom: 1rem; }
.ind-bar-head {
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    margin-bottom: 5px;
}
.ind-bar-name { font-weight: 500; color: var(--ink); }
.ind-bar-note { color: var(--muted); font-size: 12px; }
.ind-bar-bg   { background: var(--rule); height: 4px; border-radius: 2px; }
.ind-bar-fill { height: 4px; border-radius: 2px; }

.pair-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--rule);
    font-size: 13px;
}
.pair-rank { color: var(--muted); min-width: 24px; }
.pair-name { font-weight: 500; color: var(--ink); }
.pair-count { color: var(--muted); font-size: 12px; }

.occ-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    margin-bottom: 1.5rem;
}
.occ-cell { background: white; padding: 1.2rem 1.5rem; }
.occ-val {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: var(--ink);
    margin-bottom: 4px;
}
.occ-key {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

.pos-row { margin-bottom: 0.8rem; }
.pos-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    margin-bottom: 4px;
    color: var(--ink);
}
.pos-pct { color: var(--muted); }

.intel-placeholder {
    background: white;
    border: 1px solid var(--rule);
    border-left: 3px solid var(--gold);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    font-size: 13px;
    color: var(--muted);
    border-radius: 0 3px 3px 0;
}

.empty-state {
    font-size: 13px;
    color: var(--muted);
    padding: 1.2rem 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    margin-bottom: 1rem;
}

.prov-row {
    display: flex;
    gap: 8px;
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 4px;
}
.prov-key { min-width: 140px; font-weight: 500; color: var(--ink); }

.stTabs [data-baseweb="tab"] p {
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 상수 — 원본 스크린샷 기준 이모지 확정
# ─────────────────────────────────────────
FAMILY_EMOJI = {
    "Citrus":   "🍊",
    "Fruity":   "🥭",
    "Green":    "🌱",
    "Herbal":   "🌿",
    "Floral":   "🌸",
    "Aldehyde": "🧼",
    "Animal":   "🐾",
    "Woody":    "🪵",
    "Mossy":    "🪨",
    "Spicy":    "🫚",
    "Balsamic": "🍯",
}

# 원본 스키마 키 — 화면 레이블 분리
# 업계 표준 용어 기준
INDUSTRY_LABEL = {
    "perfume":        "Fine Fragrance",
    "cosmetic":       "Cosmetic",
    "food":           "Food",
    "tea_coffee":     "Tea & Coffee",
    "home_scent":     "Home Scent",
    "fabric":         "Fabric Care",
    "pharmaceutical": "Pharmaceutical",
}

# IFRA, COMMON_PAIRINGS — 파이프라인 완성 후 DB에서 읽음
# 지금은 구조만 확정, 수치 없음


# ─────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        st.error("DB 파일 없음. processors/load_to_db.py 먼저 실행하세요.")
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ingredients", conn)
    conn.close()
    return df


# ─────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────
def safe(val) -> str:
    v = str(val).strip()
    return v if v not in ("N/A", "nan", ":", "", "None") else "—"

def format_formula(formula: str) -> str:
    if not formula or formula in ("N/A", "nan", "—", ""):
        return "—"
    return re.sub(r'(\d+)', r'<sub>\1</sub>', str(formula))

def render_stars(score):
    try:
        s = int(float(score))
    except Exception:
        s = 0
    filled = "".join(['<span class="star-filled">★</span>'] * min(s, 5))
    empty  = "".join(['<span class="star-empty">★</span>'] * (5 - min(s, 5)))
    return f'<div class="star-row">{filled}{empty}</div><div class="pref-label">Preference</div>'

def render_odor_tags(descriptors: str) -> str:
    tags = []
    for d in str(descriptors).split(","):
        t = d.strip()
        if not t or t.lower() in ("n/a", "image", "nan", "vs", "none", ""):
            continue
        if re.search('[가-힣]', t):
            continue
        tags.append(t)
    return "".join([f'<span class="otag">{t}</span>' for t in tags])

def get_quality_tier(ing: dict) -> str:
    src = str(ing.get("data_source", "")).lower()
    if "notion_manual" in src or "user" in src:
        return "curated"
    elif "pubchem" in src or "pyrfume" in src:
        return "mapped"
    else:
        return "registered"

def render_badge(tier: str) -> str:
    labels = {
        "curated":    ("★★★ Curated",    "badge-curated"),
        "mapped":     ("★★☆ Mapped",     "badge-mapped"),
        "registered": ("★☆☆ Registered", "badge-registered"),
    }
    text, cls = labels.get(tier, ("★☆☆ Registered", "badge-registered"))
    return f'<span class="badge {cls}">{text}</span>'


# ─────────────────────────────────────────
# 필터
# ─────────────────────────────────────────
def render_filters(df):
    c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 1])
    with c1:
        query = st.text_input("", placeholder="Search ingredients...",
                              label_visibility="collapsed")
    with c2:
        vol_opts = ["All Volatility"] + sorted([
            v.capitalize() for v in df["volatility_class"].dropna().unique()
            if v not in ("N/A", "nan")
        ])
        vol = st.selectbox("", vol_opts, label_visibility="collapsed")
    with c3:
        fam_raw  = sorted([f for f in df["odor_family"].dropna().unique()
                           if f not in ("N/A", "nan")])
        fam_opts = ["All Families"] + fam_raw
        fam_sel  = st.selectbox("", fam_opts, label_visibility="collapsed")
        fam      = fam_sel if fam_sel != "All Families" else "All"
    with c4:
        # IFRA 필터 — 파이프라인 완성 후 DB 연동
        # 지금은 All만 동작, 나머지는 placeholder
        ifra_opts = ["All IFRA", "Compliant", "Restricted", "Prohibited"]
        ifra_sel  = st.selectbox("", ifra_opts, label_visibility="collapsed")
    with c5:
        curated_only = st.toggle("Curated only", value=False)

    return query, vol, fam, ifra_sel, curated_only


def apply_filters(df, query, vol, fam, ifra_sel, curated_only):
    if query:
        df = df[df["name"].str.contains(query, case=False, na=False)]
    if vol not in ("All Volatility", "All"):
        df = df[df["volatility_class"] == vol.lower()]
    if fam != "All":
        df = df[df["odor_family"] == fam]
    if curated_only:
        df = df[df["data_source"].str.contains(
            "notion_manual|user", case=False, na=False)]
    return df


# ─────────────────────────────────────────
# 탭 1 — Material
# ─────────────────────────────────────────
def tab_material(ing):
    tier = get_quality_tier(ing)

    # IDENTIFICATION
    st.markdown('<div class="sec-label">Identification</div>',
                unsafe_allow_html=True)

    raw_cid = safe(ing.get("pubchem_cid", ""))
    try:
        cid = str(int(float(raw_cid))) if raw_cid != "—" else "—"
    except Exception:
        cid = raw_cid

    cas     = safe(ing.get("cas_number", ""))
    formula = safe(ing.get("molecular_formula", ""))
    weight  = safe(ing.get("molecular_weight", ""))

    st.markdown(f"""
    <div class="grid4">
        <div class="gcell">
            <div class="gcell-val">{format_formula(formula)}</div>
            <div class="gcell-key">Molecular Formula</div>
        </div>
        <div class="gcell">
            <div class="gcell-val">{weight}</div>
            <div class="gcell-key">MW (g/mol)</div>
        </div>
        <div class="gcell">
            <div class="gcell-val">{cid}</div>
            <div class="gcell-key">PubChem CID</div>
        </div>
        <div class="gcell">
            <div class="gcell-val">{cas}</div>
            <div class="gcell-key">CAS Number</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # PHYSICAL PROPERTIES
    # boiling point, logP, vapor pressure → PubChem 수집 후 자동 반영
    vol_class = safe(ing.get("volatility_class", ""))
    st.markdown('<div class="sec-label">Physical Properties</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="data-box">
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr>
                <td style="padding:6px 0;color:var(--muted);width:180px;">
                    Boiling Point</td>
                <td style="padding:6px 0;">—</td>
                <td style="padding:6px 0;color:var(--muted);font-size:12px;">
                    → {vol_class.capitalize() if vol_class != '—' else '—'} note
                </td>
            </tr>
            <tr>
                <td style="padding:6px 0;color:var(--muted);">logP</td>
                <td style="padding:6px 0;">—</td>
                <td style="padding:6px 0;color:var(--muted);font-size:12px;">
                    소수성 지표 — 높을수록 Base note 경향</td>
            </tr>
            <tr>
                <td style="padding:6px 0;color:var(--muted);">Vapor Pressure</td>
                <td style="padding:6px 0;">—</td>
                <td style="padding:6px 0;color:var(--muted);font-size:12px;">
                    낮을수록 잔향 오래 지속</td>
            </tr>
        </table>
        <div style="font-size:11px;color:var(--muted);margin-top:0.8rem;
                    border-top:1px solid var(--rule);padding-top:0.6rem;">
            PubChem 수집 파이프라인 완성 후 자동 반영
        </div>
    </div>
    """, unsafe_allow_html=True)

    # KEY COMPONENTS — CURATED만
    components = safe(ing.get("main_components", ""))
    if tier == "curated" and components != "—":
        st.markdown('<div class="sec-label">Key Components</div>',
                    unsafe_allow_html=True)
        html = '<div style="margin-bottom:1rem;">'
        for c in components.split(","):
            c = c.strip()
            if c:
                html += f'<span class="otag">{c}</span>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

    # CHEMICAL STRUCTURE — PubChem CID 있을 때만
    if cid and cid != "—":
        st.markdown('<div class="sec-label">Chemical Structure</div>',
                    unsafe_allow_html=True)
        img_url = (f"https://pubchem.ncbi.nlm.nih.gov"
                   f"/rest/pug/compound/cid/{cid}/PNG")
        col1, _ = st.columns([1, 3])
        with col1:
            st.image(img_url, caption=f"PubChem CID {cid}", width=240)

    # PROVENANCE
    st.markdown('<div class="sec-label">Provenance</div>',
                unsafe_allow_html=True)
    src = safe(ing.get("data_source", ""))
    curated_by = "user" if tier == "curated" else "imported"
    st.markdown(f"""
    <div class="data-box" style="font-size:12px;">
        <div class="prov-row">
            <span class="prov-key">source_system</span>
            <span>{src}</span>
        </div>
        <div class="prov-row">
            <span class="prov-key">mapping_method</span>
            <span>CAS / name match</span>
        </div>
        <div class="prov-row">
            <span class="prov-key">curated_by</span>
            <span>{curated_by}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 탭 2 — Sensory
# ─────────────────────────────────────────
def tab_sensory(ing):
    tier = get_quality_tier(ing)
    name = ing.get("name", "")

    if tier == "registered":
        st.markdown("""
        <div class="empty-state">
            이 원료의 감각 데이터는 아직 수집되지 않았습니다.<br>
            향후 CURATED 확장 시 추가됩니다.
        </div>
        """, unsafe_allow_html=True)
        return

    # ODOR DESCRIPTORS
    st.markdown('<div class="sec-label">Odor Descriptors</div>',
                unsafe_allow_html=True)
    tags_html  = render_odor_tags(ing.get("odor_descriptors", ""))
    src_label  = "user" if tier == "curated" else "Pyrfume / Leffingwell"
    st.markdown(f"""
    <div style="margin-bottom:0.5rem;">{tags_html}</div>
    <div style="font-size:11px;color:var(--muted);">
        descriptor_source: {src_label}
    </div>
    """, unsafe_allow_html=True)

    if tier == "mapped":
        st.markdown('<div class="sec-label">Personal Sensory Notes</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="empty-state">직접 기록된 감각 데이터가 없습니다.</div>
        """, unsafe_allow_html=True)
        return

    # CURATED 전용 ─────────────────────────

    # OBJECTIVE DESCRIPTION
    st.markdown('<div class="sec-label">Objective Description</div>',
                unsafe_allow_html=True)
    obj = safe(ing.get("objective_description", ""))
    st.markdown(f'<div class="data-box">{obj}</div>', unsafe_allow_html=True)

    # PERSONAL SENSORY NOTES + KR | EN 토글
    st.markdown('<div class="sec-label">Personal Sensory Notes</div>',
                unsafe_allow_html=True)
    lang = st.radio("", ["KR", "EN"], horizontal=True, key=f"lang_{name}")

    notes_raw = str(ing.get("sensory_notes", ""))
    paragraphs = [n.strip() for n in notes_raw.split("|")
                  if n.strip() and n.strip() not in ("N/A", "nan")]

    if lang == "KR":
        for p in paragraphs:
            st.markdown(f'<div class="data-box">{p}</div>',
                        unsafe_allow_html=True)
    else:
        # EN: sensory_notes_en 컬럼 추가 후 교체
        # 현재는 KR 원문 표시
        for p in paragraphs:
            st.markdown(f'<div class="data-box">{p}</div>',
                        unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:11px;color:var(--muted);margin-top:0.4rem;">
            ※ EN 번역 준비 중 — sensory_notes_en 컬럼 추가 후 자동 전환
        </div>
        """, unsafe_allow_html=True)

    # COMPARISON NOTES
    comp_notes = str(ing.get("comparison_notes", "")).strip()
    if comp_notes and comp_notes not in ("N/A", "nan", ""):
        st.markdown('<div class="sec-label">Comparison Notes</div>',
                    unsafe_allow_html=True)
        pairs = (comp_notes.split("||") if "||" in comp_notes
                 else [comp_notes])
        for pair in pairs:
            parts      = [p.strip() for p in pair.split("|") if p.strip()]
            desc_items = [p for p in parts if ":" in p]
            for desc in desc_items:
                nm, tx = desc.split(":", 1)
                st.markdown(f"""
                <div class="data-box">
                    <strong>{nm.strip()}</strong>: {tx.strip()}
                </div>
                """, unsafe_allow_html=True)

    # 원문 인용 박스
    full_quote = " | ".join(paragraphs)
    if full_quote:
        st.markdown(f"""
        <div class="quote-box">
            <div class="quote-label">Personal Sensory Record — Unedited</div>
            <div class="quote-text">{full_quote}</div>
            <div class="quote-sub">
                조향 훈련 과정에서 직접 기록한 1차 감각 데이터입니다
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 탭 3 — Usage
# ─────────────────────────────────────────
def tab_usage(ing):
    tier = get_quality_tier(ing)

    # IFRA REGULATION
    st.markdown('<div class="sec-label">IFRA Regulation</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="data-box">
        <div style="font-size:13px;color:var(--muted);margin-bottom:0.5rem;">
            IFRA Status
        </div>
        <div style="font-size:15px;margin-bottom:1rem;">—</div>
        <table class="reg-table">
            <thead>
                <tr>
                    <th>Product Category</th>
                    <th style="text-align:right;">Max Concentration</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>Fine Fragrance</td><td style="text-align:right;">—</td></tr>
                <tr><td>Skin Cream / Lotion</td><td style="text-align:right;">—</td></tr>
                <tr><td>Rinse-off Products</td><td style="text-align:right;">—</td></tr>
                <tr><td>Fabric Care</td><td style="text-align:right;">—</td></tr>
            </tbody>
        </table>
        <div style="font-size:11px;color:var(--muted);
                    border-top:1px solid var(--rule);padding-top:0.6rem;">
            Source: IFRA 51st Amendment (2023) —
            IFRA 수집 파이프라인 완성 후 자동 반영
        </div>
    </div>
    """, unsafe_allow_html=True)

    # INDUSTRY APPLICATION — CURATED만
    st.markdown('<div class="sec-label">Industry Application</div>',
                unsafe_allow_html=True)

    if tier != "curated":
        st.markdown("""
        <div class="empty-state">
            직접 조사 데이터 없음 — CURATED 원료만 제공됩니다.
        </div>
        """, unsafe_allow_html=True)
    else:
        usages      = [u.strip() for u in
                       str(ing.get("industry_usage", "")).split(",")
                       if u.strip() not in ("N/A", "nan", "")]
        all_ind     = list(INDUSTRY_LABEL.keys())

        for ind in all_ind:
            label = INDUSTRY_LABEL[ind]
            used  = ind in usages
            fill  = "100%" if used else "0%"
            color = "var(--ink)" if used else "var(--rule)"
            note  = "사용" if used else "미사용"
            st.markdown(f"""
            <div class="ind-bar-wrap">
                <div class="ind-bar-head">
                    <span class="ind-bar-name">{label}</span>
                    <span class="ind-bar-note">{note}</span>
                </div>
                <div class="ind-bar-bg">
                    <div class="ind-bar-fill"
                         style="width:{fill};background:{color};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
            데이터 출처: 직접 조사 기반
        </div>
        """, unsafe_allow_html=True)

    # COMMON PAIRINGS
    st.markdown('<div class="sec-label">Common Pairings</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="empty-state">
        Parfumo CSV 파이프라인 완성 후 자동 계산됩니다.<br>
        <span style="font-size:11px;">
            Source: Parfumo dataset (2024-12-10), non-commercial
        </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 탭 4 — Occurrence
# ─────────────────────────────────────────
def tab_occurrence(ing):
    st.markdown("""
    <div style="font-size:11px;color:var(--muted);margin-bottom:1.5rem;">
        Source: Parfumo dataset — 59,325 perfumes (collected 2024)
        · Consumer community data. Historical reference only.
    </div>
    """, unsafe_allow_html=True)

    # FREQUENCY SUMMARY
    st.markdown('<div class="sec-label">Frequency Summary</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="occ-grid">
        <div class="occ-cell">
            <div class="occ-val">—</div>
            <div class="occ-key">Total Appearances</div>
        </div>
        <div class="occ-cell">
            <div class="occ-val">—</div>
            <div class="occ-key">Global Rank</div>
        </div>
        <div class="occ-cell">
            <div class="occ-val">—</div>
            <div class="occ-key">Coverage</div>
        </div>
    </div>
    <div style="font-size:11px;color:var(--muted);margin-bottom:1.5rem;">
        Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.
    </div>
    """, unsafe_allow_html=True)

    # NOTE POSITION BREAKDOWN
    st.markdown('<div class="sec-label">Note Position Breakdown</div>',
                unsafe_allow_html=True)
    for label in ["Top note", "Middle note", "Base note"]:
        st.markdown(f"""
        <div class="pos-row">
            <div class="pos-label">
                <span>{label}</span>
                <span class="pos-pct">—</span>
            </div>
            <div class="ind-bar-bg">
                <div class="ind-bar-fill" style="width:0%;background:var(--rule);"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TOP PERFUMES
    st.markdown('<div class="sec-label">Top Perfumes Featuring This Ingredient</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="empty-state">
        Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.
    </div>
    """, unsafe_allow_html=True)

    # TOP BRANDS
    st.markdown('<div class="sec-label">Top Brands Using This Ingredient</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="empty-state">
        Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 탭 5 — Intelligence
# ─────────────────────────────────────────
def tab_intelligence(ing):
    name = ing.get("name", "")

    st.markdown('<div class="sec-label">Reddit Mentions — r/fragrance</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="intel-placeholder">
        Reddit PRAW API 연동 후 <strong>{name}</strong> 언급 글 실시간 표시<br>
        · 최근 30일 상위 5개 (제목 / 업보트 / 댓글 수 / 링크)<br>
        · 키워드 빈도 차트
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Industry News</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="intel-placeholder">
        Perfumer &amp; Flavorist RSS —
        <strong>{name} fragrance ingredient</strong> 관련 기사
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Academic Signal</div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div class="intel-placeholder">
        Semantic Scholar API —
        <strong>{name} fragrance</strong> 최신 논문
        (제목 / 출판연도 / DOI 링크)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;color:var(--muted);margin-top:1rem;">
        Intelligence 탭은 05_Intelligence.py 페이지와 연동됩니다.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Ingredient Intelligence</div>
    <div class="pg-title">Ingredients</div>
    <div class="pg-sub">
        원료별 화학 데이터, 감각 노트, 규제 현황, 시장 빈도를 한 화면에서 탐색합니다.
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        return

    st.markdown('<hr class="filter-rule">', unsafe_allow_html=True)
    query, vol, fam, ifra_sel, curated_only = render_filters(df)
    st.markdown('<hr class="filter-rule">', unsafe_allow_html=True)

    filtered = apply_filters(df, query, vol, fam, ifra_sel, curated_only)
    st.markdown(
        f'<div style="font-size:12px;color:var(--muted);margin-bottom:0.8rem;">'
        f'{len(filtered)}개 원료</div>',
        unsafe_allow_html=True
    )

    if filtered.empty:
        st.info("검색 결과가 없습니다.")
        return

    selected_name = st.selectbox(
        "", filtered["name"].tolist(), label_visibility="collapsed"
    )
    if not selected_name:
        return

    ing  = df[df["name"] == selected_name].iloc[0].to_dict()
    tier = get_quality_tier(ing)

    # 원료 헤더
    family     = safe(ing.get("odor_family", ""))
    volatility = safe(ing.get("volatility_class", ""))
    role       = safe(ing.get("role", ""))
    sci        = safe(ing.get("scientific_name", ""))
    score      = ing.get("preference_score", 0)
    emoji      = FAMILY_EMOJI.get(family, "")

    chip_fam  = (f'<span class="chip chip-family">{emoji} {family}</span>'
                 if family != "—" else "")
    chip_vol  = (f'<span class="chip chip-note">'
                 f'{volatility.capitalize()} Note</span>'
                 if volatility != "—" else "")
    chip_role = (f'<span class="chip chip-role">{role}</span>'
                 if role not in ("—", "") else "")

    st.markdown(f"""
    <div class="ing-header">
        <div style="display:flex;justify-content:space-between;
                    align-items:flex-start;">
            <div>
                <div class="ing-name">{selected_name}</div>
                <div class="ing-sci">{sci if sci != '—' else ''}</div>
                <div class="badge-wrap">
                    {render_badge(tier)}
                    <span class="badge-meta">
                        curated_by: {'user' if tier == 'curated' else 'imported'}
                    </span>
                </div>
                <div class="chip-row">{chip_fam}{chip_vol}{chip_role}</div>
            </div>
            <div style="text-align:right;">{render_stars(score)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 5탭
    t1, t2, t3, t4, t5 = st.tabs(
        ["Material", "Sensory", "Usage", "Occurrence", "Intelligence"]
    )
    with t1: tab_material(ing)
    with t2: tab_sensory(ing)
    with t3: tab_usage(ing)
    with t4: tab_occurrence(ing)
    with t5: tab_intelligence(ing)


if __name__ == "__main__":
    main()
