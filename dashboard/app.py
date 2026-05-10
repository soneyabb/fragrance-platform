import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="Fragrance Intelligence Platform",
    page_icon="⚗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 사이드바 설정
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# 메인 홈 화면
def main():
    st.title("⚗️ Fragrance Intelligence Platform")
    
    st.markdown("""
    ### 프로젝트 소개
    이 플랫폼은 향수 원료 데이터 수집, 분석 및 트렌드 시각화를 위한 통합 인텔리전스 도구입니다.
    
    #### 주요 기능:
    * **원료 탐색기**: PubChem 등 다양한 소스로부터 수집된 성분 정보 확인
    * **향 분석**: 원료별 향기 특성 및 네트워크 시각화
    * **트렌드 분석**: Google Trends 및 Reddit 데이터를 통한 실시간 선호도 파악
    * **데이터 파이프라인**: 자동화된 수집 및 정제 시스템
    
    왼쪽 사이드바의 메뉴를 통해 각 분석 페이지로 이동할 수 있습니다.
    """)
    
    st.info("현재 시스템은 초기 구축 단계에 있습니다. 각 폴더에 스크립트를 추가하여 기능을 확장할 수 있습니다.")

if __name__ == "__main__":
    main()
