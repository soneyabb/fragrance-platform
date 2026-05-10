import requests
import pandas as pd
import time
import os
import re

# PubChem PUG REST API 베이스 URL
BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

def get_cas_from_synonyms(cid):
    """
    CID를 사용하여 PubChem에서 Synonyms를 가져오고 CAS 번호를 추출합니다.
    """
    url = f"{BASE_URL}/compound/cid/{cid}/synonyms/JSON"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            synonyms = data.get('InformationList', {}).get('Information', [{}])[0].get('Synonym', [])
            
            # CAS 번호 패턴 (예: 123-45-6)
            cas_pattern = re.compile(r'^\d{2,7}-\d{2}-\d$')
            for synonym in synonyms:
                if cas_pattern.match(synonym):
                    return synonym
        return "N/A"
    except Exception:
        return "N/A"

def get_pubchem_data(name, scientific_name=None):
    """
    원료명으로 CID를 조회하고, 해당 CID로 화학 정보를 수집합니다.
    검색 실패 시 학명이나 핵심 단어로 재시도합니다.
    """
    # 초기값 설정
    info = {
        "pubchem_cid": "N/A",
        "cas_number": "N/A",
        "molecular_formula": "N/A",
        "molecular_weight": "N/A"
    }

    # 검색 후보 리스트 생성
    search_candidates = [name]
    
    # 1. 학명이 있으면 추가
    if scientific_name and str(scientific_name) != 'nan' and scientific_name != ':':
        # 학명에서 저자명(L., Risso 등) 제외 시도
        clean_sci = scientific_name.split(' ')[0:2]
        if len(clean_sci) >= 2:
            search_candidates.append(' '.join(clean_sci))
        search_candidates.append(scientific_name)
    
    # 2. 이름의 마지막 단어 (예: Alpine Lavender -> Lavender)
    if ' ' in name:
        search_candidates.append(name.split(' ')[-1])
        
    # 3. 이름의 첫 단어 (예: Bitter Orange Flower -> Orange)
    if ' ' in name:
        search_candidates.append(name.split(' ')[0])

    # 중복 제거 및 유효성 확인
    search_candidates = list(dict.fromkeys([c for c in search_candidates if c and len(c) > 1]))

    cid = None
    for candidate in search_candidates:
        cid_url = f"{BASE_URL}/compound/name/{candidate}/cids/JSON"
        try:
            response = requests.get(cid_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                cid = data.get('IdentifierList', {}).get('CID', [None])[0]
                if cid:
                    info["pubchem_cid"] = cid
                    break
        except Exception:
            continue
        time.sleep(0.2) # 재시도 사이 짧은 지연

    if not cid:
        return info

    # 2. 속성 정보 조회 (Formula, Weight)
    props_url = f"{BASE_URL}/compound/cid/{info['pubchem_cid']}/property/MolecularFormula,MolecularWeight/JSON"
    try:
        time.sleep(0.5) # API 호출 사이 딜레이
        response = requests.get(props_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            props = data.get('PropertyTable', {}).get('Properties', [{}])[0]
            info["molecular_formula"] = props.get("MolecularFormula", "N/A")
            info["molecular_weight"] = props.get("MolecularWeight", "N/A")
    except Exception:
        pass

    # 3. CAS 번호 조회
    time.sleep(0.5) # API 호출 사이 딜레이
    info["cas_number"] = get_cas_from_synonyms(info["pubchem_cid"])

    return info

def main():
    input_file = "data/raw/fragrance_ingredients_v4.csv"
    output_file = "data/raw/pubchem_raw.csv"

    # 파일 읽기 (첫 줄이 파일명이므로 skiprows=1)
    if not os.path.exists(input_file):
        print(f"Error: {input_file} 파일을 찾을 수 없습니다.")
        return

    df = pd.read_csv(input_file, skiprows=1)
    
    # 중복 제거된 원료명 목록 (학명 포함하여 순회)
    ingredients_to_process = df[['name', 'scientific_name']].drop_duplicates()
    total = len(ingredients_to_process)
    
    results = []
    
    print(f"총 {total}개의 원료 정보를 PubChem에서 수집을 시작합니다...")

    for i, (_, row) in enumerate(ingredients_to_process.iterrows(), 1):
        name = row['name']
        sci_name = row['scientific_name']
        
        # 데이터 수집
        pubchem_info = get_pubchem_data(name, sci_name)
        
        # 결과 결합
        result_row = {
            "name": name,
            **pubchem_info
        }
        results.append(result_row)
        
        # 진행 상황 출력
        cid_str = f"CID {pubchem_info['pubchem_cid']}" if pubchem_info['pubchem_cid'] != "N/A" else "Not Found"
        print(f"[{i}/{total}] {name} → {cid_str}")
        
        # API 부하 방지를 위한 필수 딜레이
        time.sleep(0.5)

    # 결과 저장
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    
    print(f"\n수집 완료! 결과가 '{output_file}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
