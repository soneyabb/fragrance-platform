"""
02_Compare.py
-------------
Sillage — Side by Side Comparison
기능 1: 비교 테이블
기능 2: Radar Chart
기능 3: 유사 원료 찾기 (클릭 시 비교 테이블 자동 추가)
기능 4: Odor Family 탐색
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import re
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer

st.set_page_config(
    page_title="Compare — Sillage",
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
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.4rem;
}
.pg-title {
    font-family: 'DM Serif Display', serif;
    font-size: 40px; color: var(--ink);
    margin-bottom: 0.3rem; line-height: 1;
}
.pg-sub { font-size: 14px; color: var(--muted); margin-bottom: 2rem; }

.section-rule {
    border: none; border-top: 1px solid var(--rule); margin: 2rem 0;
}
.sec-label {
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.8rem; margin-top: 2rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}

/* 선택된 원료 태그 */
.selected-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem; }
.sel-tag {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 13px; font-weight: 500;
    padding: 6px 14px;
    border: 1px solid var(--ink);
    border-radius: 2px;
    background: var(--ink); color: #f0ece6;
}

/* 비교 테이블 */
.cmp-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.cmp-table th {
    font-family: 'DM Serif Display', serif;
    font-size: 18px; font-weight: 400;
    color: var(--ink); padding: 12px 16px;
    border-bottom: 2px solid var(--ink);
    text-align: left; background: white;
}
.cmp-table th.row-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted);
}
.cmp-table td {
    padding: 10px 16px;
    border-bottom: 1px solid var(--rule);
    color: var(--ink); vertical-align: top;
}
.cmp-table tr:hover td { background: #f5f3ef; }
.cmp-table .row-label {
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); background: var(--paper) !important;
    min-width: 140px;
}
.badge-c { color: var(--active); font-weight: 600; font-size: 12px; }
.badge-m { color: var(--gold);   font-weight: 600; font-size: 12px; }
.badge-r { color: var(--muted);  font-weight: 600; font-size: 12px; }

/* 유사 원료 */
.sim-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--rule);
    font-size: 13px;
}
.sim-rank  { color: var(--muted); min-width: 24px; }
.sim-name  { font-weight: 500; flex: 1; padding: 0 12px; }
.sim-common { color: var(--muted); font-size: 12px; flex: 2; }
.sim-score  { font-size: 11px; color: var(--muted); min-width: 36px; text-align: right; }

/* Family 카드 */
.family-card {
    background: white; border: 1px solid var(--rule);
    border-radius: 3px; padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.family-card-name { font-weight: 500; font-size: 14px; margin-bottom: 4px; }
.family-card-meta { font-size: 12px; color: var(--muted); }

/* 하단 연결 */
.nav-link {
    display: inline-block; font-size: 13px; font-weight: 500;
    padding: 8px 20px; border: 1px solid var(--rule);
    border-radius: 2px; background: white; color: var(--ink);
    text-decoration: none; margin-right: 8px;
}

.empty-state {
    font-size: 13px; color: var(--muted);
    padding: 1.2rem 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 상수
# ─────────────────────────────────────────
FAMILY_EMOJI = {
    "Citrus":"🍊","Fruity":"🥭","Green":"🌱","Herbal":"🌿","Floral":"🌸",
    "Aldehyde":"🧼","Animal":"🐾","Woody":"🪵","Mossy":"🪨",
    "Spicy":"🫚","Balsamic":"🍯",
}


# ─────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    # 스크립트 위치 기준 절대 경로 생성
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "data", "fragrance_db.sqlite")
    
    if not os.path.exists(db_path):
        st.error(f"DB 파일 없음: {db_path}")
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

def get_quality_tier(ing: dict) -> str:
    src = str(ing.get("data_source", "")).lower()
    if "notion_manual" in src or "user" in src:
        return "curated"
    elif "pubchem" in src or "pyrfume" in src:
        return "mapped"
    return "registered"

def tier_badge(tier: str) -> str:
    return {
        "curated":    '<span class="badge-c">★★★ Curated</span>',
        "mapped":     '<span class="badge-m">★★☆ Mapped</span>',
        "registered": '<span class="badge-r">★☆☆ Registered</span>',
    }.get(tier, "—")

def render_stars(score) -> str:
    try:
        s = int(float(score))
    except Exception:
        return "—"
    return "★" * min(s, 5) + "☆" * (5 - min(s, 5))

def parse_descriptors(s: str) -> list:
    return [d.strip().lower() for d in str(s).split(",")
            if d.strip() and d.strip().lower()
            not in ("n/a", "nan", "image", "vs", "none", "")
            and not re.search('[가-힣]', d.strip())]


# ─────────────────────────────────────────
# 유사도 계산
# odor_descriptor 멀티핫 벡터 → cosine similarity
# 외부 API 없음, sklearn 로컬 계산
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def compute_similarity(_df: pd.DataFrame) -> pd.DataFrame:
    df = _df.copy()
    df["desc_list"] = df["odor_descriptors"].apply(parse_descriptors)
    mlb = MultiLabelBinarizer()
    matrix = mlb.fit_transform(df["desc_list"])
    sim_matrix = cosine_similarity(matrix)
    return pd.DataFrame(sim_matrix,
                        index=df["name"].values,
                        columns=df["name"].values)

def get_similar(sim_df, base_name, df, top_n=5):
    if base_name not in sim_df.index:
        return []
    scores = sim_df[base_name].drop(index=base_name).sort_values(ascending=False)
    base_descs = set(parse_descriptors(
        df[df["name"] == base_name]["odor_descriptors"].values[0]
    ))
    results = []
    for name, score in scores.head(top_n).items():
        row = df[df["name"] == name]
        if row.empty:
            continue
        other_descs = set(parse_descriptors(row["odor_descriptors"].values[0]))
        common = list(base_descs & other_descs)[:4]
        results.append((name, round(float(score), 2), common))
    return results


# ─────────────────────────────────────────
# 기능 1 — 비교 테이블
# 행 클릭 정렬: Streamlit HTML 한계로 미구현
# 셀 클릭 이동: 하단 Navigate 링크로 대체
# ─────────────────────────────────────────
def render_compare_table(selected_ings: list):
    st.markdown('<div class="sec-label">Comparison Table</div>',
                unsafe_allow_html=True)

    ROWS = [
        ("tier",             "Quality"),
        ("odor_family",      "Odor Family"),
        ("volatility_class", "Note Position"),
        ("boiling_point",    "Boiling Point"),
        ("logp",             "logP"),
        ("vapor_pressure",   "Vapor Pressure"),
        ("ifra_status",      "IFRA Status"),
        ("occurrence",       "Occurrence"),
        ("odor_descriptors", "Odor Descriptors"),
        ("preference_score", "Preference"),
    ]

    # 파이프라인 미완성 컬럼 — DB에 없으므로 "—" 처리
    PIPELINE_PENDING = {
        "boiling_point", "logp", "vapor_pressure",
        "ifra_status", "occurrence"
    }

    header = '<tr><th class="row-header">Attribute</th>'
    for ing in selected_ings:
        header += f'<th>{ing["name"]}</th>'
    header += "</tr>"

    rows_html = ""
    for key, label in ROWS:
        rows_html += f'<tr><td class="row-label">{label}</td>'
        for ing in selected_ings:
            tier = get_quality_tier(ing)

            if key == "tier":
                cell = tier_badge(tier)

            elif key in PIPELINE_PENDING:
                cell = "—"

            elif key == "odor_descriptors":
                descs = parse_descriptors(str(ing.get(key, "")))
                cell  = ", ".join(descs[:4])
                if len(descs) > 4:
                    cell += "…"

            elif key == "preference_score":
                # CURATED만 표시
                cell = render_stars(ing.get(key, 0)) if tier == "curated" else "—"

            elif key == "volatility_class":
                v = safe(ing.get(key, ""))
                cell = v.capitalize() if v != "—" else "—"

            else:
                cell = safe(ing.get(key, ""))

            rows_html += f"<td>{cell}</td>"
        rows_html += "</tr>"

    st.markdown(f"""
    <div style="overflow-x:auto;">
        <table class="cmp-table">
            <thead>{header}</thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
        Boiling Point · logP · Vapor Pressure · IFRA Status · Occurrence —
        파이프라인 완성 후 자동 반영
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 기능 2 — Radar Chart
# 실수치 없음 → 구조 확정, 파이프라인 후 교체
# ─────────────────────────────────────────
def render_radar(selected_ings: list):
    st.markdown('<div class="sec-label">Radar Chart</div>',
                unsafe_allow_html=True)

    if len(selected_ings) < 2:
        st.markdown("""
        <div class="empty-state">
            원료를 2개 이상 선택하면 Radar Chart가 표시됩니다.
        </div>
        """, unsafe_allow_html=True)
        return

    axes   = ["Persistence", "Diffusion", "Skin Affinity", "Market Use", "Safety"]
    colors = ["#1a1a18", "#b5935a", "#2d6a4f", "#6b6860", "#92400e"]
    fig    = go.Figure()

    for i, ing in enumerate(selected_ings):
        # TODO: 파이프라인 완성 후 실수치로 교체
        # Persistence  → boiling_point 정규화
        # Diffusion    → vapor_pressure 역수 정규화
        # Skin Affinity→ logP 정규화
        # Market Use   → Parfumo occurrence 정규화
        # Safety       → IFRA status (Compliant=1, Restricted=0.5, Prohibited=0)
        values = [0, 0, 0, 0, 0]

        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=axes + [axes[0]],
            fill="toself",
            name=ing["name"],
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.25,
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1],
                            tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=12, family="DM Sans")),
        ),
        showlegend=True,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#1a1a18"),
        legend=dict(font=dict(size=12)),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    <div style="font-size:11px;color:var(--muted);">
        Persistence(boiling point) · Diffusion(vapor pressure) ·
        Skin Affinity(logP) · Market Use(Parfumo) · Safety(IFRA) —
        파이프라인 완성 후 실수치 반영
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 기능 3 — 유사 원료 찾기
# 클릭 시 비교 테이블에 자동 추가 (st.button)
# ─────────────────────────────────────────
def render_similar(df, sim_df, selected_names):
    st.markdown('<div class="sec-label">Similar Ingredients</div>',
                unsafe_allow_html=True)

    if not selected_names:
        st.markdown("""
        <div class="empty-state">원료를 선택하면 유사 원료가 표시됩니다.</div>
        """, unsafe_allow_html=True)
        return

    base = st.selectbox(
        "기준 원료 선택",
        selected_names,
        key="sim_base",
        label_visibility="visible"
    )

    results = get_similar(sim_df, base, df, top_n=5)

    if not results:
        st.markdown("""
        <div class="empty-state">유사 원료를 계산할 수 없습니다.</div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
        <strong>{base}</strong> 기준 —
        odor descriptor cosine similarity
    </div>
    """, unsafe_allow_html=True)

    for i, (name, score, common) in enumerate(results, 1):
        common_str = ", ".join(common) if common else "—"
        already    = name in selected_names
        can_add    = len(selected_names) < 5 and not already

        col_info, col_btn = st.columns([6, 1])
        with col_info:
            st.markdown(f"""
            <div class="sim-row">
                <span class="sim-rank">{i}</span>
                <span class="sim-name">{name}</span>
                <span class="sim-common">공통: {common_str}</span>
                <span class="sim-score">{score:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if already:
                st.markdown(
                    '<div style="font-size:11px;color:var(--active);'
                    'padding-top:0.8rem;">✓ 추가됨</div>',
                    unsafe_allow_html=True
                )
            elif can_add:
                if st.button("+ 추가", key=f"sim_add_{name}"):
                    st.session_state.selected_names.append(name)
                    st.rerun()

    st.markdown("""
    <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
        계산 방식: odor descriptor 벡터 cosine similarity · 외부 API 없음
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 기능 4 — Odor Family 탐색
# 카드 클릭 → Streamlit 한계로 버튼으로 대체
# ─────────────────────────────────────────
def render_family_explorer(df, selected_names):
    st.markdown('<div class="sec-label">Odor Family Explorer</div>',
                unsafe_allow_html=True)

    families = sorted([f for f in df["odor_family"].dropna().unique()
                       if f not in ("N/A", "nan")])

    selected_family = st.radio(
        "", families, horizontal=True,
        key="family_explorer", label_visibility="collapsed"
    )

    family_df = df[df["odor_family"] == selected_family]
    emoji     = FAMILY_EMOJI.get(selected_family, "")

    st.markdown(f"""
    <div style="font-size:12px;color:var(--muted);margin-bottom:1rem;">
        {emoji} {selected_family} — {len(family_df)}개 원료
    </div>
    """, unsafe_allow_html=True)

    for _, row in family_df.iterrows():
        name      = row["name"]
        vol       = str(row.get("volatility_class", "")).capitalize()
        descs     = parse_descriptors(str(row.get("odor_descriptors", "")))
        desc_short = ", ".join(descs[:3])
        tier      = get_quality_tier(row.to_dict())
        badge_txt = {"curated":"★★★","mapped":"★★☆","registered":"★☆☆"}.get(tier,"")
        already   = name in selected_names
        can_add   = len(selected_names) < 5 and not already

        col_card, col_btn = st.columns([6, 1])
        with col_card:
            added_mark = (
                ' <span style="color:var(--active);font-size:11px;">✓</span>'
                if already else ""
            )
            st.markdown(f"""
            <div class="family-card">
                <div class="family-card-name">
                    {badge_txt} {name}{added_mark}
                </div>
                <div class="family-card-meta">
                    {vol} note · {desc_short}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if can_add:
                if st.button("+ 추가", key=f"fam_add_{name}"):
                    st.session_state.selected_names.append(name)
                    st.rerun()


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Side by Side</div>
    <div class="pg-title">Compare</div>
    <div class="pg-sub">
        원료를 나란히 놓고 물성, 규제, 시장 빈도를 비교합니다.
        조향사의 선택 흐름을 그대로 반영합니다.
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        return

    # session_state 초기화
    if "selected_names" not in st.session_state:
        st.session_state.selected_names = []

    all_names = df["name"].tolist()

    # ── 원료 선택 영역 ──────────────────────
    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
        unsafe_allow_html=True
    )

    # 선택된 원료 태그 표시
    if st.session_state.selected_names:
        tags_html = '<div class="selected-wrap">'
        for n in st.session_state.selected_names:
            tags_html += f'<span class="sel-tag">{n}</span>'
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)

    # 원료 추가/제거
    col_add, col_remove, col_clear = st.columns([2, 2, 1])

    with col_add:
        if len(st.session_state.selected_names) < 5:
            to_add = st.selectbox(
                "",
                ["+ 원료 추가"] + [n for n in all_names
                                   if n not in st.session_state.selected_names],
                key="add_selector",
                label_visibility="collapsed"
            )
            if to_add and to_add != "+ 원료 추가":
                st.session_state.selected_names.append(to_add)
                st.rerun()
        else:
            st.markdown(
                '<div style="font-size:12px;color:var(--muted);padding-top:0.5rem;">'
                '최대 5개까지 선택 가능합니다.</div>',
                unsafe_allow_html=True
            )

    with col_remove:
        if st.session_state.selected_names:
            to_remove = st.selectbox(
                "",
                ["— 원료 제거"] + st.session_state.selected_names,
                key="remove_selector",
                label_visibility="collapsed"
            )
            if to_remove and to_remove != "— 원료 제거":
                st.session_state.selected_names.remove(to_remove)
                st.rerun()

    with col_clear:
        if st.session_state.selected_names:
            if st.button("전체 초기화"):
                st.session_state.selected_names = []
                st.rerun()

    # 빠른 추가 — 첫 번째 선택 원료의 Odor Family 기준
    if st.session_state.selected_names:
        base_name  = st.session_state.selected_names[0]
        base_row   = df[df["name"] == base_name]
        if not base_row.empty:
            base_family = safe(base_row.iloc[0].get("odor_family", ""))
            if base_family != "—":
                same_family = df[
                    (df["odor_family"] == base_family) &
                    (~df["name"].isin(st.session_state.selected_names))
                ]["name"].tolist()[:5]

                if same_family:
                    st.markdown(f"""
                    <div style="font-size:11px;color:var(--muted);
                                margin-top:0.5rem;margin-bottom:4px;">
                        같은 {FAMILY_EMOJI.get(base_family,"")}
                        {base_family} 계열 빠른 추가:
                    </div>
                    """, unsafe_allow_html=True)
                    q_cols = st.columns(len(same_family))
                    for i, qname in enumerate(same_family):
                        with q_cols[i]:
                            if st.button(qname, key=f"quick_{qname}"):
                                if len(st.session_state.selected_names) < 5:
                                    st.session_state.selected_names.append(qname)
                                    st.rerun()

    st.markdown(
        '<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
        unsafe_allow_html=True
    )

    # ── 선택된 원료 데이터 추출 ─────────────
    selected_ings = []
    for name in st.session_state.selected_names:
        row = df[df["name"] == name]
        if not row.empty:
            selected_ings.append(row.iloc[0].to_dict())

    # ── 기능 1: 비교 테이블 ─────────────────
    if selected_ings:
        render_compare_table(selected_ings)
    else:
        st.markdown("""
        <div class="empty-state">
            위에서 원료를 선택하면 비교 테이블이 표시됩니다.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 기능 2: Radar Chart ─────────────────
    render_radar(selected_ings)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 기능 3: 유사 원료 찾기 ─────────────
    sim_df = compute_similarity(df)
    render_similar(df, sim_df, st.session_state.selected_names)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 기능 4: Odor Family 탐색 ───────────
    render_family_explorer(df, st.session_state.selected_names)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 하단 연결 ───────────────────────────
    st.markdown('<div class="sec-label">Navigate</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <a class="nav-link" href="/06_Blend" target="_self">
        → 선택한 원료로 Blend에서 조합해보기
    </a>
    <a class="nav-link" href="/01_Ingredients" target="_self">
        → Ingredients 상세 페이지
    </a>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
