"""
04_Market.py
------------
Sillage — Perfume Occurrence Analytics
데이터: Parfumo TidyTuesday CSV (2024-12-10)
       59,325 perfume profiles
시뮬레이션 데이터 없음 — 실데이터만 사용
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Market — Sillage",
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

/* KPI 그리드 */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    margin-bottom: 1.5rem;
}
.kpi-cell {
    background: white;
    padding: 1.2rem 1.5rem;
}
.kpi-val {
    font-family: 'DM Serif Display', serif;
    font-size: 28px; color: var(--ink);
    margin-bottom: 4px; line-height: 1;
}
.kpi-key {
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--muted);
}

/* note position 바 */
.pos-row { margin-bottom: 0.8rem; }
.pos-label {
    display: flex; justify-content: space-between;
    font-size: 12px; margin-bottom: 4px; color: var(--ink);
}
.pos-pct { color: var(--muted); }
.pos-bar-bg { background: var(--rule); height: 4px; border-radius: 2px; }
.pos-bar-fill { background: var(--ink); height: 4px; border-radius: 2px; }

/* 향수 카드 */
.perf-row {
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--rule);
}
.perf-name { font-size: 14px; font-weight: 500; color: var(--ink); }
.perf-meta { font-size: 12px; color: var(--muted); margin-top: 2px; }

/* 데이터 없음 */
.no-data {
    background: white;
    border: 1px solid var(--rule);
    border-left: 3px solid var(--gold);
    padding: 1.5rem 2rem;
    border-radius: 0 3px 3px 0;
    font-size: 13px;
    color: var(--muted);
    line-height: 1.8;
}

/* 출처 */
.source-block {
    font-size: 11px; color: var(--muted);
    line-height: 1.7; margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid var(--rule);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_ingredients():
    """원료 DB — CURATED 우선 정렬"""
    # 스크립트 위치 기준 절대 경로 생성
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    db_path = os.path.join(base_dir, "data", "fragrance_db.sqlite")
    
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(
        "SELECT name, data_source, odor_family FROM ingredients", conn
    )
    conn.close()
    # CURATED 우선 정렬
    def tier(src):
        s = str(src).lower()
        if "notion_manual" in s or "user" in s:
            return 0
        elif "pubchem" in s or "pyrfume" in s:
            return 1
        return 2
    df["_tier"] = df["data_source"].apply(tier)
    return df.sort_values("_tier").reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_parfumo():
    """
    Parfumo TidyTuesday CSV 로드
    경로: data/raw/parfumo_data.csv
    컬럼 (TidyTuesday 2024-12-10 기준):
      Name, Brand, Release_Year, Rating_Value, Top_Notes, Middle_Notes, Base_Notes
    notes_* 컬럼에 원료명이 쉼표 구분으로 저장됨
    """
    # 스크립트 위치 기준 절대 경로 생성
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    csv_path = os.path.join(base_dir, "data", "raw", "parfumo_data.csv")
    
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        st.error(f"Parfumo CSV 로드 오류: {e}")
        return pd.DataFrame()


def get_ingredient_market(parfumo_df: pd.DataFrame, ingredient_name: str):
    """
    특정 원료의 Parfumo 등장 데이터 추출
    반환: {
        total: int,
        rank: int,
        top_pct: float, mid_pct: float, base_pct: float,
        perfumes: DataFrame (name, brand, year, rating, position),
        by_year: DataFrame (year, count)
    }
    """
    if parfumo_df.empty:
        return None

    name_lower = ingredient_name.lower()

    # 각 노트 포지션별 등장 향수 추출
    def matches(cell):
        if pd.isna(cell):
            return False
        return name_lower in str(cell).lower()

    mask_top  = parfumo_df["Top_Notes"].apply(matches)
    mask_middle = parfumo_df["Middle_Notes"].apply(matches)
    mask_base = parfumo_df["Base_Notes"].apply(matches)
    mask_any  = mask_top | mask_middle | mask_base

    total = mask_any.sum()
    if total == 0:
        return {"total": 0}

    # Note position breakdown
    top_n  = mask_top.sum()
    mid_n  = mask_middle.sum()
    base_n = mask_base.sum()

    # 등장 향수 목록
    perf_rows = []
    for idx, row in parfumo_df[mask_any].iterrows():
        pos = []
        if matches(row.get("Top_Notes")):    pos.append("Top")
        if matches(row.get("Middle_Notes")): pos.append("Middle")
        if matches(row.get("Base_Notes")):   pos.append("Base")
        perf_rows.append({
            "name":     row.get("Name", "—"),
            "brand":    row.get("Brand", "—"),
            "year":     row.get("Release_Year", "—"),
            "rating":   row.get("Rating_Value", "—"),
            "position": " / ".join(pos),
        })

    perf_df = pd.DataFrame(perf_rows)

    # 연도별 트렌드
    if "year" in parfumo_df.columns:
        year_df = (
            perf_df[perf_df["year"].notna() & (perf_df["year"] != "—")]
            .copy()
        )
        year_df["year"] = pd.to_numeric(year_df["year"], errors="coerce")
        year_df = year_df[year_df["year"] >= 2000]
        by_year = (
            year_df.groupby("year").size()
            .reset_index(name="count")
            .sort_values("year")
        )
    else:
        by_year = pd.DataFrame()

    return {
        "total":    int(total),
        "top_n":    int(top_n),
        "mid_n":    int(mid_n),
        "base_n":   int(base_n),
        "top_pct":  round(top_n  / total * 100) if total else 0,
        "mid_pct":  round(mid_n  / total * 100) if total else 0,
        "base_pct": round(base_n / total * 100) if total else 0,
        "perfumes": perf_df,
        "by_year":  by_year,
    }


@st.cache_data(ttl=3600)
def get_top30_ingredients(_parfumo_df: pd.DataFrame, curated_names: list):
    """
    Parfumo 전체 원료 등장 빈도 Top 30 계산
    CURATED 원료 하이라이트
    """
    if _parfumo_df.empty:
        return pd.DataFrame()

    from collections import Counter
    counter = Counter()

    for col in ["Top_Notes", "Middle_Notes", "Base_Notes"]:
        if col not in _parfumo_df.columns:
            continue
        for cell in _parfumo_df[col].dropna():
            for item in str(cell).split(","):
                name = item.strip()
                if name:
                    counter[name] += 1

    top30 = pd.DataFrame(
        counter.most_common(30),
        columns=["ingredient", "count"]
    )
    top30["is_curated"] = top30["ingredient"].isin(curated_names)
    top30["rank"] = range(1, len(top30) + 1)
    return top30


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Market Analytics</div>
    <div class="pg-title">Market</div>
    <div class="pg-sub">
        Perfume Occurrence Analytics —
        based on 59,325 perfumes · Parfumo dataset (2024)
    </div>
    """, unsafe_allow_html=True)

    ing_df     = load_ingredients()
    parfumo_df = load_parfumo()

    # ── Parfumo CSV 없을 때 안내 ─────────────
    if parfumo_df.empty:
        st.markdown("""
        <div class="no-data">
            <strong>Parfumo 데이터셋이 아직 준비되지 않았습니다.</strong><br><br>
            아래 경로에 CSV를 배치하면 자동으로 반영됩니다.<br>
            <code>data/raw/parfumo_data.csv</code><br><br>
            출처: TidyTuesday 2024-12-10<br>
            <a href="https://github.com/rfordatascience/tidytuesday/tree/main/data/2024/2024-12-10"
               target="_blank">
               github.com/rfordatascience/tidytuesday
            </a><br><br>
            Non-commercial use only.
        </div>
        """, unsafe_allow_html=True)
        # CSV 없어도 원료 선택 UI는 표시
        parfumo_ready = False
    else:
        parfumo_ready = True

    if ing_df.empty:
        st.error("DB 파일 없음. processors/load_to_db.py 먼저 실행하세요.")
        return

    # 원료 목록 — CURATED 우선
    curated_names = ing_df[
        ing_df["data_source"].str.contains(
            "notion_manual|user", case=False, na=False
        )
    ]["name"].tolist()
    all_names = ing_df["name"].tolist()

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    # ── 원료 선택 ────────────────────────────
    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        selected = st.selectbox(
            "원료 선택",
            all_names,
            label_visibility="collapsed",
            help="CURATED 66개가 상단에 표시됩니다."
        )

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    # ── 원료별 Market 데이터 ─────────────────
    if parfumo_ready and selected:
        data = get_ingredient_market(parfumo_df, selected)

        if not data or data.get("total", 0) == 0:
            st.markdown(f"""
            <div class="no-data">
                <strong>{selected}</strong>는 Parfumo 데이터셋에서
                발견되지 않았습니다.<br>
                원료명 표기가 다를 수 있습니다.
                (예: "Bergamot" vs "Bergamot Oil")
            </div>
            """, unsafe_allow_html=True)
        else:
            total     = data["total"]
            parfumo_n = len(parfumo_df)

            # ── FREQUENCY SUMMARY ────────────
            st.markdown('<div class="sec-label">Frequency Summary</div>',
                        unsafe_allow_html=True)

            # 전체 원료 중 rank 계산
            top30 = get_top30_ingredients(parfumo_df, curated_names)
            rank_row = top30[top30["ingredient"].str.lower() == selected.lower()]
            rank_str = f"#{rank_row.iloc[0]['rank']}" if not rank_row.empty else "—"
            coverage = round(total / parfumo_n * 100, 1) if parfumo_n else 0

            st.markdown(f"""
            <div class="kpi-grid">
                <div class="kpi-cell">
                    <div class="kpi-val">{total:,}</div>
                    <div class="kpi-key">Total Appearances</div>
                </div>
                <div class="kpi-cell">
                    <div class="kpi-val">{rank_str}</div>
                    <div class="kpi-key">Global Rank (Top 30 기준)</div>
                </div>
                <div class="kpi-cell">
                    <div class="kpi-val">{coverage}%</div>
                    <div class="kpi-key">Coverage ({parfumo_n:,} perfumes)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── NOTE POSITION BREAKDOWN ──────
            st.markdown('<div class="sec-label">Note Position Breakdown</div>',
                        unsafe_allow_html=True)
            for label, pct in [
                ("Top note",    data["top_pct"]),
                ("Middle note", data["mid_pct"]),
                ("Base note",   data["base_pct"]),
            ]:
                st.markdown(f"""
                <div class="pos-row">
                    <div class="pos-label">
                        <span>{label}</span>
                        <span class="pos-pct">{pct}%</span>
                    </div>
                    <div class="pos-bar-bg">
                        <div class="pos-bar-fill" style="width:{pct}%;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ── RELEASE TREND ────────────────
            if not data["by_year"].empty:
                st.markdown('<div class="sec-label">Release Trend (2000–2024)</div>',
                            unsafe_allow_html=True)
                fig_year = px.line(
                    data["by_year"], x="year", y="count",
                    color_discrete_sequence=["#1a1a18"],
                )
                fig_year.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="DM Sans", color="#1a1a18"),
                    xaxis=dict(showgrid=False, title=""),
                    yaxis=dict(showgrid=True, gridcolor="#e4e0d8", title=""),
                    margin=dict(t=10, b=0, l=0, r=0),
                )
                st.plotly_chart(fig_year, use_container_width=True)

            # ── TOP PERFUMES ─────────────────
            st.markdown('<div class="sec-label">Top Perfumes Featuring This Ingredient</div>',
                        unsafe_allow_html=True)

            perf_df = data["perfumes"]
            if not perf_df.empty:
                # 평점 기준 정렬, 상위 10개
                if "rating" in perf_df.columns:
                    perf_df = perf_df.copy()
                    perf_df["rating_num"] = pd.to_numeric(
                        perf_df["rating"], errors="coerce"
                    )
                    perf_df = perf_df.sort_values(
                        "rating_num", ascending=False
                    ).head(10)

                for _, row in perf_df.iterrows():
                    rating_str = (
                        f"★ {row['rating']}" if row["rating"] != "—" else ""
                    )
                    st.markdown(f"""
                    <div class="perf-row">
                        <div class="perf-name">{row['name']}</div>
                        <div class="perf-meta">
                            {row['brand']} · {row['year']} ·
                            {row['position']} · {rating_str}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
                    평점 기준 상위 10개 표시
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── TOP 30 바 차트 ───────────────────────
    st.markdown('<div class="sec-label">Top 30 Ingredients by Occurrence</div>',
                unsafe_allow_html=True)

    if parfumo_ready:
        top30 = get_top30_ingredients(parfumo_df, curated_names)
        if not top30.empty:
            # CURATED 하이라이트 색상
            top30["color"] = top30["is_curated"].map({
                True:  "#1a1a18",   # 검정 — CURATED
                False: "#c4b59a",   # 연갈색 — 그 외
            })

            fig_bar = go.Figure(go.Bar(
                x=top30["count"],
                y=top30["ingredient"],
                orientation="h",
                marker_color=top30["color"],
                text=top30["count"].apply(lambda x: f"{x:,}"),
                textposition="outside",
            ))
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="DM Sans", color="#1a1a18"),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(autorange="reversed", title=""),
                margin=dict(t=10, b=0, l=0, r=80),
                height=700,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("""
            <div style="font-size:11px;color:var(--muted);">
                ■ <span style="color:#1a1a18;">검정</span> — CURATED 원료 &nbsp;
                ■ <span style="color:#c4b59a;">연갈색</span> — 그 외 원료
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="font-size:13px;color:var(--muted);padding:1rem 0;">
            Parfumo CSV 파이프라인 완성 후 자동 반영됩니다.
        </div>
        """, unsafe_allow_html=True)

    # ── 데이터 출처 ──────────────────────────
    st.markdown("""
    <div class="source-block">
        Source: Parfumo dataset via TidyTuesday (2024-12-10)<br>
        59,325 perfume profiles | Non-commercial use<br>
        Note: This reflects consumer perfume community data,
        not industry production volumes.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()