"""
ifra_collector.py
-----------------
IFRA 51st Amendment (2023) 원료 규제 데이터 파싱
출처: https://ifrafragrance.org/safe-use/library (공개 Excel)
방식: 로컬 ifra_51st.xlsx 파싱 (수동 다운로드 완료)
결과: data/raw/ifra_data.csv

컬럼:
  name, cas_number, synonyms, ifra_status, amendment_version,
  category_1_pct ~ category_12_pct (18개)

주의:
  - IFRA 공식 공개 데이터 (크롤링 아님)
  - data/raw/ifra_51st.xlsx 원본 수정 금지
  - header=2 로 읽어야 실제 컬럼명이 나옴
"""

import pandas as pd
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_XLSX = os.path.join(BASE_DIR, "data", "raw", "ifra_51st.xlsx")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "raw", "ifra_data.csv")

# IFRA Category 컬럼 → 표준 컬럼명 매핑
CATEGORY_MAP = {
    "Category 1 (%)":   "category_1_pct",
    "Category 2 (%)":   "category_2_pct",
    "Category 3 (%)":   "category_3_pct",
    "Category 4 (%)":   "category_4_pct",
    "Category 5A (%)":  "category_5a_pct",
    "Category 5B (%)":  "category_5b_pct",
    "Category 5C (%)":  "category_5c_pct",
    "Category 5D (%)":  "category_5d_pct",
    "Category 6 (%)":   "category_6_pct",
    "Category 7A (%)":  "category_7a_pct",
    "Category 7B (%)":  "category_7b_pct",
    "Category 8 (%)":   "category_8_pct",
    "Category 9 (%)":   "category_9_pct",
    "Category 10A (%)": "category_10a_pct",
    "Category 10B (%)": "category_10b_pct",
    "Category 11A (%)": "category_11a_pct",
    "Category 11B (%)": "category_11b_pct",
    "Category 12 (%)":  "category_12_pct",
}

def determine_status(row: pd.Series) -> str:
    """
    IFRA Standard type 컬럼 기반으로 규제 상태 결정
    값이 없으면 Category 값으로 추론
    """
    std_type = str(row.get("IFRA Standard type", "")).strip().lower()

    if "prohibit" in std_type:
        return "Prohibited"
    if "restrict" in std_type:
        return "Restricted"
    if "specify" in std_type or "specified" in std_type:
        return "Specified"

    # IFRA Standard type이 없으면 Category 값으로 추론
    cat_cols = list(CATEGORY_MAP.keys())
    values = [str(row.get(c, "")).strip().lower() for c in cat_cols]
    if all(v in ("", "nan", "no restriction") for v in values):
        return "No Restriction"
    if any(v == "0" or v == "0.0" for v in values):
        return "Prohibited"
    return "Restricted"

def parse_ifra_excel() -> pd.DataFrame:
    if not os.path.exists(INPUT_XLSX):
        print(f"[ERROR] 파일 없음: {INPUT_XLSX}")
        print("  → data/raw/ifra_51st.xlsx 를 수동으로 배치해주세요.")
        return pd.DataFrame()

    print(f"읽는 중: {INPUT_XLSX}")
    df = pd.read_excel(INPUT_XLSX, sheet_name=0, header=2)
    print(f"  원본 행 수: {len(df)}, 컬럼 수: {len(df.columns)}")
    return df

def normalize_ifra(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    result = pd.DataFrame()

    # 핵심 컬럼
    result["name"]              = df["Name of the IFRA Standard"].astype(str).str.strip()
    result["cas_number"]        = df["CAS numbers"].astype(str).str.strip().replace("nan", None)
    result["synonyms"]          = df["Synonyms"].astype(str).str.strip().replace("nan", None)
    result["amendment_version"] = "51st (2023)"

    # 규제 상태
    result["ifra_status"] = df.apply(determine_status, axis=1)

    # Category 농도 18개
    for orig_col, new_col in CATEGORY_MAP.items():
        if orig_col in df.columns:
            result[new_col] = (
                df[orig_col]
                .astype(str)
                .str.strip()
                .replace({"nan": None, "NaN": None, "": None})
            )
        else:
            result[new_col] = None

    # 빈 행 제거
    result = result[result["name"].notna() & (result["name"] != "") & (result["name"] != "nan")]
    result = result.drop_duplicates(subset=["name"])
    result = result.reset_index(drop=True)

    return result

def main():
    df_raw = parse_ifra_excel()
    if df_raw.empty:
        return

    df_out = normalize_ifra(df_raw)
    if df_out.empty:
        print("[ERROR] 정규화 결과가 비어 있습니다.")
        return

    df_out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n✅ 완료: {len(df_out)}개 원료 → {OUTPUT_CSV}")
    print("\n상태별 분포:")
    print(df_out["ifra_status"].value_counts().to_string())
    print("\n샘플 (처음 3행):")
    print(df_out[["name", "cas_number", "ifra_status", "category_1_pct", "category_12_pct"]].head(3).to_string())

if __name__ == "__main__":
    main()
