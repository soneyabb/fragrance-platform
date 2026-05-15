import streamlit as st
import pandas as pd
import sqlite3
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os

# 페이지 설정
st.set_page_config(page_title="Note Network", page_icon="🕸️", layout="wide")

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

    /* 인사이트 섹션 (빈 박스 제거 및 스타일 조정) */
    .insight-container {
        margin-top: 40px;
    }
    .insight-ttl {
        font-size: 18px;
        font-weight: 700;
        color: #1e2022;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .insight-item {
        font-size: 14px;
        color: #4a4e54;
        margin-bottom: 8px;
        padding-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT name, industry_usage, odor_family FROM ingredients", conn)
    conn.close()
    return df

def main():
    st.markdown('<div class="pg-title">🕸️ Note Network</div>', unsafe_allow_html=True)
    st.markdown('<div class="pg-desc">원료와 산업군 간의 관계를 시각화하여 범용성과 새로운 향기 조합의 가능성을 분석합니다.</div>', unsafe_allow_html=True)

    df = load_data()
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 산업 분야 컬러 매핑 (요청된 색상 반영)
    industry_colors = {
        "perfume": "#1e2022", 
        "cosmetic": "#1e40af", 
        "food": "#2d6a4f",
        "tea_coffee": "#92400e", 
        "home_scent": "#4a1d96", 
        "fabric": "#6b7280",
        "pharmaceutical": "#065f46"
    }

    # 상단 필터 바 (perfume 제외한 6개 산업군 기본 선택)
    default_selected = [ind for ind in industry_colors.keys() if ind != "perfume"]
    
    st.markdown('<div class="top-bar">', unsafe_allow_html=True)
    selected_industries = st.multiselect(
        "Select Industries to Analyze Connectivity", 
        list(industry_colors.keys()), 
        default=default_selected
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # 네트워크 생성
    G = nx.Graph()
    for _, row in df.iterrows():
        ingredient = row['name']
        usages = [u.strip() for u in str(row['industry_usage']).split(',') if u.strip()]
        valid_usages = [u for u in usages if u in selected_industries]
        
        if valid_usages:
            # 연결 수에 따른 노드 크기 결정 (1개:10, 2개:15, 3개 이상:20)
            conn_count = len(valid_usages)
            if conn_count == 1:
                node_size = 10
            elif conn_count == 2:
                node_size = 15
            else:
                node_size = 20
                
            G.add_node(ingredient, color="#CCCCCC", size=node_size, title=f"Family: {row['odor_family']} ({conn_count} industries)")
            for usage in valid_usages:
                G.add_node(usage, color=industry_colors.get(usage, "#000000"), size=25, shape="diamond")
                G.add_edge(ingredient, usage)

    # 그래프 렌더링
    st.markdown('<div style="font-size: 18px; font-weight: 700; color: #4a4e54; margin-bottom: 15px;">Industrial Connectivity Map</div>', unsafe_allow_html=True)
    nt = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#1e2022")
    nt.from_nx(G)
    nt.set_options('{"physics": {"forceAtlas2Based": {"gravitationalConstant": -100, "springLength": 100}, "solver": "forceAtlas2Based"}}')
    
    try:
        temp_dir = "dashboard/temp"
        os.makedirs(temp_dir, exist_ok=True)
        path = os.path.join(temp_dir, "network.html")
        nt.save_graph(path)
        with open(path, 'r', encoding='utf-8') as f:
            components.html(f.read(), height=620)
    except Exception as e:
        st.error(f"Error: {e}")

    # 인사이트 섹션 (빈 박스 레이아웃 제거)
    st.markdown('<div class="insight-container"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    degrees = dict(G.degree())
    most_versatile = sorted([n for n in degrees if n not in industry_colors], 
                           key=lambda x: degrees[x], reverse=True)[:5]

    with c1:
        st.markdown('<div class="insight-ttl">🏆 Top Versatile Ingredients</div>', unsafe_allow_html=True)
        for i, name in enumerate(most_versatile, 1):
            st.markdown(f'<div class="insight-item"><b>{i}. {name}</b> ({degrees[name]} industries)</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="insight-ttl">📊 Connectivity by Industry</div>', unsafe_allow_html=True)
        for industry in selected_industries:
            if industry in G:
                count = len(list(G.neighbors(industry)))
                st.markdown(f'<div class="insight-item"><b>{industry.capitalize()}</b>: {count} ingredients</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
