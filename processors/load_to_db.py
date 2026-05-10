import pandas as pd
from sqlalchemy import create_engine, types
import os

def main():
    # 파일 경로 설정
    raw_ingredients_path = "data/raw/fragrance_ingredients_v4.csv"
    raw_pubchem_path = "data/raw/pubchem_raw.csv"
    processed_csv_path = "data/processed/ingredients.csv"
    db_path = "data/fragrance_db.sqlite"
    
    # 1. 데이터 읽기
    if not os.path.exists(raw_ingredients_path):
        print(f"Error: {raw_ingredients_path} 파일이 없습니다.")
        return
    if not os.path.exists(raw_pubchem_path):
        print(f"Error: {raw_pubchem_path} 파일이 없습니다. PubChem 수집을 먼저 실행하세요.")
        return

    # 첫 줄이 파일명이므로 skiprows=1 적용
    df_ingredients = pd.read_csv(raw_ingredients_path, skiprows=1)
    df_pubchem = pd.read_csv(raw_pubchem_path)
    
    # 2. 데이터 병합 준비
    # 원본 파일에 이미 있는 PubChem 관련 컬럼(기존 N/A 데이터)을 삭제하여 중복 방지
    cols_to_drop = ["pubchem_cid", "cas_number", "molecular_formula", "molecular_weight"]
    df_ingredients = df_ingredients.drop(columns=[col for col in cols_to_drop if col in df_ingredients.columns])
    
    # name 기준으로 Left Join 병합
    df_merged = pd.merge(df_ingredients, df_pubchem, on="name", how="left")
    
    # 3. 데이터 저장 (Processed CSV)
    os.makedirs(os.path.dirname(processed_csv_path), exist_ok=True)
    df_merged.to_csv(processed_csv_path, index=False, encoding="utf-8-sig")
    
    # 4. SQLite DB 적재
    engine = create_engine(f"sqlite:///{db_path}")
    
    # 컬럼 타입 지정 (source_info, industry_usage를 TEXT로 보장)
    dtype_dict = {
        "source_info": types.TEXT,
        "industry_usage": types.TEXT,
        "odor_descriptors": types.TEXT,
        "subjective_description": types.TEXT,
        "sensory_notes": types.TEXT
    }
    
    # 데이터베이스에 저장 (이미 존재하면 replace)
    df_merged.to_sql(
        name="ingredients",
        con=engine,
        if_exists="replace",
        index=False,
        dtype=dtype_dict
    )
    
    print(f"DB 적재 완료: {len(df_merged)}개 원료")

if __name__ == "__main__":
    main()
