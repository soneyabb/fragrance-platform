import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(page_title="Note Analysis", page_icon="📊", layout="wide")

# --- 공통 디자인 시스템 적용 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #fdfcfb;
    }

    /* 사이드바 통일 (타이틀 제거) */
    [data-testid="stSidebar"] {
        background-color: #1e2022 !important;
    }
    [data-testid="stSidebarNav"] span { color: #f0ece6 !important; }

    /* 타이틀 및 설명 */
    .pg-title { font-size: 42px; font-weight: 800; color: #1e2022; margin-bottom: 0.5rem; }
    .pg-desc { color: #6b7280; margin-bottom: 2.5rem; font-size: 16px; }

    /* KPI 카드 스타일 */
    .metric-row {
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 30px;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2ddd6;
        flex: 1;
        text-align: center;
    }
    .m-label {
        font-size: 11px;
        font-weight: 700;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 5px;
    }
    .m-value {
        font-size: 26px;
        font-weight: 800;
        color: #1e2022;
    }

    /* 섹션 타이틀 */
    .section-ttl {
        font-size: 24px;
        font-weight: 800;
        color: #1e2022;
        margin: 40px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #1e2022;
    }
    
    .sub-ttl {
        font-size: 18px;
        font-weight: 700;
        color: #4a4e54;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ingredients", conn)
    conn.close()
    return df

def main():
    st.markdown('<div class="pg-title">📊 Note Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-desc">원료 데이터를 바탕으로 한 향기 분포 및 통계 분석입니다.</div>', unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 데이터 타입 변환
    df['preference_score'] = pd.to_numeric(df['preference_score'], errors='coerce')

    # --- KPI 섹션 ---
    total_ing = len(df)
    families = df['odor_family'].nunique()
    avg_pref = round(df['preference_score'].mean(), 2) if not df['preference_score'].dropna().empty else 0
    top_pct = f"{round((df['volatility_class'] == 'top').sum() / len(df) * 100)}%"

    st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card"><div class="m-label">Total Ingredients</div><div class="m-value">{total_ing}</div></div>
            <div class="metric-card"><div class="m-label">Odor Families</div><div class="m-value">{families}</div></div>
            <div class="metric-card"><div class="m-label">Avg Preference</div><div class="m-value">{avg_pref}</div></div>
            <div class="metric-card"><div class="m-label">Top Note %</div><div class="m-value">{top_pct}</div></div>
        </div>
    """, unsafe_allow_html=True)

    # --- 분석 섹션 1 ---
    st.markdown('<div class="section-ttl">Composition Distribution</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    muted_colors = ['#1e2022', '#4a4e54', '#9ca3af', '#e2ddd6', '#fef3e2', '#fcd9a0', '#bfdbfe', '#a7f3d0']

    with c1:
        st.markdown('<div class="sub-ttl">Distribution by Odor Family</div>', unsafe_allow_html=True)
        family_counts = df['odor_family'].value_counts().reset_index()
        family_counts.columns = ['Family', 'Count']
        fig_family = px.pie(family_counts, values='Count', names='Family', hole=0.5,
                           color_discrete_sequence=muted_colors)
        fig_family.update_layout(margin=dict(t=0, b=0, l=0, r=0), font_family="Inter")
        st.plotly_chart(fig_family, use_container_width=True)

    with c2:
        st.markdown('<div class="sub-ttl">Volatility Class Count</div>', unsafe_allow_html=True)
        vol_counts = df['volatility_class'].value_counts().reindex(['top', 'middle', 'base'], fill_value=0).reset_index()
        vol_counts.columns = ['Volatility', 'Count']
        fig_vol = px.bar(vol_counts, x='Volatility', y='Count', color='Volatility',
                        color_discrete_map={'top': '#e2ddd6', 'middle': '#1e2022', 'base': '#9ca3af'})
        fig_vol.update_layout(margin=dict(t=20, b=0, l=0, r=0), font_family="Inter", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_vol, use_container_width=True)

    # --- 분석 섹션 2 ---
    st.markdown('<div class="section-ttl">Detailed Insights</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        st.markdown('<div class="sub-ttl">Top Odor Descriptors</div>', unsafe_allow_html=True)
        all_descriptors = []
        for desc in df['odor_descriptors'].dropna():
            all_descriptors.extend([d.strip() for d in str(desc).split(',') if d.strip() not in ('image', 'nan', 'N/A', '')])
        
        desc_df = pd.Series(all_descriptors).value_counts().head(12).reset_index()
        desc_df.columns = ['Descriptor', 'Frequency']
        fig_desc = px.bar(desc_df, y='Descriptor', x='Frequency', orientation='h',
                         color='Frequency', color_continuous_scale='Greys')
        fig_desc.update_layout(margin=dict(t=20, b=0, l=0, r=0), font_family="Inter", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_desc, use_container_width=True)

    with c4:
        st.markdown('<div class="sub-ttl">Preference Distribution</div>', unsafe_allow_html=True)
        fig_pref = px.histogram(df, x="preference_score", nbins=6, 
                               labels={'preference_score': 'Score'},
                               color_discrete_sequence=['#1e2022'])
        fig_pref.update_layout(margin=dict(t=20, b=0, l=0, r=0), font_family="Inter", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pref, use_container_width=True)

if __name__ == "__main__":
    main()
