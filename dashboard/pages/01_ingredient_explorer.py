import streamlit as st
import pandas as pd
import sqlite3
import os

# 페이지 설정
st.set_page_config(page_title="Ingredient Explorer", page_icon="🔍", layout="wide")

# Odor Family별 이모지 매핑
FAMILY_EMOJI = {
    "Citrus": "🍊",
    "Fruity": "🥭",
    "Green": "🌱",
    "Herbal": "🌿",
    "Floral": "💐",
    "Aldehyde": "🧼",
    "Animal": "🐾",
    "Woody": "🪵",
    "Mossy": "🪨",
    "Spicy": "🫚",
    "Balsamic": "🍯",
}

def load_data():
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        st.error("데이터베이스 파일이 없습니다. 먼저 데이터 적재를 수행하세요.")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ingredients", conn)
    conn.close()
    return df

def main():
    st.title("🔍 Ingredient Explorer (원료 탐색기)")
    st.markdown("---")
    
    df = load_data()
    if df.empty:
        return

    # 사이드바 필터
    st.sidebar.header("Filters")
    
    # 1. 검색어
    search_query = st.sidebar.text_input("원료명 검색", "")
    
    # 2. Volatility Class 필터
    volatility_options = ["All"] + sorted(df['volatility_class'].dropna().unique().tolist())
    selected_volatility = st.sidebar.selectbox("Volatility Class", volatility_options)
    
    # 3. Odor Family 필터
    family_list = sorted(df['odor_family'].dropna().unique().tolist())
    family_options = ["All"] + [f"{FAMILY_EMOJI.get(f, '⚗️')} {f}" for f in family_list]
    selected_family_display = st.sidebar.selectbox("Odor Family", family_options)
    selected_family = selected_family_display.split(" ", 1)[1] if selected_family_display != "All" else "All"

    # 데이터 필터링
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False)]
    if selected_volatility != "All":
        filtered_df = filtered_df[filtered_df['volatility_class'] == selected_volatility]
    if selected_family != "All":
        filtered_df = filtered_df[filtered_df['odor_family'] == selected_family]

    # 메인 레이아웃
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader(f"Results ({len(filtered_df)})")
        selected_name = st.selectbox("원료를 선택하여 상세 정보를 확인하세요", filtered_df['name'].tolist())
    
    if selected_name:
        ingredient = df[df['name'] == selected_name].iloc[0]
        family = ingredient['odor_family']
        emoji = FAMILY_EMOJI.get(family, "⚗️")
        
        with col2:
            st.header(f"{ingredient['name']} {ingredient['preference_moon']}")
            st.write(f"**Scientific Name:** {ingredient['scientific_name']}")
            st.write(f"**Odor Family:** {emoji} {family}")
            
            tabs = st.tabs(["Overview", "Sensory & Notes", "Chemistry", "Industry"])
            
            with tabs[0]:
                st.markdown(f"### Objective Description\n{ingredient['objective_description']}")
                st.markdown(f"### Subjective Summary\n{ingredient['subjective_description']}")
                st.info(f"**Role:** {ingredient['role']} | **Origin:** {ingredient['origin_country']}")
                
            with tabs[1]:
                st.markdown("### Sensory Notes")
                notes = ingredient['sensory_notes'].split('|') if ingredient['sensory_notes'] else []
                for note in notes:
                    st.write(f"- {note.strip()}")
                
                if ingredient['comparison_notes'] and str(ingredient['comparison_notes']) != 'nan':
                    st.markdown("### Comparison Notes")
                    st.write(ingredient['comparison_notes'])
            
            with tabs[2]:
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("PubChem CID", ingredient['pubchem_cid'])
                    st.metric("CAS Number", ingredient['cas_number'])
                with c2:
                    st.metric("Molecular Formula", ingredient['molecular_formula'])
                    st.metric("Molecular Weight", ingredient['molecular_weight'])
                
                st.markdown(f"**Main Components:** {ingredient['main_components']}")
                st.markdown(f"**Extraction Method:** {ingredient['extraction_method']}")

            with tabs[3]:
                st.markdown("### Industry Usage")
                usages = ingredient['industry_usage'].split(',') if ingredient['industry_usage'] else []
                st.write(", ".join([f"`{u.strip()}`" for u in usages]))
                
                st.markdown("### Source Information")
                st.code(ingredient['source_info'], language='json')

    # 하단 데이터 테이블
    st.markdown("---")
    st.subheader("Raw Data View")
    st.dataframe(filtered_df)

if __name__ == "__main__":
    main()
