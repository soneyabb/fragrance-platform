"""
03_Connections.py
-----------------
Sillage — Ingredient × Industry × Odor Family Network
노드 색상 3종: CURATED(진파랑) / MAPPED(연파랑) / 산업(주황) / Family(초록)
엣지: 원료→산업 실선 / 원료→Family 점선
하단: Top Versatile / Most Exclusive / Family Clusters / Connectivity by Industry
"""

import streamlit as st
import pandas as pd
import sqlite3
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Connections — Sillage",
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
.section-rule {
    border: none; border-top: 1px solid var(--rule); margin: 2rem 0;
}

/* 범례 */
.legend-wrap {
    display: flex; flex-wrap: wrap; gap: 16px;
    margin-bottom: 1rem; font-size: 12px;
}
.legend-item {
    display: flex; align-items: center; gap: 6px;
    color: var(--ink);
}
.legend-dot {
    width: 10px; height: 10px;
    border-radius: 50%; flex-shrink: 0;
}
.legend-diamond {
    width: 10px; height: 10px;
    transform: rotate(45deg); flex-shrink: 0;
}

/* 인사이트 카드 */
.insight-row {
    display: flex; justify-content: space-between;
    align-items: center;
    padding: 0.7rem 0;
    border-bottom: 1px solid var(--rule);
    font-size: 13px;
}
.insight-rank { color: var(--muted); min-width: 24px; }
.insight-name { font-weight: 500; flex: 1; padding: 0 12px; }
.insight-count { color: var(--muted); font-size: 12px; }

/* 클릭 안내 */
.click-note {
    font-size: 11px; color: var(--muted);
    padding: 0.6rem 0; margin-bottom: 1rem;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
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
# 노드 색상 상수
# ─────────────────────────────────────────
COLOR_CURATED    = "#1e40af"   # 진파랑 — CURATED 원료
COLOR_MAPPED     = "#93c5fd"   # 연파랑 — MAPPED 원료
COLOR_REGISTERED = "#dbeafe"   # 더 연한 파랑 — REGISTERED
COLOR_INDUSTRY   = "#f97316"   # 주황 — 산업 카테고리
COLOR_FAMILY     = "#16a34a"   # 초록 — Odor Family

INDUSTRY_LABEL = {
    "perfume":        "Fine Fragrance",
    "cosmetic":       "Cosmetic",
    "food":           "Food",
    "tea_coffee":     "Tea & Coffee",
    "home_scent":     "Home Scent",
    "fabric":         "Fabric Care",
    "pharmaceutical": "Pharmaceutical",
}

FAMILY_EMOJI = {
    "Citrus":"🍊","Fruity":"🥭","Green":"🌱","Herbal":"🌿","Floral":"🌸",
    "Aldehyde":"🧼","Animal":"🐾","Woody":"🪵","Mossy":"🪨",
    "Spicy":"🫚","Balsamic":"🍯",
}


# ─────────────────────────────────────────
# 데이터 로드
# name, industry_usage, odor_family, data_source만 로드
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
    df = pd.read_sql(
        "SELECT name, industry_usage, odor_family, data_source FROM ingredients",
        conn
    )
    conn.close()
    return df


# ─────────────────────────────────────────
# 헬퍼
# ─────────────────────────────────────────
def get_quality_tier(data_source: str) -> str:
    src = str(data_source).lower()
    if "notion_manual" in src or "user" in src:
        return "curated"
    elif "pubchem" in src or "pyrfume" in src:
        return "mapped"
    return "registered"

def node_color(tier: str) -> str:
    return {
        "curated":    COLOR_CURATED,
        "mapped":     COLOR_MAPPED,
        "registered": COLOR_REGISTERED,
    }.get(tier, COLOR_REGISTERED)

def node_size_by_tier(tier: str) -> int:
    # Parfumo occurrence 없으므로 tier 기반 임시 크기
    # 파이프라인 완성 후 occurrence rank 기반으로 교체
    return {"curated": 20, "mapped": 14, "registered": 10}.get(tier, 10)


# ─────────────────────────────────────────
# 네트워크 그래프 생성
# ─────────────────────────────────────────
def build_network(df, selected_industries, selected_families,
                  show_family_edges: bool) -> Network:
    """
    노드 타입:
      원료 노드 — 원형, tier 색상
      산업 노드 — 다이아몬드, 주황
      Family 노드 — 삼각형, 초록

    엣지:
      원료 → 산업: 실선 (width=1.5)
      원료 → Family: 점선 (dashes=True, width=1)

    클릭 인터랙션:
      PyVis title 속성 → hover 시 원료 정보 표시
      노드 클릭 → JS로 Streamlit URL 이동 시도
      (Streamlit Cloud 보안 정책에 따라 제한될 수 있음)
    """
    G = nx.Graph()

    for _, row in df.iterrows():
        name   = row["name"]
        tier   = get_quality_tier(str(row.get("data_source", "")))
        family = str(row.get("odor_family", "")).strip()
        usages = [u.strip() for u in str(row["industry_usage"]).split(",")
                  if u.strip() and u.strip() in selected_industries]

        # Family 필터 적용
        if selected_families and family not in selected_families:
            continue

        if not usages:
            continue

        # 원료 노드
        G.add_node(
            name,
            color=node_color(tier),
            size=node_size_by_tier(tier),
            shape="dot",
            title=f"{name}\nTier: {tier}\nFamily: {family}\nIndustries: {', '.join(usages)}",
            node_type="ingredient",
            tier=tier,
        )

        # 산업 노드 + 엣지 (실선)
        for usage in usages:
            label = INDUSTRY_LABEL.get(usage, usage)
            G.add_node(
                usage,
                color=COLOR_INDUSTRY,
                size=28,
                shape="diamond",
                title=label,
                node_type="industry",
            )
            G.add_edge(name, usage, width=1.5, dashes=False, color="#c4b59a")

        # Family 노드 + 엣지 (점선)
        if show_family_edges and family and family not in ("N/A", "nan", ""):
            emoji = FAMILY_EMOJI.get(family, "")
            G.add_node(
                f"family_{family}",
                label=f"{emoji} {family}",
                color=COLOR_FAMILY,
                size=22,
                shape="triangle",
                title=f"Odor Family: {family}",
                node_type="family",
            )
            G.add_edge(name, f"family_{family}",
                       width=1, dashes=True, color="#a7f3d0")

    # PyVis 생성
    nt = Network(
        height="620px", width="100%",
        bgcolor="#faf9f7", font_color="#1a1a18"
    )
    nt.from_nx(G)

    # 물리 엔진 설정 — forceAtlas2 기반
    nt.set_options("""
    {
      "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
          "gravitationalConstant": -80,
          "springLength": 120,
          "springConstant": 0.05,
          "damping": 0.9
        },
        "stabilization": { "iterations": 200 }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 100
      }
    }
    """)

    return nt


# ─────────────────────────────────────────
# 인사이트 패널
# ─────────────────────────────────────────
def render_insights(df, G, selected_industries):

    # 산업 노드 키 집합
    industry_keys = set(INDUSTRY_LABEL.keys())

    # 원료 노드만 추출
    ingredient_nodes = [
        n for n in G.nodes()
        if G.nodes[n].get("node_type") == "ingredient"
    ]

    degrees = dict(G.degree())

    # ── Top Versatile (산업 연결 수 기준) ─────
    versatile = sorted(
        ingredient_nodes,
        key=lambda x: len([nb for nb in G.neighbors(x)
                           if nb in industry_keys]),
        reverse=True
    )[:5]

    # ── Most Exclusive (1개 산업에만 연결) ────
    exclusive = [
        n for n in ingredient_nodes
        if len([nb for nb in G.neighbors(n)
                if nb in industry_keys]) == 1
    ]

    # ── Connectivity by Industry ───────────
    industry_counts = {}
    for ind in selected_industries:
        if ind in G:
            industry_counts[ind] = len([
                nb for nb in G.neighbors(ind)
                if G.nodes[nb].get("node_type") == "ingredient"
            ])

    # ── Odor Family Clusters ───────────────
    family_industry = {}
    for _, row in df.iterrows():
        family = str(row.get("odor_family", "")).strip()
        usages = [u.strip() for u in str(row["industry_usage"]).split(",")
                  if u.strip() in industry_keys]
        if family and family not in ("N/A", "nan", ""):
            if family not in family_industry:
                family_industry[family] = set()
            family_industry[family].update(usages)

    # ── 렌더링 ────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        # Top Versatile
        st.markdown('<div class="sec-label">Top Versatile</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:var(--muted);margin-bottom:0.5rem;">'
            '가장 많은 산업에 연결된 원료</div>',
            unsafe_allow_html=True
        )
        if versatile:
            for i, name in enumerate(versatile, 1):
                ind_count = len([nb for nb in G.neighbors(name)
                                 if nb in industry_keys])
                st.markdown(f"""
                <div class="insight-row">
                    <span class="insight-rank">{i}</span>
                    <span class="insight-name">{name}</span>
                    <span class="insight-count">{ind_count}개 산업</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty-state">데이터 없음</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div style="margin-top:1.5rem;"></div>',
                    unsafe_allow_html=True)

        # Odor Family Clusters
        st.markdown('<div class="sec-label">Odor Family Clusters</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:var(--muted);margin-bottom:0.5rem;">'
            '같은 Odor Family 원료들의 산업 분포</div>',
            unsafe_allow_html=True
        )
        for family, industries in sorted(family_industry.items()):
            emoji = FAMILY_EMOJI.get(family, "")
            ind_labels = ", ".join([
                INDUSTRY_LABEL.get(i, i) for i in sorted(industries)
            ])
            st.markdown(f"""
            <div class="insight-row">
                <span class="insight-name">
                    {emoji} {family}
                </span>
                <span class="insight-count">{ind_labels}</span>
            </div>
            """, unsafe_allow_html=True)

    with c2:
        # Most Exclusive
        st.markdown('<div class="sec-label">Most Exclusive</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:var(--muted);margin-bottom:0.5rem;">'
            '특정 산업에만 사용되는 원료</div>',
            unsafe_allow_html=True
        )
        if exclusive:
            for name in exclusive[:8]:
                only_ind = [nb for nb in G.neighbors(name)
                            if nb in industry_keys]
                label = INDUSTRY_LABEL.get(only_ind[0], only_ind[0]) \
                    if only_ind else "—"
                st.markdown(f"""
                <div class="insight-row">
                    <span class="insight-name">{name}</span>
                    <span class="insight-count">{label}만</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty-state">해당 없음</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div style="margin-top:1.5rem;"></div>',
                    unsafe_allow_html=True)

        # Connectivity by Industry
        st.markdown('<div class="sec-label">Connectivity by Industry</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:11px;color:var(--muted);margin-bottom:0.5rem;">'
            '각 산업에 연결된 원료 수</div>',
            unsafe_allow_html=True
        )
        for ind, count in sorted(
            industry_counts.items(), key=lambda x: x[1], reverse=True
        ):
            label = INDUSTRY_LABEL.get(ind, ind)
            pct   = round(count / len(ingredient_nodes) * 100) \
                if ingredient_nodes else 0
            st.markdown(f"""
            <div class="insight-row">
                <span class="insight-name">{label}</span>
                <span class="insight-count">{count}개 원료 ({pct}%)</span>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Network</div>
    <div class="pg-title">Connections</div>
    <div class="pg-sub">
        Ingredient × Industry × Odor Family network
    </div>
    """, unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        return

    # ── 필터 ────────────────────────────────
    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    f1, f2, f3 = st.columns([1, 2, 2])

    with f1:
        tier_filter = st.radio(
            "Tier",
            ["CURATED만", "MAPPED 포함", "전체"],
            index=2,
            key="tier_filter"
        )

    with f2:
        all_industries = list(INDUSTRY_LABEL.keys())
        selected_industries = st.multiselect(
            "Industry",
            all_industries,
            default=[i for i in all_industries if i != "perfume"],
            format_func=lambda x: INDUSTRY_LABEL.get(x, x),
            key="ind_filter"
        )

    with f3:
        all_families = sorted([
            f for f in df["odor_family"].dropna().unique()
            if f not in ("N/A", "nan")
        ])
        selected_families = st.multiselect(
            "Odor Family",
            all_families,
            default=[],
            key="fam_filter"
        )

    show_family_edges = st.toggle(
        "Odor Family 연결선 표시",
        value=False,
        key="family_edge_toggle"
    )

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    # Tier 필터 적용
    filtered_df = df.copy()
    if tier_filter == "CURATED만":
        filtered_df = filtered_df[
            filtered_df["data_source"].str.contains(
                "notion_manual|user", case=False, na=False
            )
        ]
    elif tier_filter == "MAPPED 포함":
        filtered_df = filtered_df[
            filtered_df["data_source"].str.contains(
                "notion_manual|user|pubchem|pyrfume",
                case=False, na=False
            )
        ]

    if not selected_industries:
        st.info("산업 카테고리를 하나 이상 선택하세요.")
        return

    # ── 범례 ────────────────────────────────
    st.markdown("""
    <div class="legend-wrap">
        <div class="legend-item">
            <div class="legend-dot" style="background:#1e40af;"></div>
            CURATED 원료
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#93c5fd;"></div>
            MAPPED 원료
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#dbeafe;border:1px solid #93c5fd;"></div>
            REGISTERED 원료
        </div>
        <div class="legend-item">
            <div class="legend-diamond" style="background:#f97316;"></div>
            산업 카테고리
        </div>
        <div class="legend-item">
            <div class="legend-dot" style="background:#16a34a;
                 clip-path:polygon(50% 0%,100% 100%,0% 100%);
                 border-radius:0;"></div>
            Odor Family
        </div>
    </div>
    <div class="click-note">
        노드에 마우스를 올리면 상세 정보가 표시됩니다.
        노드 크기: CURATED &gt; MAPPED &gt; REGISTERED
        (Parfumo occurrence 파이프라인 완성 후 실빈도 기반으로 교체)
    </div>
    """, unsafe_allow_html=True)

    # ── 네트워크 생성 및 렌더링 ─────────────
    nt = build_network(
        filtered_df,
        selected_industries,
        selected_families,
        show_family_edges
    )

    try:
        temp_dir = "dashboard/temp"
        os.makedirs(temp_dir, exist_ok=True)
        path = os.path.join(temp_dir, "network.html")
        nt.save_graph(path)
        with open(path, "r", encoding="utf-8") as f:
            components.html(f.read(), height=640)
    except Exception as e:
        st.error(f"네트워크 렌더링 오류: {e}")

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 인사이트 패널 ────────────────────────
    st.markdown('<div class="sec-label">Network Insights</div>',
                unsafe_allow_html=True)

    # G 재구성 (인사이트용)
    G_insight = nx.Graph()
    for _, row in filtered_df.iterrows():
        name   = row["name"]
        tier   = get_quality_tier(str(row.get("data_source", "")))
        family = str(row.get("odor_family", "")).strip()
        usages = [u.strip() for u in str(row["industry_usage"]).split(",")
                  if u.strip() and u.strip() in selected_industries]
        if selected_families and family not in selected_families:
            continue
        if not usages:
            continue
        G_insight.add_node(name, node_type="ingredient", tier=tier)
        for usage in usages:
            G_insight.add_node(usage, node_type="industry")
            G_insight.add_edge(name, usage)

    render_insights(filtered_df, G_insight, selected_industries)


if __name__ == "__main__":
    main()