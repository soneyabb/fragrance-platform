import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import os

# 페이지 설정
st.set_page_config(page_title="Trend Insights", page_icon="📈", layout="wide")

# --- 공통 디자인 시스템 적용 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #fdfcfb;
    }

    /* 사이드바 통일 */
    [data-testid="stSidebar"] {
        background-color: #1e2022 !important;
    }
    [data-testid="stSidebarNav"] span { color: #f0ece6 !important; }

    /* 타이틀 및 설명 */
    .pg-title { font-size: 42px; font-weight: 800; color: #1e2022; margin-bottom: 0.5rem; }
    .pg-desc { color: #6b7280; margin-bottom: 2.5rem; font-size: 16px; }

    /* 상단 필터 바 */
    .top-bar {
        background: #f7f6f3;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e2ddd6;
        margin-bottom: 30px;
    }

    /* KPI 카드 스타일 (빈 박스 제거 확인) */
    .metric-row {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2ddd6;
        flex: 1;
        text-align: left;
    }
    .m-label {
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    .m-value {
        font-size: 24px;
        font-weight: 800;
        color: #1e2022;
    }
    .m-delta {
        font-size: 13px;
        font-weight: 600;
        margin-top: 5px;
    }
    .delta-up { color: #10b981; }
    .delta-down { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="pg-title">📈 Trend Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-desc">시장 반응 및 소셜 데이터 기반의 실시간 향료 트렌드를 파악합니다.</div>', unsafe_allow_html=True)

    # 상단 필터 바
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)
    db_path = "data/fragrance_db.sqlite"
    if os.path.exists(db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        ingredients_df = pd.read_sql("SELECT name FROM ingredients", conn)
        conn.close()
        ingredient_list = sorted(ingredients_df['name'].tolist())
    else:
        ingredient_list = ["Bergamot", "Lavender", "Sandalwood", "Rose", "Musk"]

    selected_ingredient = st.selectbox("Search Trend for Ingredient", ingredient_list)
    st.markdown('</div>', unsafe_allow_html=True)

    # 시뮬레이션 데이터 생성
    dates = [datetime.now() - timedelta(days=x) for x in range(365, 0, -1)]
    np.random.seed(sum(map(ord, selected_ingredient)))
    base_val = np.random.randint(20, 60)
    values = np.cumsum(np.random.randn(365)) + base_val
    values = np.clip(values, 0, 100)
    trend_df = pd.DataFrame({"Date": dates, "Interest": values})

    # --- KPI 섹션 ---
    curr_val = round(values[-1])
    delta = round(values[-1] - values[-30], 1)
    delta_class = "delta-up" if delta >= 0 else "delta-down"
    delta_sym = "+" if delta >= 0 else ""

    st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="m-label">Current Interest</div>
                <div class="m-value">{curr_val} / 100</div>
                <div class="m-delta {delta_class}">{delta_sym}{delta}% (vs last month)</div>
            </div>
            <div class="metric-card">
                <div class="m-label">Peak Season</div>
                <div class="m-value">{'Winter' if base_val % 2 == 0 else 'Summer'}</div>
                <div style="font-size:12px; color:#6b7280; margin-top:4px;">Seasonal Preference Peak</div>
            </div>
            <div class="metric-card">
                <div class="m-label">Regional Hotspot</div>
                <div class="m-value">Europe / NA</div>
                <div style="font-size:12px; color:#6b7280; margin-top:4px;">Highest Search Volume</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- 메인 차트 ---
    st.markdown(f'<div style="font-size: 18px; font-weight: 700; color: #4a4e54; margin-bottom: 20px;">Interest Trend: {selected_ingredient}</div>', unsafe_allow_html=True)
    fig = px.line(trend_df, x="Date", y="Interest", color_discrete_sequence=['#1e2022'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_family="Inter",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        margin=dict(t=10, b=0, l=0, r=0)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 이 페이지는 현재 시뮬레이션 데이터를 사용 중이며, 향후 실제 Google Trends API 연동 예정입니다.")

if __name__ == "__main__":
    main()
