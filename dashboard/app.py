import streamlit as st
import os
import sqlite3

# 페이지 설정
st.set_page_config(
    page_title="Fragrance Intelligence Platform",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 데이터베이스 통계 추출 ---
def get_db_stats():
    db_path = "data/fragrance_db.sqlite"
    stats = {"total": 0, "pubchem": 0, "industry_count": 7}
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 총 원료 수
            cursor.execute("SELECT COUNT(*) FROM ingredients")
            stats["total"] = cursor.fetchone()[0]
            
            # PubChem 데이터 수집 완료 수 (N/A, 빈값 제외)
            cursor.execute("SELECT COUNT(*) FROM ingredients WHERE pubchem_cid IS NOT NULL AND pubchem_cid != '' AND pubchem_cid != 'N/A'")
            stats["pubchem"] = cursor.fetchone()[0]
            
            conn.close()
        except Exception as e:
            st.error(f"DB Error: {e}")
    return stats

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
        text-transform: capitalize;
    }

    /* 사이드바의 'app' 글자를 'Fragrance Intelligence'로 교체 */
    [data-testid="stSidebarNav"] ul li:first-child span {
        visibility: hidden;
        position: relative;
    }
    [data-testid="stSidebarNav"] ul li:first-child span::after {
        content: "Fragrance Intelligence";
        visibility: visible;
        position: absolute;
        left: 0;
        top: 0;
        white-space: nowrap;
    }

    /* Hero Section */
    .hero-container {
        background: #1e2022;
        padding: 3.5rem 3.5rem 2.5rem 3.5rem;
        border-radius: 24px;
        color: #f0ece6;
        margin-bottom: 2.5rem;
        position: relative;
    }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 12px;
        letter-spacing: -0.04em;
    }
    .hero-subtitle {
        font-size: 17px;
        font-weight: 300;
        opacity: 0.8;
        line-height: 1.6;
        max-width: 800px;
        margin-bottom: 2rem;
    }

    /* 실시간 통계 바 (헤더 내 배치) */
    .hero-stats {
        display: flex;
        gap: 25px;
        font-size: 14px;
        font-weight: 500;
        color: rgba(240, 236, 230, 0.6);
        padding-top: 1.5rem;
        border-top: 1px solid rgba(240, 236, 230, 0.1);
    }
    .hero-stats b {
        color: #ffffff;
    }

    /* 2x2 카드 그리드 시스템 */
    .feature-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 25px;
        max-width: 1100px;
    }
    .f-card {
        background: white;
        padding: 2.2rem;
        border-radius: 20px;
        border: 1px solid #e2ddd6;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        text-decoration: none !important;
        color: #1e2022 !important;
        display: flex;
        flex-direction: column;
    }
    .f-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(30, 32, 34, 0.08);
        border-color: #1e2022;
    }
    .f-icon { font-size: 36px; margin-bottom: 18px; }
    .f-title { font-size: 21px; font-weight: 700; margin-bottom: 10px; }
    .f-desc { font-size: 15px; color: #6b7280; line-height: 1.6; }

    /* 스테이터스 바 (상단) */
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
    # 데이터 로드
    stats = get_db_stats()

    # 상단 스테이터스
    st.markdown("""
        <div class="status-bar">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width:6px; height:6px; background:#10b981; border-radius:50%;"></div> Platform Active
            </div>
            <div style="color: #e2ddd6;">|</div>
            <div>Latest Data Sync: May 2026</div>
        </div>
    """, unsafe_allow_html=True)

    # Hero Section
    st.markdown(f"""
        <div class="hero-container">
            <div class="hero-title">Fragrance Intelligence</div>
            <div class="hero-subtitle">
                향료 원료의 화학 데이터, 감각 노트, 산업 트렌드를 하나의 플랫폼에서 탐색하는 조향 인텔리전스 도구입니다.
            </div>
            <div class="hero-stats">
                <div><b>{stats['total']}</b>개 원료</div>
                <div style="color: rgba(240, 236, 230, 0.2);">·</div>
                <div><b>{stats['pubchem']}</b>개 화학데이터</div>
                <div style="color: rgba(240, 236, 230, 0.2);">·</div>
                <div><b>{stats['industry_count']}</b>개 산업군</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Feature Cards (2x2 배정)
    st.markdown("""
        <div class="feature-grid">
            <a href="/Ingredient_Explorer" class="f-card" target="_self">
                <div class="f-icon">⚗️</div>
                <div class="f-title">Ingredient Explorer</div>
                <div class="f-desc">화학적 데이터와 조향 노트를 결합한 원료 라이브러리입니다.</div>
            </a>
            <a href="/Note_Analysis" class="f-card" target="_self">
                <div class="f-icon">📊</div>
                <div class="f-title">Note Analysis</div>
                <div class="f-desc">원료 데이터를 바탕으로 한 향 분포 및 통계 분석입니다.</div>
            </a>
            <a href="/Trend_Insights" class="f-card" target="_self">
                <div class="f-icon">📈</div>
                <div class="f-title">Trend Insights</div>
                <div class="f-desc">시장 반응 및 소셜 데이터 기반의 실시간 향료 트렌드를 파악합니다.</div>
            </a>
            <a href="/Note_Network" class="f-card" target="_self">
                <div class="f-icon">🕸️</div>
                <div class="f-title">Note Network</div>
                <div class="f-desc">원료와 산업군 간의 관계를 시각화하여 범용성과 새로운 향기 조합의 가능성을 분석합니다.</div>
            </a>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
