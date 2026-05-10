import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(page_title="Trend Chart", page_icon="📈", layout="wide")

def main():
    st.title("📈 Trend Chart (트렌드 분석)")
    st.markdown("---")

    st.info("""
    **Note:** 이 페이지는 향후 Google Trends 및 Reddit API 연동을 통해 실시간 시장 트렌드를 시각화할 예정입니다.
    현재는 시연을 위한 시뮬레이션 데이터를 표시합니다.
    """)

    # 원료 선택
    db_path = "data/processed/ingredients.csv"
    if os.path.exists(db_path):
        ingredients_df = pd.read_csv(db_path)
        ingredient_list = sorted(ingredients_df['name'].tolist())
    else:
        ingredient_list = ["Bergamot", "Lavender", "Sandalwood", "Rose", "Musk"]

    selected_ingredient = st.selectbox("분석할 원료를 선택하세요", ingredient_list)

    # 시뮬레이션 데이터 생성
    dates = [datetime.now() - timedelta(days=x) for x in range(365, 0, -1)]
    
    # 랜덤 워크 기반 트렌드 생성
    np.random.seed(sum(map(ord, selected_ingredient))) # 원료명에 따른 고정된 랜덤 패턴
    base_val = np.random.randint(20, 60)
    values = np.cumsum(np.random.randn(365)) + base_val
    values = np.clip(values, 0, 100) # 0-100 범위로 제한

    trend_df = pd.DataFrame({
        "Date": dates,
        "Search Interest": values
    })

    # 트렌드 시각화
    st.subheader(f"Search Interest Trend: {selected_ingredient}")
    fig = px.line(trend_df, x="Date", y="Search Interest", 
                 title=f"Google Trends Simulation for '{selected_ingredient}' (Last 12 Months)",
                 color_discrete_sequence=['#FF4B4B'])
    fig.update_layout(hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    # 추가 인사이트 (Mock)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Trend", f"{round(values[-1])}", f"{round(values[-1] - values[-30])}%")
    c2.metric("Peak Season", "Winter" if base_val % 2 == 0 else "Summer")
    c3.metric("Regional Interest", "Western Europe / North America")

    st.markdown("---")
    st.subheader("Upcoming Features")
    st.markdown("""
    - **Google Trends API 연동**: 실시간 검색량 추이 및 관련 검색어 분석
    - **Reddit/Twitter Sentiment Analysis**: 소셜 미디어상의 감성 분석 및 언급량 추적
    - **AWS Lambda & EventBridge**: 매일 자정 자동으로 트렌드 데이터 갱신
    """)

import os
if __name__ == "__main__":
    main()
