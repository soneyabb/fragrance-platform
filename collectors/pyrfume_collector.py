"""
pyrfume_collector.py
--------------------
목적: Pyrfume 데이터셋에서 odor descriptor를 우리 329개 원료에 매핑
소스: goodscents/behavior.csv, leffingwell/behavior.csv
출처: Pyrfume Project (pyrfume.org) — 포트폴리오 용도 사용, 출처 명시
결과: data/raw/pyrfume_data.csv
  컬럼: cas_number, goodscents_descriptors, leffingwell_labels, data_source
"""

import pyrfume
import pandas as pd
import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBCHEM_CSV = os.path.join(BASE_DIR, "data", "raw", "pubchem_raw.csv")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "raw", "pyrfume_data.csv")


def load_our_cas() -> set:
    """우리 329개 원료의 CAS 번호 집합 반환"""
    df = pd.read_csv(PUBCHEM_CSV)
    cas_set = set()
    for val in df["cas_number"].dropna():
        # 여러 CAS(\n 구분) 중 첫 번째만 사용
        first = str(val).split("\n")[0].strip()
        if first and first != "N/A":
            cas_set.add(first)
    print(f"[INFO] 우리 원료 CAS 번호: {len(cas_set)}개")
    return cas_set


def load_goodscents(our_cas: set) -> pd.DataFrame:
    """goodscents behavior.csv → CAS 매핑"""
    df = pyrfume.load_data("goodscents/behavior.csv")
    df.index = df.index.astype(str).str.strip()
    matched = df[df.index.isin(our_cas)]
    result = matched.reset_index()
    result.columns = ["cas_number", "goodscents_descriptors"]
    print(f"[INFO] goodscents 매핑: {len(result)}개")
    return result


def load_leffingwell(our_cas: set) -> pd.DataFrame:
    """leffingwell behavior.csv → CAS 매핑 후 라벨 텍스트로 변환"""
    stim = pyrfume.load_data("leffingwell/stimuli.csv")
    beh  = pyrfume.load_data("leffingwell/behavior.csv")

    # stimuli에서 CAS 컬럼 확인 후 매핑
    stim.index = stim.index.astype(str)
    beh.index  = beh.index.astype(str)

    # CAS 컬럼 찾기
    cas_col = None
    for col in stim.columns:
        if "CAS" in col or "cas" in col:
            cas_col = col
            break

    if cas_col is None:
        print("[WARN] leffingwell stimuli에 CAS 컬럼 없음 — 스킵")
        return pd.DataFrame(columns=["cas_number", "leffingwell_labels"])

    stim_filtered = stim[stim[cas_col].astype(str).isin(our_cas)]
    merged = stim_filtered[[cas_col]].join(beh, how="inner")

    # 1인 라벨만 텍스트로 합치기
    label_cols = [c for c in beh.columns]
    def row_to_labels(row):
        return ";".join([c for c in label_cols if row.get(c, 0) == 1])

    merged["leffingwell_labels"] = merged.apply(row_to_labels, axis=1)
    result = merged[[cas_col, "leffingwell_labels"]].rename(columns={cas_col: "cas_number"})
    print(f"[INFO] leffingwell 매핑: {len(result)}개")
    return result


def main():
    our_cas = load_our_cas()

    gs  = load_goodscents(our_cas)
    lef = load_leffingwell(our_cas)

    # 두 소스 합치기
    result = gs.merge(lef, on="cas_number", how="outer")
    result["data_source"] = "pyrfume (goodscents + leffingwell)"

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"\n✅ 완료: {len(result)}개 원료 매핑 → {OUTPUT_CSV}")
    print(result.head(3))


if __name__ == "__main__":
    main()
