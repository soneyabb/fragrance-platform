import streamlit as st
import pandas as pd
import sqlite3
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os

# 페이지 설정
st.set_page_config(page_title="Industrial Connection Map", page_icon="🕸️", layout="wide")

def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        return pd.DataFrame()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT name, industry_usage, odor_family FROM ingredients", conn)
    conn.close()
    return df

def main():
    st.title("🕸️ Industrial Connection Map (산업 연결 맵)")
    st.markdown("---")

    df = load_data()
    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    st.markdown("""
    이 맵은 향료 원료(노드)와 해당 원료가 사용되는 산업 분야(노드) 간의 연결성을 보여줍니다.
    중심에 위치한 노드일수록 여러 산업에서 범용적으로 사용되는 원료입니다.
    """)

    # 네트워크 생성
    G = nx.Graph()

    # 산업 분야 색상 매핑
    industry_colors = {
        "perfume": "#FF9E9E",
        "cosmetic": "#9E9EFF",
        "food": "#9EFF9E",
        "tea_coffee": "#FFFF9E",
        "home_scent": "#FF9EFF",
        "fabric": "#9EFFFF",
        "pharmaceutical": "#FFD29E"
    }

    # 노드 및 엣지 추가
    selected_industries = st.multiselect(
        "필터링할 산업 분야를 선택하세요", 
        list(industry_colors.keys()), 
        default=list(industry_colors.keys())
    )

    for _, row in df.iterrows():
        ingredient = row['name']
        usages = [u.strip() for u in row['industry_usage'].split(',') if u.strip()]
        
        # 필터링된 산업만 포함
        valid_usages = [u for u in usages if u in selected_industries]
        
        if valid_usages:
            G.add_node(ingredient, color="#CCCCCC", size=15, title=f"Family: {row['odor_family']}")
            for usage in valid_usages:
                G.add_node(usage, color=industry_colors.get(usage, "#000000"), size=25, shape="diamond")
                G.add_edge(ingredient, usage)

    # PyVis 시각화
    nt = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    nt.from_nx(G)
    
    # 레이아웃 옵션 설정
    nt.set_options("""
    var options = {
      "nodes": {
        "font": { "size": 12 }
      },
      "edges": {
        "color": { "inherit": true },
        "smooth": false
      },
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "maxVelocity": 50,
        "solver": "forceAtlas2Based",
        "timestep": 0.35,
        "stabilization": { "iterations": 150 }
      }
    }
    """)

    # 파일 저장 및 출력
    try:
        # 임시 디렉토리 생성 (워크스페이스 내부)
        temp_dir = "dashboard/temp"
        os.makedirs(temp_dir, exist_ok=True)
        path = os.path.join(temp_dir, "network.html")
        nt.save_graph(path)
        
        with open(path, 'r', encoding='utf-8') as f:
            html_data = f.read()
            components.html(html_data, height=650)
    except Exception as e:
        st.error(f"시각화 로딩 중 오류가 발생했습니다: {e}")

    # 인사이트
    st.markdown("---")
    st.subheader("Key Insights")
    col1, col2 = st.columns(2)
    
    # 연결성 분석
    degrees = dict(G.degree())
    most_versatile = sorted([n for n in degrees if n not in industry_colors], 
                           key=lambda x: degrees[x], reverse=True)[:5]
    
    with col1:
        st.write("**Top 5 Versatile Ingredients (가장 범용적인 원료):**")
        for i, name in enumerate(most_versatile, 1):
            st.write(f"{i}. {name} (Used in {degrees[name]} industries)")

    with col2:
        st.write("**Industry Connectivity (산업별 원료 연결 수):**")
        for industry in selected_industries:
            if industry in G:
                count = len(list(G.neighbors(industry)))
                st.write(f"- {industry.capitalize()}: {count} ingredients")

if __name__ == "__main__":
    main()
