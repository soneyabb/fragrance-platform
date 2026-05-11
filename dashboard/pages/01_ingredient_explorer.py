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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
}

/* 타이틀 및 설명 */
.pg-title { font-size: 42px; font-weight: 800; color: #1e2022; margin-bottom: 0.5rem; letter-spacing: -0.03em; }
.pg-desc { color: #6b7280; margin-bottom: 2.5rem; font-size: 16px; }

/* 카드 컨테이너 */
.ing-card {
    background: #ffffff;
    border: 1px solid #e2ddd6;
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.03);
}

/* 원료명 */
.ing-name {
    font-size: 36px;
    font-weight: 800;
    color: #1e2022;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 8px;
}

/* 학명 */
.ing-sci {
    font-size: 18px;
    font-weight: 400;
    color: #6b7280;
    font-style: italic;
    margin-bottom: 1.5rem;
}

/* 별점 */
.star-row {
    display: flex;
    gap: 4px;
    margin-bottom: 4px;
    justify-content: flex-end;
}
.star-filled { color: #1e2022; font-size: 20px; }
.star-empty  { color: #e2ddd6; font-size: 20px; }
.pref-label  {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #9ca3af;
    text-align: right;
}

/* 칩 */
.chip-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 1.5rem; }
.chip {
    font-size: 14px;
    font-weight: 600;
    padding: 8px 18px;
    border-radius: 100px;
    border: 1px solid;
    display: inline-block;
}
.chip-family { background:#fef3e2; color:#92400e; border-color:#fcd9a0; }
.chip-note   { background:#ecfdf5; color:#065f46; border-color:#a7f3d0; }
.chip-role   { background:#eff6ff; color:#1e40af; border-color:#bfdbfe; }

/* 소제목 (강화) */
.slbl {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.01em;
    text-transform: uppercase;
    color: #1e2022;
    margin-bottom: 15px;
    margin-top: 3rem;
    padding-bottom: 10px;
    border-bottom: 2px solid #1e2022;
}

/* 태그 */
.otag {
    display: inline-block;
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    color: #495057;
    font-size: 15px;
    font-weight: 500;
    padding: 6px 16px;
    border-radius: 100px;
    margin: 4px 4px;
}

/* 박스 (줄간격 및 패딩 강화) */
.sbox {
    background: #fafafa;
    border-radius: 15px;
    padding: 2rem;
    margin-bottom: 1rem;
    font-size: 16px;
    color: #374151;
    line-height: 1.85;
}

/* 2컬럼 박스 */
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 1.5rem;
}
.col-box {
    background: #fafafa;
    border-radius: 15px;
    padding: 2rem;
}
.col-ttl {
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 12px;
}
.col-tx { font-size: 16px; color: #374151; line-height: 1.85; }

/* 인용 박스 */
.qt-box {
    background: #1e2022;
    border-radius: 18px;
    padding: 2rem 2.5rem;
    margin-top: 1.5rem;
}
.qt-text {
    font-size: 18px;
    color: #f0ece6;
    line-height: 1.9;
    font-weight: 300;
    font-style: italic;
}
.qt-attr {
    font-size: 12px;
    color: #6b7280;
    margin-top: 12px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    font-weight: 600;
}

/* 핵심 데이터 카드 (값 중앙, 라벨 하단 고정) */
.chem4 { display: grid; grid-template-columns: repeat(4,1fr); gap: 15px; margin-bottom: 1.5rem; }
.ccard { 
    background: #f8f9fa; 
    border-radius: 12px; 
    padding: 15px 12px; 
    display: flex;
    flex-direction: column;
    text-align: center; 
    border: 1px solid #f1f3f5;
    min-height: 110px !important; 
}
.cval-container {
    flex: 1;             /* 남은 공간 모두 차지 */
    display: flex;
    align-items: center; /* 수직 중앙 정렬 */
    justify-content: center;
    width: 100%;
}
.cval  { 
    font-size: 16px; 
    font-weight: 800; 
    color: #1e2022; 
    word-break: keep-all;
    line-height: 1.4;
}
.ckey  { 
    font-size: 11px; 
    font-weight: 800; 
    letter-spacing: 0.12em; 
    text-transform: uppercase; 
    color: #9ca3af; 
    padding-top: 10px;
}

/* 탭 카테고리 글자 크기 최적화 (18px) */
.stTabs [data-baseweb="tab"] p {
    font-size: 18px !important;
    font-weight: 700 !important;
    white-space: nowrap;
}
.stTabs [data-baseweb="tab"] {
    margin-right: 15px !important;
    padding-bottom: 2px !important;
}

/* 산업 바 */
.bar-row  { margin-bottom: 15px; }
.bar-top  { display: flex; justify-content: space-between; font-size: 15px; font-weight: 600; color: #1e2022; margin-bottom: 8px; }
.bar-desc { font-size: 13px; color: #6b7280; }
.bar-bg   { background: #e9ecef; border-radius: 100px; height: 8px; }
.bar-fill { background: #1e2022; border-radius: 100px; height: 8px; }

/* 링크 */
.lnk-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 1.2rem; }
.lnk {
    display: flex; align-items: center; gap: 10px;
    background: #f7f6f3; border: 1px solid #e2ddd6;
    border-radius: 11px; padding: 10px 14px;
    text-decoration: none;
}
.lnk-t { font-size: 13px; font-weight: 600; color: #1e2022; }
.lnk-s { font-size: 12px; color: #6b7280; }

/* 트렌드 카드 */
.trend-card {
    border-left: 3px solid #1e2022;
    padding: 10px 14px;
    margin-bottom: 7px;
    background: #f7f6f3;
    border-radius: 0 11px 11px 0;
}
.trend-m  { font-size: 11px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #4a5260; margin-bottom: 4px; }
.trend-tx { font-size: 13px; color: #4a4e54; line-height: 1.7; }

/* API 안내 박스 */
.api-box {
    background: #f7f6f3; border-radius: 11px;
    padding: 1rem 1.2rem;
    font-size: 13px; color: #4a4e54; line-height: 1.75;
    margin-top: 0.8rem;
}

/* Safety & Regulation 박스 */
.safety-box {
    background: #fff5f5;
    border: 1px solid #feb2b2;
    border-left: 5px solid #f56565;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1rem;
}
.safety-m { font-size: 18px; font-weight: 700; color: #c53030; margin-bottom: 8px; }
.safety-s { font-size: 16px; color: #4a5568; line-height: 1.7; }

/* 사이드바 통일 */
[data-testid="stSidebar"] {
    background-color: #1e2022 !important;
}
[data-testid="stSidebarNav"] span {
    color: #f0ece6 !important;
    font-weight: 500;
}
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
    import re
    tags = []
    for d in str(descriptors).split(","):
        t = d.strip()
        # 기본 필터링: 빈 문자열, N/A, image, vs, nan 등 제외
        if not t or t.lower() in ("n/a", "image", "nan", "vs", "none", ""):
            continue
        # 한글 포함 항목 제외
        if re.search('[가-힣]', t):
            continue
        tags.append(t)
    
    return "".join([f'<span class="otag">{t}</span>' for t in tags])


def format_formula(formula: str) -> str:
    """화학 분자식의 숫자를 HTML 아래첨자(sub)로 변환"""
    if not formula or formula in ("N/A", "nan", "—", ""):
        return "—"
    import re
    # 숫자 부분만 <sub>로 감쌈
    return re.sub(r'(\d+)', r'<sub>\1</sub>', str(formula))


def safe(val) -> str:
    v = str(val).strip()
    return v if v not in ("N/A", "nan", ":", "") else "—"


# ── 상단 필터 바 ─────────────────────────────────────────────────────────────
def render_top_filters(df):
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    
    with c1:
        query = st.text_input("원료명 검색", "", placeholder="Search ingredients...")

    with c2:
        vol_opts = ["All"] + sorted([
            v for v in df["volatility_class"].dropna().unique()
            if v not in ("N/A", "nan")
        ])
        vol = st.selectbox("Volatility Class", vol_opts)

    with c3:
        fam_raw = sorted([
            f for f in df["odor_family"].dropna().unique()
            if f not in ("N/A", "nan")
        ])
        fam_opts = ["All"] + [f"{FAMILY_EMOJI.get(f,'⚗️')} {f}" for f in fam_raw]
        fam_sel  = st.selectbox("Odor Family", fam_opts)
        fam      = fam_sel.split(" ", 1)[1] if fam_sel != "All" else "All"

    with c4:
        ind_opts = ["All"] + sorted(list(INDUSTRY_INFO.keys()))
        ind      = st.selectbox("Industry", ind_opts)

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

    # Sensory Summary (Personal Memory (KR) 우선)
    st.markdown('<div class="slbl">Sensory Summary</div>', unsafe_allow_html=True)
    summary = str(ing.get("Personal Memory (KR)", "")).strip()
    if not summary or summary in ("N/A", "nan", "—", "None"):
        # Fallback to sensory_notes first line
        notes = str(ing.get("sensory_notes", "")).split("|")
        summary = notes[0].strip() if notes else "No memory recorded."
    
    st.markdown(f'<div class="sbox">{summary}</div>', unsafe_allow_html=True)

    # At a Glance 4칸
    st.markdown('<div class="slbl">At a Glance</div>', unsafe_allow_html=True)
    origin  = safe(ing.get("origin_country", ""))
    method  = safe(ing.get("extraction_method", ""))
    comp    = safe(ing.get("main_components", "")).split(",")[0].strip()
    usages  = [u.strip() for u in str(ing.get("industry_usage","")).split(",") if u.strip() not in ("N/A","perfume","")]
    indust  = " · ".join(usages[:2]) if usages else "—"

    st.markdown(f"""
    <div class="chem4">
      <div class="ccard"><div class="cval-container"><div class="cval">{origin}</div></div><div class="ckey">Origin</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{method}</div></div><div class="ckey">Extraction</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{comp}</div></div><div class="ckey">Key Component</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{indust}</div></div><div class="ckey">Top Industries</div></div>
    </div>
    """, unsafe_allow_html=True)


def tab_sensory(ing):
    obj_desc  = safe(ing.get("objective_description", ""))
    subj_desc = safe(ing.get("subjective_description", ""))

    # PROFESSIONAL 텍스트 가공 (영어/한글 분리 및 정렬 시도)
    # 만약 데이터가 한글로만 되어 있다면 그대로 노출하되, 영문이 섞여 있다면 영문을 위로 배치
    display_obj = obj_desc
    if obj_desc != "—":
        import re
        # 영문과 한글이 섞여 있는지 체크 (단순 줄바꿈 처리 포함)
        en_parts = []
        kr_parts = []
        for line in obj_desc.split("\n"):
            if re.search('[가-힣]', line):
                kr_parts.append(line.strip())
            else:
                en_parts.append(line.strip())
        
        if en_parts and kr_parts:
            display_obj = f"{' '.join(en_parts)}<br/><div style='margin-top:8px; color:#6b7280;'>{' '.join(kr_parts)}</div>"
        elif kr_parts and not en_parts:
            # 한글만 있는 경우 (현재 상태)
            display_obj = kr_parts[0]

    st.markdown(f"""
    <div class="two-col">
      <div class="col-box">
        <div class="col-ttl">Professional</div>
        <div class="col-tx" style="line-height:1.6;">{display_obj}</div>
      </div>
      <div class="col-box">
        <div class="col-ttl">Personal Memory</div>
        <div class="col-tx" style="line-height:1.6;">{subj_desc}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Odor Descriptors (정제 로직 적용)
    st.markdown('<div class="slbl">Odor Descriptors</div>', unsafe_allow_html=True)
    tags_html = render_odor_tags(ing.get("odor_descriptors", ""))
    st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)

    # Detailed Notes
    notes_raw = str(ing.get("sensory_notes", ""))
    if notes_raw and notes_raw not in ("N/A", "nan"):
        st.markdown('<div class="slbl">Detailed Notes</div>', unsafe_allow_html=True)
        for note in notes_raw.split("|"):
            n = note.strip()
            if n:
                st.markdown(f'<div class="sbox">{n}</div>', unsafe_allow_html=True)

    # Comparison Notes (디자인 개편)
    comp_notes = str(ing.get("comparison_notes", "")).strip()
    if comp_notes and comp_notes not in ("N/A", "nan", ""):
        st.markdown('<div class="slbl">Comparison Notes</div>', unsafe_allow_html=True)
        
        # 여러 쌍이 있을 경우 (|| 또는 패턴으로 분리 가능성 대비)
        pairs = comp_notes.split("||") if "||" in comp_notes else [comp_notes]
        
        for idx, pair in enumerate(pairs):
            if idx > 0: st.markdown("---")
            
            parts = [p.strip() for p in pair.split("|") if p.strip()]
            if parts:
                # 설명이 포함된 항목들 추출
                desc_items = [p for p in parts if ":" in p]
                
                # 지능형 제목 생성: 설명 항목에서 원료명 추출하여 A vs B 형태 완성
                names_found = []
                for item in desc_items:
                    n = item.split(":", 1)[0].strip()
                    if n not in names_found: names_found.append(n)
                
                if len(names_found) >= 2:
                    title = f"{names_found[0]} vs {names_found[1]}"
                else:
                    # 기존 제목 사용하되 image 등 불필요 단어 제거
                    title = parts[0].replace("image", "").strip()
                
                # 제목 볼드 처리
                st.markdown(f'<div style="font-size: 17px; font-weight: 800; color: #1e2022; margin-bottom: 12px;">{title}</div>', unsafe_allow_html=True)
                
                # 불렛 리스트 형태
                list_html = '<div style="font-size: 15px; line-height: 1.8; color: #4a5568; margin-left: 5px;">'
                for desc in desc_items:
                    name_part, text_part = desc.split(":", 1)
                    name_part = name_part.strip()
                    text_part = text_part.strip()
                    
                    # 설명 끝에 원료명이 중복으로 붙어있는 경우 제거 (오타 대응 포함)
                    # 현재 비교 중인 모든 원료명을 후보군으로 설정
                    candidates = [n.lower() for n in names_found]
                    # 흔한 오타 교차 체크 (Ceaderwood <-> Cedarwood 등)
                    if "ceaderwood" in candidates and "cedarwood" not in candidates: candidates.append("cedarwood")
                    if "cedarwood" in candidates and "ceaderwood" not in candidates: candidates.append("ceaderwood")
                    
                    words = text_part.split()
                    if words:
                        # 마지막 단어 추출 (문장부호 제외)
                        last_word = words[-1].strip(".,!? ").lower()
                        if last_word in candidates:
                            text_part = " ".join(words[:-1]).strip()
                            # 남은 문장 부호 정리
                            text_part = text_part.rstrip(". ").strip()
                    
                    if not text_part.endswith("."): text_part += "." # 마침표 보정
                    
                    list_html += f'<div style="margin-bottom: 8px;"><b style="color: #1e2022;">• {name_part}</b>: {text_part}</div>'
                list_html += '</div>'
                st.markdown(list_html, unsafe_allow_html=True)

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
    raw_cid = safe(ing.get("pubchem_cid", ""))
    # CID 정수 변환 (8294.0 같은 실수형 방지)
    try:
        cid = str(int(float(raw_cid))) if raw_cid and raw_cid != "—" else "—"
    except:
        cid = raw_cid

    cas     = safe(ing.get("cas_number", ""))
    formula = safe(ing.get("molecular_formula", ""))
    weight  = safe(ing.get("molecular_weight", ""))

    st.markdown('<div class="slbl">Chemical Identity</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="chem4">
      <div class="ccard"><div class="cval-container"><div class="cval">{format_formula(formula)}</div></div><div class="ckey">Formula</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{weight}</div></div><div class="ckey">MW g/mol</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{cid}</div></div><div class="ckey">PubChem CID</div></div>
      <div class="ccard"><div class="cval-container"><div class="cval">{cas}</div></div><div class="ckey">CAS No.</div></div>
    </div>
    """, unsafe_allow_html=True)

    # PubChem 구조식 이미지
    if cid and cid != "—":
        st.markdown('<div class="slbl">Chemical Structure</div>', unsafe_allow_html=True)
        img_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG"
        # 이미지 로딩 실패 대비 alt 텍스트 및 에러 처리
        st.image(img_url, width=300, caption=f"PubChem CID {cid}")

    # 주요 성분 (태그형으로 변경)
    components = safe(ing.get("main_components", ""))
    if components != "—":
        st.markdown('<div class="slbl">Key Components</div>', unsafe_allow_html=True)
        comps_html = '<div style="margin-bottom: 1.5rem;">'
        for comp in components.split(","):
            c = comp.strip()
            if c:
                comps_html += f'<span class="otag">{c}</span>'
        comps_html += '</div>'
        st.markdown(comps_html, unsafe_allow_html=True)


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
    st.markdown('<div class="pg-title">🔍 Ingredient Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-desc">조향 원료의 화학적 데이터와 감각 분석 정보를 탐색하는 고급 라이브러리입니다.</div>', unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        return

    # 1. 상단 필터 바
    query, vol, fam, ind = render_top_filters(df)
    filtered = apply_filters(df, query, vol, fam, ind)

    # 2. 원료 선택 (전체 너비)
    st.markdown(f"**{len(filtered)}개 원료가 검색되었습니다.**")
    if filtered.empty:
        st.info("검색 결과가 없습니다. 필터를 조정해 보세요.")
        return

    selected_name = st.selectbox(
        "원료를 선택하세요",
        filtered["name"].tolist(),
        label_visibility="visible"
    )

    if not selected_name:
        return

    ing = df[df["name"] == selected_name].iloc[0].to_dict()

    # 3. 상세 정보 (전체 너비 카드 스타일)
    st.markdown('<div class="ing-card">', unsafe_allow_html=True)
    
    # 헤더 섹션
    family     = safe(ing.get("odor_family", ""))
    volatility = safe(ing.get("volatility_class", ""))
    role       = safe(ing.get("role", ""))
    sci        = safe(ing.get("scientific_name", ""))
    score      = ing.get("preference_score", 0)

    header_html = f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
      <div>
        <div class="ing-name">{selected_name}</div>
        <div class="ing-sci">{sci}</div>
      </div>
      <div>{render_stars(score)}</div>
    </div>
    {render_chips(family, volatility, role)}
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # 탭 섹션 (전체 너비)
    t_ov, t_se, t_ch, t_in = st.tabs(["Overview", "Sensory Analysis", "Chemical Identity", "Industry Data"])

    with t_ov: tab_overview(ing)
    with t_se: tab_sensory(ing)
    with t_ch: tab_chemistry(ing)
    with t_in: tab_industry(ing)
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
