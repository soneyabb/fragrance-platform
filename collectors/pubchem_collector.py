"""
pubchem_collector.py (v3)
--------------------------
변경사항 (v2 → v3):
  - 소스 확장: fragrance_ingredients_v4.csv(66개) + ifra_data.csv(263개) 통합
  - CAS 번호 우선 검색 추가 (IFRA 소스는 CAS가 있으므로 훨씬 정확)
  - 중복 원료 자동 제거 (name 기준)
  - 검색 순서: CAS → 학명 → 주성분 → 영문명

실행:
    python collectors/pubchem_collector.py
"""

import requests
import pandas as pd
import time
import os
import re

# ── 경로 ──────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER_CSV  = os.path.join(BASE_DIR, "data", "raw", "fragrance_ingredients_v4.csv")
IFRA_CSV    = os.path.join(BASE_DIR, "data", "raw", "ifra_data.csv")
OUTPUT_CSV  = os.path.join(BASE_DIR, "data", "raw", "pubchem_raw.csv")
BASE_URL    = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

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


# ── 입력 데이터 준비 ──────────────────────────────────────

def load_combined_sources() -> pd.DataFrame:
    """
    마스터(66개) + IFRA(263개) 합치기.
    결과 컬럼: name, scientific_name, main_components,
               extraction_method, cas_number(IFRA 기준)
    중복은 name 기준으로 마스터 우선.
    """
    rows = []

    # 1) 마스터 CSV
    if os.path.exists(MASTER_CSV):
        df_master = pd.read_csv(MASTER_CSV, skiprows=1)
        for _, row in df_master.iterrows():
            rows.append({
                "name":             str(row.get("name", "")).strip(),
                "scientific_name":  str(row.get("scientific_name", "")).strip(),
                "main_components":  str(row.get("main_components", "")).strip(),
                "extraction_method":str(row.get("extraction_method", "")).strip(),
                "cas_number":       str(row.get("cas_number", "")).strip(),
                "source":           "master",
            })
        print(f"[INFO] 마스터 로드: {len(df_master)}개")
    else:
        print(f"[WARN] 마스터 파일 없음: {MASTER_CSV}")

    # 2) IFRA CSV
    if os.path.exists(IFRA_CSV):
        df_ifra = pd.read_csv(IFRA_CSV)
        for _, row in df_ifra.iterrows():
            rows.append({
                "name":             str(row.get("name", "")).strip(),
                "scientific_name":  "",
                "main_components":  "",
                "extraction_method":"",
                "cas_number":       str(row.get("cas_number", "")).strip(),
                "source":           "ifra",
            })
        print(f"[INFO] IFRA 로드: {len(df_ifra)}개")
    else:
        print(f"[WARN] IFRA 파일 없음: {IFRA_CSV}")

    df = pd.DataFrame(rows)

    # 중복 제거: name 기준, master 우선
    df = df.sort_values("source", ascending=True)  # master < ifra 알파벳순
    df = df.drop_duplicates(subset=["name"], keep="first")
    df = df.reset_index(drop=True)

    print(f"[INFO] 중복 제거 후 총 {len(df)}개 원료 처리 예정\n")
    return df


# ── API 함수 ──────────────────────────────────────────────

def search_cid_by_cas(cas_raw: str) -> str | None:
    """
    CAS 번호로 CID 검색.
    CAS가 여러 개(\n 구분)면 첫 번째만 시도.
    """
    if not cas_raw or cas_raw.strip() in ("N/A", "nan", "", "None"):
        return None
    # 여러 CAS 중 첫 번째만 사용
    first_cas = cas_raw.replace("\\n", "\n").split("\n")[0].strip()
    if not first_cas:
        return None
    url = f"{BASE_URL}/compound/name/{requests.utils.quote(first_cas)}/cids/JSON"
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            cids = r.json().get("IdentifierList", {}).get("CID", [])
            return str(cids[0]) if cids else None
    except Exception:
        pass
    return None


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
    """후보 쿼리 목록을 순서대로 시도. 성공한 첫 번째 CID 반환."""
    for query in candidates:
        if not query or query.strip() in ("N/A", ":", "", "nan"):
            continue
        cid = search_cid(query)
        if cid:
            return cid, query
        time.sleep(0.3)
    return None, ""


def get_properties(cid: str) -> dict:
    props = "MolecularFormula,MolecularWeight,IUPACName,IsomericSMILES,XLogP"
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
                "logp":              str(p.get("XLogP", "N/A")),
            }
    except Exception:
        pass
    return {}


def get_experimental_data(cid: str) -> dict:
    """PUG View API → Boiling Point, Vapor Pressure 추출"""
    url = (
        f"https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/"
        f"{cid}/JSON?heading=Experimental+Properties"
    )
    res = {"boiling_point": "N/A", "vapor_pressure": "N/A"}
    try:
        r = requests.get(url, timeout=12)
        if r.status_code == 200:
            sections = r.json().get("Record", {}).get("Section", [])
            for sec in sections:
                if sec.get("TOCHeading") == "Experimental Properties":
                    for sub in sec.get("Section", []):
                        heading = sub.get("TOCHeading")
                        try:
                            val = sub["Information"][0]["Value"]["StringWithMarkup"][0]["String"]
                            if heading == "Boiling Point":
                                res["boiling_point"] = val
                            elif heading == "Vapor Pressure":
                                res["vapor_pressure"] = val
                        except (KeyError, IndexError):
                            continue
    except Exception:
        pass
    return res


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
    if not raw or str(raw).strip() in ("N/A", ":", "nan", ""):
        return ""
    cleaned = re.split(r"EO의|의 ", str(raw))[0]
    return re.split(r"[,·/]", cleaned)[0].strip()


def clean_scientific(sci: str) -> str:
    if not sci or str(sci).strip() in ("N/A", ":", "nan", ""):
        return ""
    parts = str(sci).strip().split()
    return " ".join(parts[:2]) if len(parts) >= 2 else str(sci).strip()


# ── 메인 ──────────────────────────────────────────────────

def main():
    df = load_combined_sources()
    results = []
    total = len(df)
    success_count = 0
    skip_count = 0

    for idx, row in df.iterrows():
        name       = str(row["name"]).strip()
        sci_raw    = str(row.get("scientific_name", "")).strip()
        comp_raw   = str(row.get("main_components", "")).strip()
        method_raw = str(row.get("extraction_method", "")).strip()
        cas_raw    = str(row.get("cas_number", "")).strip()
        source     = str(row.get("source", "")).strip()

        print(f"[{idx+1:03d}/{total}] {name:<40}", end="  ")

        base = {
            "name":             name,
            "source":           source,
            "pubchem_cid":      "N/A",
            "cas_number":       "N/A",
            "molecular_formula":"N/A",
            "molecular_weight": "N/A",
            "iupac_name":       "N/A",
            "smiles":           "N/A",
            "logp":             "N/A",
            "boiling_point":    "N/A",
            "vapor_pressure":   "N/A",
            "pubchem_note":     "",
        }

        # 1) 조합/합성향료 스킵
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

        # 2) 동물성: override 검색명 사용
        if name in ANIMAL_OVERRIDE:
            override = ANIMAL_OVERRIDE[name]
            cid, used = search_cid_multi([override])
            note = f"동물성 — 주성분({override}) 기준"
        else:
            # 3) CAS 우선 → 학명 → 주성분 → 영문명 순서
            cid = search_cid_by_cas(cas_raw)
            if cid:
                used = f"CAS({cas_raw.split(chr(10))[0].strip()})"
                note = f"CAS 검색 성공: {used}"
            else:
                sci_clean  = clean_scientific(sci_raw)
                first_comp = first_component(comp_raw)
                candidates = [sci_clean, first_comp, name]
                cid, used  = search_cid_multi(candidates)
                note       = f"검색어: '{used}'" if used else "CID 없음"

        if not cid:
            base["pubchem_note"] = "CID not found (CAS/학명/성분/원료명 모두 실패)"
            results.append(base)
            print("→ CID 없음")
            skip_count += 1
            continue

        # 4) 속성 수집
        base["pubchem_cid"] = cid
        props = get_properties(cid)
        base.update(props)
        time.sleep(0.2)

        exp_data = get_experimental_data(cid)
        base.update(exp_data)
        time.sleep(0.2)

        cas = get_cas(cid)
        base["cas_number"] = cas
        base["pubchem_note"] = note
        time.sleep(0.2)

        results.append(base)
        print(f"→ CID {cid}  CAS {cas}")
        success_count += 1

    # 저장
    out = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    print(f"""
{'='*60}
[DONE] 저장 완료: {OUTPUT_CSV}
       총 {total}개  |  성공 {success_count}개  |  스킵/실패 {skip_count}개
{'='*60}
""")


if __name__ == "__main__":
    main()
