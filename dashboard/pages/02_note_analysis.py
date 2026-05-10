import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(page_title="Note Analysis", page_icon="📊", layout="wide")

def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ingredients", conn)
    conn.close()
    return df

def main():
    st.title("📊 Note Analysis (향 노트 분석)")
    st.markdown("---")

    df = load_data()
    if df.empty:
        st.warning("데이터가 없습니다. 데이터 적재를 먼저 완료해주세요.")
        return

    # 대시보드 요약 지표
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Ingredients", len(df))
    col2.metric("Odor Families", df['odor_family'].nunique())
    col3.metric("Avg Preference", round(df['preference_score'].mean(), 2))
    col4.metric("Top Note %", f"{round((df['volatility_class'] == 'top').sum() / len(df) * 100)}%")

    st.markdown("---")

    # 차트 레이아웃
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Distribution by Odor Family")
        family_counts = df['odor_family'].value_counts().reset_index()
        family_counts.columns = ['Family', 'Count']
        fig_family = px.pie(family_counts, values='Count', names='Family', hole=0.4,
                           color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_family, use_container_width=True)

    with c2:
        st.subheader("Volatility Class Count")
        vol_counts = df['volatility_class'].value_counts().reindex(['top', 'middle', 'base'], fill_value=0).reset_index()
        vol_counts.columns = ['Volatility', 'Count']
        fig_vol = px.bar(vol_counts, x='Volatility', y='Count', color='Volatility',
                        color_discrete_map={'top': '#FF9E9E', 'middle': '#9E9EFF', 'base': '#9EFF9E'})
        st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("---")

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Top Odor Descriptors")
        # 모든 descriptors 추출 및 카운트
        all_descriptors = []
        for desc in df['odor_descriptors'].dropna():
            all_descriptors.extend([d.strip() for d in desc.split(',') if d.strip() != 'image'])
        
        desc_df = pd.Series(all_descriptors).value_counts().head(15).reset_index()
        desc_df.columns = ['Descriptor', 'Frequency']
        fig_desc = px.bar(desc_df, y='Descriptor', x='Frequency', orientation='h',
                         color='Frequency', color_continuous_scale='Viridis')
        st.plotly_chart(fig_desc, use_container_width=True)

    with c4:
        st.subheader("Preference Score Distribution")
        fig_pref = px.histogram(df, x="preference_score", nbins=6, 
                               labels={'preference_score': 'Score'},
                               color_discrete_sequence=['#FECB52'])
        st.plotly_chart(fig_pref, use_container_width=True)

if __name__ == "__main__":
    main()
