import streamlit as st
import os

# 페이지 설정
st.set_page_config(
    page_title="Fragrance Intelligence Platform",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 공통 디자인 시스템 CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    /* 전체 배경 및 폰트 */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background-color: #fdfcfb;
    }

    /* 사이드바 통일 (타이틀/푸터 제거용) */
    [data-testid="stSidebar"] {
        background-color: #1e2022 !important;
    }
    [data-testid="stSidebarNav"] span {
        color: #f0ece6 !important;
        font-weight: 500;
    }

    /* Hero Section */
    .hero-container {
        background: #1e2022;
        padding: 2.5rem 3rem;
        border-radius: 20px;
        color: #f0ece6;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 12px;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        font-size: 16px;
        font-weight: 300;
        opacity: 0.85;
        line-height: 1.6;
    }

    /* 2x2 카드 그리드 시스템 */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        max-width: 1000px; /* 너무 퍼지지 않게 제한 */
    }
    .f-card {
        background: white;
        padding: 1.8rem;
        border-radius: 16px;
        border: 1px solid #e2ddd6;
        transition: all 0.3s ease;
        text-decoration: none !important;
        color: #1e2022 !important;
        display: flex;
        flex-direction: column;
    }
    .f-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(30, 32, 34, 0.05);
        border-color: #1e2022;
    }
    .f-icon { font-size: 32px; margin-bottom: 15px; }
    .f-title { font-size: 19px; font-weight: 700; margin-bottom: 8px; white-space: nowrap; }
    .f-desc { font-size: 14px; color: #6b7280; line-height: 1.5; }

    /* 스테이터스 바 */
    .status-bar {
        background: #f7f6f3;
        padding: 8px 20px;
        border-radius: 100px;
        display: inline-flex;
        align-items: center;
        gap: 15px;
        font-size: 12px;
        font-weight: 600;
        color: #4a4e54;
        margin-bottom: 1.5rem;
        border: 1px solid #e2ddd6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # 상단 스테이터스
    st.markdown("""
        <div class="status-bar">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width:6px; height:6px; background:#10b981; border-radius:50%;"></div> Platform Active
            </div>
            <div style="color: #e2ddd6;">|</div>
            <div>Latest Data: May 2026</div>
        </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown("""
        <div class="hero-container">
            <div class="hero-title">Fragrance Intelligence</div>
            <div class="hero-subtitle">
                데이터 기반의 감각 분석과 실시간 트렌드를 통해 
                미래의 향을 설계하는 통합 인텔리전스 시스템입니다.
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Feature Cards (2x2 배정)
    st.markdown("""
        <div class="feature-grid">
            <a href="/ingredient_explorer" class="f-card" target="_self">
                <div class="f-icon">🧪</div>
                <div class="f-title">🔍 Ingredient Explorer</div>
                <div class="f-desc">화학적 데이터와 조향 노트를 결합한 원료 라이브러리입니다.</div>
            </a>
            <a href="/note_analysis" class="f-card" target="_self">
                <div class="f-icon">📊</div>
                <div class="f-title">📊 Note Analysis</div>
                <div class="f-desc">원료별 휘발도와 향기 분포를 시각적으로 분석합니다.</div>
            </a>
            <a href="/trend_chart" class="f-card" target="_self">
                <div class="f-icon">📈</div>
                <div class="f-title">📈 Trend Insights</div>
                <div class="f-desc">소셜 데이터 기반의 실시간 향료 트렌드를 파악합니다.</div>
            </a>
            <a href="/network_graph" class="f-card" target="_self">
                <div class="f-icon">🕸️</div>
                <div class="f-title">🕸️ Note Network</div>
                <div class="f-desc">원료 간의 상보성 및 연결 관계를 시각화합니다.</div>
            </a>
        </div>
    """, unsafe_allow_html=True)

    # 사이드바 타이틀/푸터 제거됨 (내비게이션만 유지)

if __name__ == "__main__":
    main()
