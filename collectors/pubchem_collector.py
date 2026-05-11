"""
pubchem_collector.py (v2)
--------------------------
개선사항:
  - 검색 3단계: 학명 → 주성분 → 영문명 순서로 시도
  - 조합향료/합성향료 자동 감지 후 스킵
  - 동물성 원료는 주성분명으로 검색
  - 원본 CSV 절대 수정 안 함 → data/raw/pubchem_raw.csv 에만 저장

실행:
    python collectors/pubchem_collector.py
"""

import requests
import pandas as pd
import time
import os
import re

# ── 경로 ──────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV  = os.path.join(BASE_DIR, "data", "raw", "fragrance_ingredients_v4.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "raw", "pubchem_raw.csv")
BASE_URL   = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# ── 조합/합성향료: 스킵 대상 ──────────────────────────────
SYNTHETIC_EXTRACTION = {
    "조합 향료", "조합향료", "합성향료", "합성향료(합성)",
    "합성", "합성향료 ", "조합향료 "
}
SYNTHETIC_NAMES = {
    "Green Note", "Sea Scent", "Aldehydal", "White Musk"
}

# ── 동물성: 주성분으로 검색 ───────────────────────────────
ANIMAL_OVERRIDE = {
    "Musk":         "Muscone",
    "Civet Cat Oil":"Civetone",
    "Beaver Oil":   "Castoramine",
    "Amber":        "Ambroxan",
}

# ── API 함수 ──────────────────────────────────────────────

def search_cid(query: str) -> str | None:
    """단일 쿼리로 CID 검색. 실패 시 None."""
    url = f"{BASE_URL}/compound/name/{requests.utils.quote(query.strip())}/cids/JSON"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            cids = r.json().get("IdentifierList", {}).get("CID", [])
            return str(cids[0]) if cids else None
    except Exception:
        pass
    return None


def search_cid_multi(candidates: list[str]) -> tuple[str | None, str]:
    """
    후보 쿼리 목록을 순서대로 시도.
    성공한 첫 번째 CID와 사용된 쿼리를 반환.
    """
    for query in candidates:
        if not query or query.strip() in ("N/A", ":", "", "nan"):
            continue
        cid = search_cid(query)
        if cid:
            return cid, query
        time.sleep(0.3)
    return None, ""


def get_properties(cid: str) -> dict:
    props = "MolecularFormula,MolecularWeight,IUPACName,IsomericSMILES"
    url = f"{BASE_URL}/compound/cid/{cid}/property/{props}/JSON"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            p = r.json().get("PropertyTable", {}).get("Properties", [{}])[0]
            return {
                "molecular_formula": p.get("MolecularFormula", "N/A"),
                "molecular_weight":  str(p.get("MolecularWeight", "N/A")),
                "iupac_name":        p.get("IUPACName", "N/A"),
                "smiles":            p.get("IsomericSMILES", "N/A"),
            }
    except Exception:
        pass
    return {}


def get_cas(cid: str) -> str:
    url = f"{BASE_URL}/compound/cid/{cid}/synonyms/JSON"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            syns = (
                r.json()
                .get("InformationList", {})
                .get("Information", [{}])[0]
                .get("Synonym", [])
            )
            for s in syns:
                parts = s.split("-")
                if len(parts) == 3 and all(p.isdigit() for p in parts):
                    return s
    except Exception:
        pass
    return "N/A"


def first_component(raw: str) -> str:
    """'Linalyl acetate, Linalool, ...' 에서 첫 번째 성분명만 추출."""
    if not raw or str(raw).strip() in ("N/A", ":", "nan", ""):
        return ""
    # 'EO의 xx%' 같은 설명 제거
    cleaned = re.split(r"EO의|의 ", str(raw))[0]
    first = re.split(r"[,·/]", cleaned)[0].strip()
    return first


def clean_scientific(sci: str) -> str:
    """학명에서 명명자(저자) 제거 → 속명+종명만 반환."""
    if not sci or str(sci).strip() in ("N/A", ":", "nan", ""):
        return ""
    # 예) "Citrus bergamia Risso" → "Citrus bergamia"
    parts = str(sci).strip().split()
    if len(parts) >= 2:
        return " ".join(parts[:2])
    return str(sci).strip()


# ── 메인 ──────────────────────────────────────────────────

def main():
    print(f"[INFO] 원본 파일 로드: {INPUT_CSV}\n")
    df = pd.read_csv(INPUT_CSV, skiprows=1)
    results = []
    total = len(df)
    success_count = 0
    skip_count = 0

    for _, row in df.iterrows():
        name       = str(row["name"]).strip()
        sci_raw    = str(row.get("scientific_name", "")).strip()
        comp_raw   = str(row.get("main_components", "")).strip()
        method_raw = str(row.get("extraction_method", "")).strip()
        idx        = _ + 1

        print(f"[{idx:02d}/{total}] {name:<25}", end="  ")

        base = {
            "name":             name,
            "pubchem_cid":      "N/A",
            "cas_number":       "N/A",
            "molecular_formula":"N/A",
            "molecular_weight": "N/A",
            "iupac_name":       "N/A",
            "smiles":           "N/A",
            "pubchem_note":     "",
        }

        # ── 1) 조합/합성향료 스킵 ─────────────────────────
        is_synthetic = (
            name in SYNTHETIC_NAMES
            or method_raw in SYNTHETIC_EXTRACTION
        )
        if is_synthetic:
            base["pubchem_note"] = "synthetic_blend — PubChem 수집 불가"
            results.append(base)
            print("→ synthetic_blend 스킵")
            skip_count += 1
            continue

        # ── 2) 동물성: override 검색명 사용 ──────────────
        if name in ANIMAL_OVERRIDE:
            override = ANIMAL_OVERRIDE[name]
            cid, used = search_cid_multi([override])
            note = f"동물성 — 주성분({override}) 기준"
        else:
            # ── 3) 일반: 학명 → 주성분 → 영문명 순서 ────
            sci_clean  = clean_scientific(sci_raw)
            first_comp = first_component(comp_raw)
            candidates = [sci_clean, first_comp, name]
            cid, used  = search_cid_multi(candidates)
            note       = f"검색어: '{used}'" if used else "CID 없음"

        if not cid:
            base["pubchem_note"] = f"CID not found (시도: 학명/성분/원료명)"
            results.append(base)
            print("→ CID 없음")
            skip_count += 1
            continue

        # ── 4) 속성 수집 ──────────────────────────────────
        base["pubchem_cid"] = cid
        props = get_properties(cid)
        base.update(props)
        time.sleep(0.3)

        cas = get_cas(cid)
        base["cas_number"] = cas
        base["pubchem_note"] = note
        time.sleep(0.3)

        results.append(base)
        print(f"→ CID: {cid}  CAS: {cas}  ({note})")
        success_count += 1

    # ── 저장 ──────────────────────────────────────────────
    out = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"""
{'='*55}
[DONE] 저장 완료: {OUTPUT_CSV}
       총 {total}개  |  성공 {success_count}개  |  N/A {skip_count}개
{'='*55}
""")


if __name__ == "__main__":
    main()
