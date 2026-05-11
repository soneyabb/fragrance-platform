"""
load_to_db.py
-------------
fragrance_ingredients_v4.csv (마스터)
+ pubchem_raw.csv (PubChem 수집 결과)
를 병합하여 data/fragrance_db.sqlite 에 적재합니다.

원본 CSV는 절대 수정하지 않습니다.
병합 결과는 data/processed/ingredients.csv 에도 저장됩니다.

실행 방법:
    python processors/load_to_db.py
"""

import pandas as pd
import sqlite3
import os

# ── 경로 ──────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV  = os.path.join(BASE_DIR, "data", "raw", "fragrance_ingredients_v4.csv")
PUBCHEM_CSV = os.path.join(BASE_DIR, "data", "raw", "pubchem_raw.csv")
PROCESSED   = os.path.join(BASE_DIR, "data", "processed", "ingredients.csv")
DB_PATH     = os.path.join(BASE_DIR, "data", "fragrance_db.sqlite")


def main():
    # 1) 마스터 로드
    print("[1/5] 마스터 CSV 로드 중...")
    master = pd.read_csv(MASTER_CSV, skiprows=1)
    print(f"      → {len(master)}개 원료, {len(master.columns)}개 컬럼")

    # 2) PubChem 데이터 병합
    if os.path.exists(PUBCHEM_CSV):
        print("[2/5] PubChem 데이터 병합 중...")
        pubchem = pd.read_csv(PUBCHEM_CSV)

        # PubChem 컬럼만 추출 (name 키 + 수집 컬럼)
        pubchem_cols = [
            "name", "pubchem_cid", "cas_number",
            "molecular_formula", "molecular_weight",
            "iupac_name", "smiles", "pubchem_note"
        ]
        pubchem = pubchem[[c for c in pubchem_cols if c in pubchem.columns]]

        # 마스터의 기존 pubchem 컬럼 제거 후 병합
        drop_cols = [c for c in pubchem_cols[1:] if c in master.columns]
        master = master.drop(columns=drop_cols, errors="ignore")
        merged = master.merge(pubchem, on="name", how="left")
        print(f"      → 병합 완료: {len(merged)}개 원료")
    else:
        print("[2/5] pubchem_raw.csv 없음 — PubChem 컬럼은 N/A 유지")
        merged = master.copy()

    # 3) 결측값 정리
    print("[3/5] 결측값 정리 중...")
    merged = merged.fillna("N/A")
    # `:` 단독으로 입력된 placeholder 정리
    for col in merged.columns:
        merged[col] = merged[col].astype(str).str.strip()
        merged[col] = merged[col].replace(":", "N/A")

    # 4) processed CSV 저장
    print("[4/5] processed CSV 저장 중...")
    os.makedirs(os.path.dirname(PROCESSED), exist_ok=True)
    merged.to_csv(PROCESSED, index=False, encoding="utf-8-sig")
    print(f"      → {PROCESSED}")

    # 5) SQLite 적재
    print("[5/5] SQLite 적재 중...")
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    merged.to_sql(
        "ingredients",
        conn,
        if_exists="replace",   # 기존 테이블 교체
        index=False
    )

    # 검증
    count = pd.read_sql("SELECT COUNT(*) as cnt FROM ingredients", conn).iloc[0]["cnt"]
    cols  = pd.read_sql("PRAGMA table_info(ingredients)", conn)["name"].tolist()
    conn.close()

    print(f"      → DB: {DB_PATH}")
    print(f"      → 테이블: ingredients  |  행: {count}  |  컬럼: {len(cols)}")
    print(f"\n[DONE] 완료!")
    print(f"       컬럼 목록: {cols}")


if __name__ == "__main__":
    main()
