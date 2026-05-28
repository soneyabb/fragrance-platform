"""
load_to_db.py
-------------
목적: 모든 수집된 원시 데이터(CSV)를 통합하여 최종 SQLite DB에 적재.
소스:
  1. fragrance_ingredients_v4.csv (마스터)
  2. pubchem_raw.csv (화학 물성 - BP, logP, VP 포함)
  3. academic_signals.csv (Semantic Scholar)
  4. reddit_signals.csv (Reddit PRAW)
  5. ifra_manual.csv (IFRA 규제 - 수동)
  6. parfumo_data.csv (Parfumo 시장 데이터)

실행: python processors/load_to_db.py
"""

import pandas as pd
import sqlite3
import os

# ── 경로 설정 ─────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV  = os.path.join(BASE_DIR, "data", "raw", "fragrance_ingredients_v4.csv")
PUBCHEM_CSV = os.path.join(BASE_DIR, "data", "raw", "pubchem_raw.csv")
SCHOLAR_CSV = os.path.join(BASE_DIR, "data", "raw", "academic_signals.csv")
REDDIT_CSV  = os.path.join(BASE_DIR, "data", "raw", "reddit_signals.csv")
IFRA_CSV    = os.path.join(BASE_DIR, "data", "raw", "ifra_data.csv")
PARFUMO_CSV = os.path.join(BASE_DIR, "data", "raw", "parfumo_data.csv")

PROCESSED   = os.path.join(BASE_DIR, "data", "processed", "ingredients.csv")
DB_PATH     = os.path.join(BASE_DIR, "data", "fragrance_db.sqlite")


def main():
    # 1) 마스터 로드
    print("[1/6] 마스터 CSV 로드 중...")
    if not os.path.exists(MASTER_CSV):
        print(f"[ERR] 마스터 파일 없음: {MASTER_CSV}")
        return
    master = pd.read_csv(MASTER_CSV, skiprows=1)
    print(f"      → {len(master)}개 원료 로드됨")

    merged = master.copy()

    # 2) PubChem 데이터 병합 (물리적 특성 포함)
    if os.path.exists(PUBCHEM_CSV):
        print("[2/6] PubChem 데이터 병합 중...")
        pc = pd.read_csv(PUBCHEM_CSV)
        pc_cols = ["name", "pubchem_cid", "cas_number", "molecular_formula", "molecular_weight", 
                   "iupac_name", "smiles", "logp", "boiling_point", "vapor_pressure"]
        # 기존 마스터에 해당 컬럼이 있으면 제거 후 새로 병합
        merged = merged.drop(columns=[c for c in pc_cols[1:] if c in merged.columns], errors="ignore")
        merged = merged.merge(pc[[c for c in pc_cols if c in pc.columns]], on="name", how="outer")

    # 3) Scholar 학술 데이터 병합
    if os.path.exists(SCHOLAR_CSV):
        print("[3/6] Scholar 학술 데이터 병합 중...")
        sc = pd.read_csv(SCHOLAR_CSV)
        sc_cols = ["name", "academic_count", "top_citation_count", "latest_paper_year"]
        merged = merged.merge(sc[[c for c in sc_cols if c in sc.columns]], on="name", how="left")

    # 4) Reddit 커뮤니티 데이터 병합
    if os.path.exists(REDDIT_CSV):
        print("[4/6] Reddit 커뮤니티 데이터 병합 중...")
        rd = pd.read_csv(REDDIT_CSV)
        rd_cols = ["name", "reddit_mentions", "reddit_score"]
        merged = merged.merge(rd[[c for c in rd_cols if c in rd.columns]], on="name", how="left")

    # 5) IFRA 규제 데이터 병합
    if os.path.exists(IFRA_CSV):
        print("[5/6] IFRA 규제 데이터 병합 중...")
        ifra = pd.read_csv(IFRA_CSV)
        ifra_cols = ["name", "ifra_status", "amendment_version",
                     "category_1_pct","category_2_pct","category_3_pct",
                     "category_4_pct","category_5a_pct","category_5b_pct",
                     "category_5c_pct","category_5d_pct","category_6_pct",
                     "category_7a_pct","category_7b_pct","category_8_pct",
                     "category_9_pct","category_10a_pct","category_10b_pct",
                     "category_11a_pct","category_11b_pct","category_12_pct"]
        merged = merged.merge(ifra[[c for c in ifra_cols if c in ifra.columns]], on="name", how="outer")

    # --- 결측치 세부 처리 ---
    # 1. 수치형 컬럼 정의 (0 또는 None으로 채워 타입 유지)
    numeric_cols = [
        "molecular_weight", "logp", "academic_count",
        "top_citation_count", "reddit_mentions", "reddit_score",
        "category_1_pct","category_2_pct","category_3_pct",
        "category_4_pct","category_5a_pct","category_5b_pct",
        "category_5c_pct","category_5d_pct","category_6_pct",
        "category_7a_pct","category_7b_pct","category_8_pct",
        "category_9_pct","category_10a_pct","category_10b_pct",
        "category_11a_pct","category_11b_pct","category_12_pct"
    ]
    for col in numeric_cols:
        if col in merged.columns:
            # 숫자로 변환 시도, 실패 시 NaN
            merged[col] = pd.to_numeric(merged[col], errors="coerce")
            # 수치형의 기본값은 0 또는 None (여기서는 0으로 처리하여 시각화 용이하게 함)
            merged[col] = merged[col].fillna(0)

    # 2. 텍스트형 컬럼 정의
    # 나머지는 문자열로 변환하고 N/A 처리
    text_cols = merged.select_dtypes(include=["object"]).columns
    for col in text_cols:
        merged[col] = merged[col].fillna("N/A").astype(str).str.replace(":", "N/A").str.strip()

    # 6) SQLite 적재
    print("[6/6] SQLite 적재 시작...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    
    # [Table 1] ingredients (통합 마스터)
    merged.to_sql("ingredients", conn, if_exists="replace", index=False)
    
    # [Table 2] perfumes (시장 데이터 - Parfumo)
    if os.path.exists(PARFUMO_CSV):
        print("      → Parfumo 대용량 데이터 적재 중 (perfumes 테이블)...")
        parfumo = pd.read_csv(PARFUMO_CSV)
        parfumo.to_sql("perfumes", conn, if_exists="replace", index=False)

    conn.close()

    # Processed CSV 저장 (백업용)
    os.makedirs(os.path.dirname(PROCESSED), exist_ok=True)
    merged.to_csv(PROCESSED, index=False, encoding="utf-8-sig")

    print(f"\n[DONE] 파이프라인 통합 완료!")
    print(f"       최종 DB: {DB_PATH}")
    print(f"       통합 원료: {len(merged)}행")

if __name__ == "__main__":
    main()
