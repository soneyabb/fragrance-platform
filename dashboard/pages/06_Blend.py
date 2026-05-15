"""
06_Blend.py
-----------
Sillage — Blend & Compose
기능 1: 조합 시뮬레이션 (원료 선택 + 비율 슬라이더 → 시각화)
기능 2: 감각 언어 → 원료 변환 (sensory_notes 키워드 매핑)

AI 생성 텍스트 없음 — 데이터 기반 시각화만
Claude API 연동 시 정확도 향상 가능 (명시)
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Blend — Sillage",
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
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}
[data-testid="stSidebar"] { background-color: var(--ink) !important; }
[data-testid="stSidebarNav"] span {
    color: #c8c4bc !important;
    font-size: 13px; font-weight: 400;
    letter-spacing: 0.04em; text-transform: uppercase;
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

.sec-label {
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.8rem; margin-top: 2rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}
.sec-header {
    font-family: 'DM Serif Display', serif;
    font-size: 24px; color: var(--ink);
    margin-bottom: 0.3rem; margin-top: 0;
}
.sec-desc {
    font-size: 13px; color: var(--muted);
    margin-bottom: 1.5rem; line-height: 1.6;
}
.section-rule {
    border: none; border-top: 1px solid var(--rule); margin: 2.5rem 0;
}

/* 예상 표시 배너 */
.estimate-banner {
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--warn); background: #fef3e2;
    border: 1px solid #fcd9a0;
    padding: 6px 14px; border-radius: 2px;
    display: inline-block; margin-bottom: 1.5rem;
}

/* 선택 원료 행 */
.blend-row {
    display: flex; align-items: center;
    gap: 12px; margin-bottom: 0.5rem;
    font-size: 13px;
}
.blend-name { font-weight: 500; min-width: 160px; }
.blend-vol  { font-size: 11px; color: var(--muted); min-width: 80px; }
.blend-tier { font-size: 11px; color: var(--muted); min-width: 60px; }

/* IFRA 상태 */
.ifra-ok  { color: var(--active); font-weight: 600; font-size: 13px; }
.ifra-res { color: var(--warn);   font-weight: 600; font-size: 13px; }
.ifra-unk { color: var(--muted);  font-size: 13px; }

/* 감각 태그 */
.stag {
    display: inline-block;
    font-size: 12px; padding: 4px 12px;
    border: 1px solid var(--rule); border-radius: 2px;
    margin: 3px 3px; background: white; color: var(--ink);
}
.stag-match {
    background: #f0faf5; border-color: #a7f3d0;
    color: var(--active);
}

/* 원료 추천 카드 */
.rec-row {
    padding: 0.8rem 0;
    border-bottom: 1px solid var(--rule);
    font-size: 13px;
}
.rec-name { font-weight: 500; color: var(--ink); margin-bottom: 3px; }
.rec-meta { font-size: 12px; color: var(--muted); }

/* placeholder */
.intel-placeholder {
    background: white; border: 1px solid var(--rule);
    border-left: 3px solid var(--gold);
    padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
    font-size: 13px; color: var(--muted);
    border-radius: 0 3px 3px 0; line-height: 1.7;
}

.empty-state {
    font-size: 13px; color: var(--muted);
    padding: 1rem 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
}
</style>
""", unsafe_allow_html=True)


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

def parse_descriptors(s: str) -> list:
    return [d.strip().lower() for d in str(s).split(",")
            if d.strip() and d.strip().lower()
            not in ("n/a", "nan", "image", "vs", "none", "")
            and not re.search('[가-힣]', d.strip())]

def parse_sensory_notes(s: str) -> list:
    """
    sensory_notes (파이프 구분) → 키워드 추출
    한글 포함 단락에서 영단어만 추출
    """
    words = []
    for segment in str(s).split("|"):
        for word in segment.split():
            w = re.sub(r'[^a-zA-Z]', '', word).lower()
            if len(w) >= 3 and not re.search('[가-힣]', word):
                words.append(w)
    return list(set(words))


# ─────────────────────────────────────────
# 기능 1 — 조합 시뮬레이션
# ─────────────────────────────────────────
def simulate_blend(selected_ings: list, ratios: dict) -> dict:
    """
    선택 원료 + 비율 기반 예상 결과 계산
    - Odor Family 분포: 비율 가중
    - Volatility 구조: 비율 가중
    - IFRA 상태: 가장 restrictive 기준
    모두 데이터 기반, AI 생성 없음
    """
    total_ratio = sum(ratios.values()) or 1

    # Odor Family 분포
    family_weights = {}
    for ing in selected_ings:
        name   = ing["name"]
        family = safe(ing.get("odor_family", ""))
        ratio  = ratios.get(name, 1) / total_ratio
        if family != "—":
            family_weights[family] = family_weights.get(family, 0) + ratio

    # Volatility 구조
    vol_weights = {"top": 0, "middle": 0, "base": 0}
    for ing in selected_ings:
        name = ing["name"]
        vol  = str(ing.get("volatility_class", "")).lower().strip()
        ratio = ratios.get(name, 1) / total_ratio
        if vol in vol_weights:
            vol_weights[vol] += ratio

    # IFRA 상태 — 현재 DB에 ifra_status 컬럼 없음
    # 파이프라인 완성 후 교체
    # 지금은 "Unknown" 반환
    ifra_status = "Unknown"

    return {
        "family_dist": family_weights,
        "vol_dist":    vol_weights,
        "ifra_status": ifra_status,
    }


def render_blend_simulator(df: pd.DataFrame):
    st.markdown("""
    <div class="sec-header">Blend Simulator</div>
    <div class="sec-desc">
        원료를 선택하고 비율을 조정하면 예상 향 구조가 시각화됩니다.<br>
        CURATED 66개 + MAPPED 원료에서 선택 가능합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="estimate-banner">
        ⚠ Estimated — 화학적 추정입니다.
        실제 조향 결과와 다를 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    # session_state 초기화
    if "blend_names" not in st.session_state:
        st.session_state.blend_names = []

    # CURATED + MAPPED 원료만
    eligible = df[
        df["data_source"].str.contains(
            "notion_manual|user|pubchem|pyrfume",
            case=False, na=False
        )
    ]["name"].tolist()

    # 원료 추가
    col_add, col_clear = st.columns([3, 1])
    with col_add:
        to_add = st.selectbox(
            "",
            ["+ 원료 추가"] + [n for n in eligible
                               if n not in st.session_state.blend_names],
            key="blend_add_sel",
            label_visibility="collapsed"
        )
        if to_add and to_add != "+ 원료 추가":
            if len(st.session_state.blend_names) < 8:
                st.session_state.blend_names.append(to_add)
                st.rerun()
    with col_clear:
        if st.session_state.blend_names:
            if st.button("전체 초기화", key="blend_clear"):
                st.session_state.blend_names = []
                st.rerun()

    if not st.session_state.blend_names:
        st.markdown("""
        <div class="empty-state">
            원료를 추가하면 조합 시뮬레이션이 시작됩니다.
        </div>
        """, unsafe_allow_html=True)
        return

    # 비율 슬라이더 + 제거 버튼
    st.markdown('<div class="sec-label">원료 비율 설정</div>',
                unsafe_allow_html=True)

    ratios = {}
    to_remove = None

    for name in st.session_state.blend_names:
        row = df[df["name"] == name]
        if row.empty:
            continue
        ing  = row.iloc[0].to_dict()
        tier = get_quality_tier(ing)
        vol  = str(ing.get("volatility_class", "")).capitalize()

        col_name, col_slider, col_val, col_rm = st.columns([2, 4, 1, 1])
        with col_name:
            st.markdown(f"""
            <div style="padding-top:0.5rem;">
                <div style="font-size:13px;font-weight:500;">{name}</div>
                <div style="font-size:11px;color:var(--muted);">
                    {vol} note
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_slider:
            ratio = st.slider(
                "", 1, 100, 20,
                key=f"ratio_{name}",
                label_visibility="collapsed"
            )
            ratios[name] = ratio
        with col_val:
            st.markdown(f"""
            <div style="padding-top:0.5rem;font-size:12px;
                        color:var(--muted);">{ratio}%</div>
            """, unsafe_allow_html=True)
        with col_rm:
            if st.button("✕", key=f"rm_{name}"):
                to_remove = name

    if to_remove:
        st.session_state.blend_names.remove(to_remove)
        st.rerun()

    # 선택 원료 데이터 추출
    selected_ings = []
    for name in st.session_state.blend_names:
        row = df[df["name"] == name]
        if not row.empty:
            selected_ings.append(row.iloc[0].to_dict())

    # 시뮬레이션 계산
    result = simulate_blend(selected_ings, ratios)

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1.5rem 0;">',
                unsafe_allow_html=True)

    # 결과 시각화
    c1, c2 = st.columns(2)

    with c1:
        # Odor Family 분포 파이 차트
        st.markdown('<div class="sec-label">Estimated Odor Family Distribution</div>',
                    unsafe_allow_html=True)
        family_dist = result["family_dist"]
        if family_dist:
            family_names  = list(family_dist.keys())
            family_values = [round(v * 100, 1) for v in family_dist.values()]

            fig_pie = go.Figure(go.Pie(
                labels=family_names,
                values=family_values,
                hole=0.4,
                marker_colors=[
                    "#1a1a18", "#b5935a", "#2d6a4f",
                    "#6b6860", "#92400e", "#1e40af", "#c4b59a"
                ],
                textinfo="percent+label",
                textposition="inside",
            ))
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#1a1a18"),
                showlegend=True,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.markdown(
                '<div class="empty-state">Odor Family 데이터 없음</div>',
                unsafe_allow_html=True
            )

    with c2:
        # Volatility 구조 바 차트
        st.markdown('<div class="sec-label">Estimated Volatility Structure</div>',
                    unsafe_allow_html=True)
        vol_dist = result["vol_dist"]
        total_vol = sum(vol_dist.values()) or 1

        for label, key in [("Top Note", "top"),
                           ("Middle Note", "middle"),
                           ("Base Note", "base")]:
            pct = round(vol_dist.get(key, 0) / total_vol * 100)
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="display:flex;justify-content:space-between;
                            font-size:12px;margin-bottom:4px;">
                    <span>{label}</span>
                    <span style="color:var(--muted);">{pct}%</span>
                </div>
                <div style="background:var(--rule);height:4px;border-radius:2px;">
                    <div style="background:var(--ink);height:4px;
                                border-radius:2px;width:{pct}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # IFRA 종합 상태
        st.markdown('<div class="sec-label">IFRA Composite Status</div>',
                    unsafe_allow_html=True)
        ifra = result["ifra_status"]
        if ifra == "Compliant":
            cls, label = "ifra-ok", "Compliant"
        elif ifra == "Restricted":
            cls, label = "ifra-res", "Restricted (가장 restrictive 원료 기준)"
        else:
            cls, label = "ifra-unk", "Unknown — IFRA 파이프라인 완성 후 자동 반영"
        st.markdown(f'<div class="{cls}">{label}</div>',
                    unsafe_allow_html=True)

    # Parfumo 유사 향수
    st.markdown('<div class="sec-label">Similar Perfumes from Parfumo</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="intel-placeholder">
        Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.<br>
        원료 조합이 비슷한 향수 상위 5개를 Parfumo 데이터에서 검색합니다.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 기능 2 — 감각 언어 → 원료 변환
# Claude API 없이 sensory_notes 키워드 매핑
# ─────────────────────────────────────────

# 감각 언어 → descriptor 매핑 사전
# 한국어 감각 표현 → 영문 odor descriptor 매핑
# 직접 조사 기반, 확장 가능
SENSORY_MAP = {
    # 숲/자연
    "숲":       ["woody", "green", "earthy", "moss", "cedar"],
    "나무":     ["woody", "cedar", "sandalwood", "pine"],
    "젖은":     ["earthy", "moss", "green", "damp"],
    "흙":       ["earthy", "moss", "patchouli", "vetiver"],
    "이끼":     ["moss", "earthy", "green"],
    "풀":       ["green", "herbal", "fresh"],
    # 꽃
    "꽃":       ["floral", "rose", "jasmine", "lily"],
    "장미":     ["rose", "floral", "powdery"],
    "달콤":     ["sweet", "vanilla", "honey", "fruity"],
    # 시트러스
    "상큼":     ["citrus", "fresh", "bergamot", "lemon"],
    "신선":     ["fresh", "citrus", "aquatic", "clean"],
    "레몬":     ["lemon", "citrus", "fresh"],
    # 스파이시
    "매운":     ["spicy", "pepper", "clove", "cinnamon"],
    "향신료":   ["spicy", "clove", "cinnamon", "cardamom"],
    # 따뜻함
    "따뜻":     ["warm", "woody", "amber", "vanilla", "balsamic"],
    "훈연":     ["smoky", "woody", "leather", "incense"],
    "바닐라":   ["vanilla", "sweet", "warm", "creamy"],
    # 바다/수분
    "바다":     ["marine", "aquatic", "fresh", "salty"],
    "물":       ["aquatic", "fresh", "clean"],
    # 파우더
    "파우더":   ["powdery", "soft", "musty", "iris"],
    "부드러":   ["soft", "powdery", "creamy", "musty"],
    # 영문 직접 입력 대응
    "woody":    ["woody", "cedar", "sandalwood"],
    "floral":   ["floral", "rose", "jasmine"],
    "citrus":   ["citrus", "bergamot", "lemon"],
    "fresh":    ["fresh", "clean", "aquatic"],
    "earthy":   ["earthy", "moss", "vetiver", "patchouli"],
    "sweet":    ["sweet", "vanilla", "honey"],
    "spicy":    ["spicy", "pepper", "clove"],
    "warm":     ["warm", "amber", "vanilla"],
}


def text_to_descriptors(text: str) -> list:
    """
    자유 텍스트 → 매칭 descriptor 목록
    1. SENSORY_MAP 직접 매핑
    2. 영문 단어 직접 매핑
    """
    matched = set()
    text_lower = text.lower()

    for keyword, descriptors in SENSORY_MAP.items():
        if keyword in text_lower:
            matched.update(descriptors)

    return list(matched)


def find_ingredients_by_descriptors(
    df: pd.DataFrame, target_descs: list, top_n: int = 8
) -> pd.DataFrame:
    """
    target_descs와 가장 많이 겹치는 원료 추천
    CURATED + MAPPED에서만 검색
    """
    eligible = df[
        df["data_source"].str.contains(
            "notion_manual|user|pubchem|pyrfume",
            case=False, na=False
        )
    ].copy()

    target_set = set(d.lower() for d in target_descs)

    def overlap_score(row):
        ing_descs = set(parse_descriptors(str(row.get("odor_descriptors", ""))))
        # sensory_notes 영문 키워드도 추가
        note_words = set(parse_sensory_notes(str(row.get("sensory_notes", ""))))
        combined = ing_descs | note_words
        return len(target_set & combined)

    eligible["_score"] = eligible.apply(overlap_score, axis=1)
    result = eligible[eligible["_score"] > 0].sort_values(
        "_score", ascending=False
    ).head(top_n)

    return result


def render_sensory_to_ingredient(df: pd.DataFrame):
    st.markdown("""
    <div class="sec-header">Sensory Language → Ingredients</div>
    <div class="sec-desc">
        감각적 인상을 자유롭게 입력하면 관련 원료를 추천합니다.<br>
        한국어·영어 모두 입력 가능합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;color:var(--muted);
                margin-bottom:1rem;padding:0.6rem 0;
                border-top:1px solid var(--rule);
                border-bottom:1px solid var(--rule);">
        작동 방식: sensory_notes 키워드 매핑 (외부 API 없음) ·
        추후 Claude API 연동 시 정확도 향상 가능
    </div>
    """, unsafe_allow_html=True)

    user_input = st.text_area(
        "",
        placeholder="예: 비 오는 날 젖은 숲, 따뜻한 나무 냄새, 상큼한 아침",
        height=100,
        label_visibility="collapsed",
        key="sensory_input"
    )

    if not user_input.strip():
        st.markdown("""
        <div class="empty-state">
            위에 감각적 인상을 입력하세요.
        </div>
        """, unsafe_allow_html=True)
        return

    # descriptor 매핑
    matched_descs = text_to_descriptors(user_input)

    if not matched_descs:
        st.markdown("""
        <div class="empty-state">
            매칭되는 descriptor가 없습니다.
            다른 표현을 시도해보세요.<br>
            예: 숲, 꽃, 달콤, 상큼, 따뜻, 바다, 나무
        </div>
        """, unsafe_allow_html=True)
        return

    # 매칭 descriptor 태그 표시
    st.markdown('<div class="sec-label">Matched Odor Descriptors</div>',
                unsafe_allow_html=True)
    tags_html = "".join([
        f'<span class="stag stag-match">{d}</span>'
        for d in sorted(matched_descs)
    ])
    st.markdown(f'<div style="margin-bottom:1rem;">{tags_html}</div>',
                unsafe_allow_html=True)

    # 원료 추천
    rec_df = find_ingredients_by_descriptors(df, matched_descs, top_n=8)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="sec-label">Recommended Ingredients</div>',
                    unsafe_allow_html=True)

        if rec_df.empty:
            st.markdown(
                '<div class="empty-state">매칭 원료 없음</div>',
                unsafe_allow_html=True
            )
        else:
            for _, row in rec_df.iterrows():
                name  = row["name"]
                tier  = get_quality_tier(row.to_dict())
                vol   = str(row.get("volatility_class", "")).capitalize()
                descs = parse_descriptors(str(row.get("odor_descriptors", "")))
                score = int(row.get("_score", 0))

                # 매칭 descriptor 강조
                target_set = set(d.lower() for d in matched_descs)
                desc_html  = "".join([
                    f'<span class="stag{"  stag-match" if d in target_set else ""}">{d}</span>'
                    for d in descs[:5]
                ])

                badge = {"curated":"★★★","mapped":"★★☆","registered":"★☆☆"}.get(tier,"")
                st.markdown(f"""
                <div class="rec-row">
                    <div class="rec-name">{badge} {name}</div>
                    <div class="rec-meta">
                        {vol} note · {score}개 descriptor 매칭
                    </div>
                    <div style="margin-top:4px;">{desc_html}</div>
                </div>
                """, unsafe_allow_html=True)

            # 선택한 원료를 Blend에 추가 버튼
            st.markdown('<div style="margin-top:1rem;"></div>',
                        unsafe_allow_html=True)
            for _, row in rec_df.head(3).iterrows():
                name = row["name"]
                if name not in st.session_state.get("blend_names", []):
                    if st.button(f"+ {name} → Blend에 추가",
                                 key=f"to_blend_{name}"):
                        if "blend_names" not in st.session_state:
                            st.session_state.blend_names = []
                        if len(st.session_state.blend_names) < 8:
                            st.session_state.blend_names.append(name)
                            st.rerun()

    with c2:
        st.markdown('<div class="sec-label">Similar Perfumes</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="intel-placeholder">
            Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.<br>
            매칭 원료 조합 기반으로 유사 향수 3개를
            Parfumo 데이터에서 검색합니다.
        </div>
        """, unsafe_allow_html=True)

        # 검색 링크 — Parfumo 웹사이트 직접 검색
        if matched_descs:
            query = "+".join(matched_descs[:3])
            st.markdown(f"""
            <div style="font-size:12px;color:var(--muted);margin-top:1rem;">
                직접 검색:
                <a href="https://www.parfumo.com/search?search={query}"
                   target="_blank" style="color:var(--ink);">
                   Parfumo 검색 →
                </a>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Compose</div>
    <div class="pg-title">Blend</div>
    <div class="pg-sub">
        Compose a fragrance —
        explore how ingredients combine
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        return

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    # ── 기능 1: 조합 시뮬레이션 ─────────────
    render_blend_simulator(df)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 기능 2: 감각 언어 → 원료 변환 ───────
    render_sensory_to_ingredient(df)


if __name__ == "__main__":
    main()