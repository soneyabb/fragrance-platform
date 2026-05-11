"""
01_ingredient_explorer.py
--------------------------
향료 원료 탐색기 페이지
디자인: Option D (Warm Slate) + Plus Jakarta Sans
"""

import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(
    page_title="Ingredient Explorer",
    page_icon="🔍",
    layout="wide"
)

# ── 전역 CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* 카드 컨테이너 */
.ing-card {
    background: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 16px;
    padding: 1.4rem;
    margin-bottom: 1rem;
}

/* 원료명 */
.ing-name {
    font-size: 26px;
    font-weight: 700;
    color: #1e2022;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 4px;
}

/* 학명 */
.ing-sci {
    font-size: 12px;
    font-weight: 300;
    color: #6b7280;
    font-style: italic;
    margin-bottom: 0.9rem;
}

/* 별점 */
.star-row {
    display: flex;
    gap: 2px;
    margin-bottom: 2px;
    justify-content: flex-end;
}
.star-filled { color: #6b7280; font-size: 13px; }
.star-empty  { color: #e2ddd6; font-size: 13px; }
.pref-label  {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b7280;
    text-align: right;
}

/* 칩 */
.chip-row { display: flex; flex-wrap: wrap; gap: 5px; margin-bottom: 0.9rem; }
.chip {
    font-size: 11px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 100px;
    border: 1px solid;
    display: inline-block;
}
.chip-family { background:#fef3e2; color:#92400e; border-color:#fcd9a0; }
.chip-note   { background:#ecfdf5; color:#065f46; border-color:#a7f3d0; }
.chip-role   { background:#eff6ff; color:#1e40af; border-color:#bfdbfe; }

/* 소제목 */
.slbl {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a5260;
    margin-bottom: 7px;
    margin-top: 1rem;
}

/* 태그 */
.otag {
    display: inline-block;
    background: #f7f6f3;
    border: 1px solid #e2ddd6;
    color: #4a4e54;
    font-size: 11px;
    padding: 3px 9px;
    border-radius: 100px;
    margin: 2px 2px;
}

/* 박스 */
.sbox {
    background: #f7f6f3;
    border-radius: 9px;
    padding: 0.75rem 0.9rem;
    margin-bottom: 0.5rem;
    font-size: 12px;
    color: #4a4e54;
    line-height: 1.65;
}

/* 2컬럼 박스 */
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 0.7rem;
}
.col-box {
    background: #f7f6f3;
    border-radius: 9px;
    padding: 0.8rem 0.9rem;
}
.col-ttl {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4a5260;
    margin-bottom: 6px;
}
.col-tx { font-size: 12px; color: #4a4e54; line-height: 1.65; }

/* 인용 박스 */
.qt-box {
    background: #1e2022;
    border-radius: 11px;
    padding: 0.9rem 1rem;
    margin-top: 0.5rem;
}
.qt-text {
    font-size: 12px;
    color: #f0ece6;
    line-height: 1.75;
    font-weight: 300;
}
.qt-attr {
    font-size: 9px;
    color: #6b7280;
    margin-top: 5px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 500;
}

/* 화학식 4칸 */
.chem4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 5px; margin-bottom: 0.7rem; }
.ccard { background: #f7f6f3; border-radius: 9px; padding: 8px 6px; text-align: center; }
.cval  { font-size: 12px; font-weight: 600; color: #1e2022; }
.ckey  { font-size: 8px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #4a5260; margin-top: 3px; }

/* 컴포넌트 박스 */
.comp-box { background: #f7f6f3; border-radius: 9px; padding: 0.75rem 0.9rem; margin-bottom: 0.5rem; }
.comp-m   { font-size: 12px; font-weight: 600; color: #1e2022; margin-bottom: 3px; }
.comp-s   { font-size: 11px; color: #4a4e54; line-height: 1.55; }

/* 산업 바 */
.bar-row  { margin-bottom: 7px; }
.bar-top  { display: flex; justify-content: space-between; font-size: 11px; font-weight: 500; color: #4a4e54; margin-bottom: 3px; }
.bar-desc { font-size: 10px; color: #6b7280; }
.bar-bg   { background: #e2ddd6; border-radius: 100px; height: 4px; }
.bar-fill { background: #1e2022; border-radius: 100px; height: 4px; }

/* 링크 */
.lnk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-bottom: 0.9rem; }
.lnk {
    display: flex; align-items: center; gap: 7px;
    background: #f7f6f3; border: 1px solid #e2ddd6;
    border-radius: 8px; padding: 7px 10px;
    text-decoration: none;
}
.lnk-t { font-size: 11px; font-weight: 600; color: #1e2022; }
.lnk-s { font-size: 10px; color: #6b7280; }

/* 트렌드 카드 */
.trend-card {
    border-left: 2px solid #1e2022;
    padding: 7px 11px;
    margin-bottom: 5px;
    background: #f7f6f3;
    border-radius: 0 8px 8px 0;
}
.trend-m  { font-size: 9px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4a5260; margin-bottom: 3px; }
.trend-tx { font-size: 11px; color: #4a4e54; line-height: 1.6; }

/* API 안내 박스 */
.api-box {
    background: #f7f6f3; border-radius: 9px;
    padding: 0.75rem 0.9rem;
    font-size: 11px; color: #4a4e54; line-height: 1.65;
    margin-top: 0.6rem;
}

/* 사이드바 */
[data-testid="stSidebar"] { background: #faf9f6; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        st.error("❌ DB 파일 없음. `python processors/load_to_db.py` 먼저 실행하세요.")
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ingredients", conn)
    conn.close()
    return df


# ── 헬퍼 함수 ────────────────────────────────────────────────────────────────
FAMILY_EMOJI = {
    "Citrus":"🍊","Fruity":"🍑","Green":"🌱","Herbal":"🌿","Floral":"💐",
    "Aldehyde":"🧼","Animal":"🐾","Woody":"🪵","Mossy":"🌾",
    "Spicy":"🌶️","Balsamic":"🍯",
}

NOTE_CHIP = {
    "top":    ("Top Note",    "chip-note"),
    "middle": ("Middle Note", "chip-note"),
    "base":   ("Base Note",   "chip-note"),
}

INDUSTRY_INFO = {
    "perfume":        ("Perfume",       "핵심 top/middle/base 원료"),
    "cosmetic":       ("Cosmetic",      "스킨케어·헤어케어 향료"),
    "food":           ("Food & Beverage","마카롱·캔디·음료 착향"),
    "tea_coffee":     ("Tea & Coffee",  "Earl Grey 등 차·커피 착향"),
    "home_scent":     ("Home Scent",    "캔들·디퓨저·방향제"),
    "fabric":         ("Fabric",        "섬유유연제·세탁향료"),
    "pharmaceutical": ("Pharma",        "의약품 향료·진정 효과"),
}

INDUSTRY_BAR = {
    "perfume":95, "cosmetic":80, "food":60,
    "tea_coffee":70, "home_scent":65, "fabric":40, "pharmaceutical":50,
}

def render_stars(score):
    try:
        s = int(float(score))
    except Exception:
        s = 0
    filled = "".join(['<span class="star-filled">★</span>'] * min(s, 5))
    empty  = "".join(['<span class="star-empty">★</span>']  * (5 - min(s, 5)))
    return f'<div class="star-row">{filled}{empty}</div><div class="pref-label">Preference</div>'


def render_chips(family, volatility, role):
    emoji  = FAMILY_EMOJI.get(family, "⚗️")
    chips  = f'<span class="chip chip-family">{emoji} {family} Family</span> ' if family and family != "N/A" else ""

    vol = str(volatility).lower().strip()
    if vol in NOTE_CHIP:
        label, cls = NOTE_CHIP[vol]
        chips += f'<span class="chip {cls}">{label}</span> '

    if role and role not in ("N/A", "nan", ""):
        chips += f'<span class="chip chip-role">{role}</span>'

    return f'<div class="chip-row">{chips}</div>'


def render_odor_tags(descriptors: str) -> str:
    tags = [
        d.strip() for d in str(descriptors).split(",")
        if d.strip() and d.strip() not in ("N/A", "image", "nan", "vs", "")
    ]
    return "".join([f'<span class="otag">{t}</span>' for t in tags])


def safe(val) -> str:
    v = str(val).strip()
    return v if v not in ("N/A", "nan", ":", "") else "—"


# ── 사이드바 필터 ─────────────────────────────────────────────────────────────
def sidebar_filters(df):
    st.sidebar.markdown("### 🔍 Filter")
    query = st.sidebar.text_input("원료명 검색", "")

    vol_opts = ["All"] + sorted([
        v for v in df["volatility_class"].dropna().unique()
        if v not in ("N/A", "nan")
    ])
    vol = st.sidebar.selectbox("Volatility Class", vol_opts)

    fam_raw = sorted([
        f for f in df["odor_family"].dropna().unique()
        if f not in ("N/A", "nan")
    ])
    fam_opts = ["All"] + [f"{FAMILY_EMOJI.get(f,'⚗️')} {f}" for f in fam_raw]
    fam_sel  = st.sidebar.selectbox("Odor Family", fam_opts)
    fam      = fam_sel.split(" ", 1)[1] if fam_sel != "All" else "All"

    ind_opts = ["All"] + list(INDUSTRY_INFO.keys())
    ind      = st.sidebar.selectbox("Industry", ind_opts)

    return query, vol, fam, ind


def apply_filters(df, query, vol, fam, ind):
    if query:
        df = df[df["name"].str.contains(query, case=False, na=False)]
    if vol != "All":
        df = df[df["volatility_class"] == vol]
    if fam != "All":
        df = df[df["odor_family"] == fam]
    if ind != "All":
        df = df[df["industry_usage"].str.contains(ind, na=False)]
    return df


# ── 탭별 렌더 ────────────────────────────────────────────────────────────────
def tab_overview(ing):
    st.markdown('<div class="slbl">Odor Profile</div>', unsafe_allow_html=True)
    tags = render_odor_tags(ing.get("odor_descriptors", ""))
    obj  = safe(ing.get("objective_description", ""))
    st.markdown(f'<div style="margin-bottom:8px;">{tags}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sbox">{obj}</div>', unsafe_allow_html=True)

    # Sensory Summary (sensory_notes 첫 줄)
    notes_raw = str(ing.get("sensory_notes", "")).split("|")
    first_note = notes_raw[0].strip() if notes_raw else "—"
    st.markdown('<div class="slbl">Sensory Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sbox">{first_note}</div>', unsafe_allow_html=True)

    # At a Glance 4칸
    st.markdown('<div class="slbl">At a Glance</div>', unsafe_allow_html=True)
    origin  = safe(ing.get("origin_country", ""))
    method  = safe(ing.get("extraction_method", ""))
    comp    = safe(ing.get("main_components", "")).split(",")[0].strip()
    usages  = [u.strip() for u in str(ing.get("industry_usage","")).split(",") if u.strip() not in ("N/A","perfume","")]
    top_ind = " · ".join(usages[:2]) if usages else "—"

    st.markdown(f"""
    <div class="chem4">
      <div class="ccard"><div class="cval">{origin}</div><div class="ckey">Origin</div></div>
      <div class="ccard"><div class="cval">{method}</div><div class="ckey">Extraction</div></div>
      <div class="ccard"><div class="cval">{comp}</div><div class="ckey">Key Component</div></div>
      <div class="ccard"><div class="cval">{top_ind}</div><div class="ckey">Top Industries</div></div>
    </div>
    """, unsafe_allow_html=True)


def tab_sensory(ing):
    obj_desc  = safe(ing.get("objective_description", ""))
    subj_desc = safe(ing.get("subjective_description", ""))

    st.markdown(f"""
    <div class="two-col">
      <div class="col-box">
        <div class="col-ttl">Professional (EN)</div>
        <div class="col-tx">{obj_desc}</div>
      </div>
      <div class="col-box">
        <div class="col-ttl">Personal Memory (KR)</div>
        <div class="col-tx">{subj_desc}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Detailed Notes
    notes_raw = str(ing.get("sensory_notes", ""))
    if notes_raw and notes_raw not in ("N/A", "nan"):
        st.markdown('<div class="slbl">Detailed Notes</div>', unsafe_allow_html=True)
        for note in notes_raw.split("|"):
            n = note.strip()
            if n:
                st.markdown(f'<div class="sbox">{n}</div>', unsafe_allow_html=True)

    # Comparison Notes (있을 때만)
    comp_notes = str(ing.get("comparison_notes", "")).strip()
    if comp_notes and comp_notes not in ("N/A", "nan", ""):
        st.markdown('<div class="slbl">Comparison Notes</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sbox">{comp_notes}</div>', unsafe_allow_html=True)

    # Personal Quote
    raw_notes = str(ing.get("sensory_notes", "")).split("|")
    full_quote = " | ".join([n.strip() for n in raw_notes if n.strip()])
    if full_quote and full_quote != "N/A":
        st.markdown(f"""
        <div class="qt-box">
          <div class="qt-text">"{full_quote}"</div>
          <div class="qt-attr">Personal Sensory Memory — unedited</div>
        </div>
        """, unsafe_allow_html=True)


def tab_chemistry(ing):
    cid     = safe(ing.get("pubchem_cid", ""))
    cas     = safe(ing.get("cas_number", ""))
    formula = safe(ing.get("molecular_formula", ""))
    weight  = safe(ing.get("molecular_weight", ""))

    st.markdown('<div class="slbl">Chemical Identity</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chem4">
      <div class="ccard"><div class="cval">{formula}</div><div class="ckey">Formula</div></div>
      <div class="ccard"><div class="cval">{weight}</div><div class="ckey">MW g/mol</div></div>
      <div class="ccard"><div class="cval">{cid}</div><div class="ckey">PubChem CID</div></div>
      <div class="ccard"><div class="cval">{cas}</div><div class="ckey">CAS No.</div></div>
    </div>
    """, unsafe_allow_html=True)

    # PubChem 구조식 이미지
    if cid and cid != "—":
        st.markdown('<div class="slbl">Chemical Structure</div>', unsafe_allow_html=True)
        img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        st.image(img_url, width=250, caption=f"PubChem CID {cid}")

    # 주요 성분
    components = safe(ing.get("main_components", ""))
    if components != "—":
        st.markdown('<div class="slbl">Key Components</div>', unsafe_allow_html=True)
        for comp in components.split(","):
            c = comp.strip()
            if c:
                st.markdown(f'<div class="comp-box"><div class="comp-m">{c}</div></div>', unsafe_allow_html=True)

    # IFRA / 안전 정보 (pharmaceutical 포함 원료에만)
    industry = str(ing.get("industry_usage", ""))
    if "pharmaceutical" in industry or "cosmetic" in industry:
        st.markdown('<div class="slbl">Safety & Regulation</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="comp-box">
          <div class="comp-m">IFRA 규정 준수 필요</div>
          <div class="comp-s">피부 도포용 제품 사용 시 IFRA 농도 기준 확인 필요.
          <a href="https://www.ifrafragrance.org" target="_blank" style="color:#1e2022;">ifrafragrance.org →</a></div>
        </div>
        """, unsafe_allow_html=True)

    # pubchem_note (수집 메모)
    note = safe(ing.get("pubchem_note", ""))
    if note != "—":
        st.caption(f"📌 수집 메모: {note}")


def tab_industry(ing):
    usages = [u.strip() for u in str(ing.get("industry_usage","")).split(",") if u.strip() not in ("N/A","nan","")]
    name   = ing.get("name", "")

    st.markdown('<div class="slbl">Usage by Sector</div>', unsafe_allow_html=True)
    bars_html = ""
    for u in usages:
        if u in INDUSTRY_INFO:
            label, desc = INDUSTRY_INFO[u]
            pct = INDUSTRY_BAR.get(u, 50)
            bars_html += f"""
            <div class="bar-row">
              <div class="bar-top"><span>{label}</span><span class="bar-desc">{desc}</span></div>
              <div class="bar-bg"><div class="bar-fill" style="width:{pct}%"></div></div>
            </div>"""
    st.markdown(bars_html, unsafe_allow_html=True)

    # 링크
    st.markdown('<div class="slbl" style="margin-top:1rem;">Explore Products</div>', unsafe_allow_html=True)
    frag_url = f"https://www.fragrantica.com/search/?query={name.replace(' ', '+')}"
    gsc_url  = f"https://www.thegoodscentscompany.com/search3.php?qName={name.replace(' ', '+')}&submit=Search"
    st.markdown(f"""
    <div class="lnk-grid">
      <a class="lnk" href="{frag_url}" target="_blank">
        <div><div class="lnk-t">Fragrantica</div><div class="lnk-s">향수 전체 DB</div></div>
      </a>
      <a class="lnk" href="{gsc_url}" target="_blank">
        <div><div class="lnk-t">Good Scents Co.</div><div class="lnk-s">식품·차·코스메틱</div></div>
      </a>
    </div>
    """, unsafe_allow_html=True)

    # 트렌드 (정적 + API 예정 안내)
    st.markdown('<div class="slbl">Latest Trends <span style="font-weight:400;font-size:9px;color:#9098a0;">— 최근 3년 이내</span></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="trend-card"><div class="trend-m">2024 Q4 (Oct–Dec)</div>
    <div class="trend-tx">글로벌 니치 퍼퓨머리 시장 확대 — 천연 원료 수요 YoY +15% 상승.</div></div>
    <div class="trend-card"><div class="trend-m">2023 Q2 (Apr–Jun)</div>
    <div class="trend-tx">Clean Beauty 트렌드 확산 — 합성 향료 대비 천연 원료 선호도 증가.</div></div>
    <div class="api-box"><strong style="color:#1e2022;">API 연동 후:</strong>
    Google Trends 12개월 그래프 · News API 기사 자동 파싱 · 1시간 캐시 갱신</div>
    """, unsafe_allow_html=True)


# ── 메인 ─────────────────────────────────────────────────────────────────────
def main():
    st.title("🔍 Ingredient Explorer")
    st.markdown("---")

    df = load_data()
    if df.empty:
        return

    query, vol, fam, ind = sidebar_filters(df)
    filtered = apply_filters(df, query, vol, fam, ind)

    col_list, col_detail = st.columns([1, 2], gap="large")

    with col_list:
        st.markdown(f"**{len(filtered)}개 원료**")
        if filtered.empty:
            st.info("검색 결과가 없습니다.")
            return
        selected_name = st.selectbox(
            "원료 선택",
            filtered["name"].tolist(),
            label_visibility="collapsed"
        )

    if not selected_name:
        return

    ing = df[df["name"] == selected_name].iloc[0].to_dict()

    with col_detail:
        # 헤더
        family     = safe(ing.get("odor_family", ""))
        volatility = safe(ing.get("volatility_class", ""))
        role       = safe(ing.get("role", ""))
        sci        = safe(ing.get("scientific_name", ""))
        score      = ing.get("preference_score", 0)

        header_html = f"""
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.3rem;">
          <div>
            <div class="ing-name">{selected_name}</div>
            <div class="ing-sci">{sci}</div>
          </div>
          <div>{render_stars(score)}</div>
        </div>
        {render_chips(family, volatility, role)}
        """
        st.markdown(header_html, unsafe_allow_html=True)

        # 탭
        t_ov, t_se, t_ch, t_in = st.tabs(["Overview", "Sensory", "Chemistry", "Industry"])

        with t_ov: tab_overview(ing)
        with t_se: tab_sensory(ing)
        with t_ch: tab_chemistry(ing)
        with t_in: tab_industry(ing)

    # Raw Data
    with st.expander("Raw Data", expanded=False):
        st.dataframe(filtered, use_container_width=True)


if __name__ == "__main__":
    main()
