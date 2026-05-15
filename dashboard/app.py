import streamlit as st
import os
import sqlite3
from datetime import datetime

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Sillage",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# DB 통계 — 동적 수치 추출
# 현재 DB에 없는 수치(MAPPED, REGISTERED)는
# 파이프라인 구축 후 쿼리로 교체 예정
# ─────────────────────────────────────────
def get_db_stats():
    db_path = "data/fragrance_db.sqlite"
    stats = {
        "curated": 0,
        "mapped": 0,        # v2: Pyrfume 매핑 완료 후 동적 전환
        "registered": 0,    # v2: IFRA 수집 완료 후 동적 전환
        "perfume_refs": 59325,  # Parfumo TidyTuesday 2024 고정값
    }

    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ingredients")
            stats["curated"] = cursor.fetchone()[0]
            conn.close()
        except Exception:
            stats["curated"] = 66  # DB 없을 때 fallback
    else:
        stats["curated"] = 66

    return stats


# ─────────────────────────────────────────
# CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display&display=swap');

:root {
    --ink:      #1a1a18;
    --paper:    #faf9f7;
    --muted:    #6b6860;
    --rule:     #e4e0d8;
    --active:   #2d6a4f;
    --gold:     #b5935a;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}

/* 사이드바 */
[data-testid="stSidebar"] {
    background-color: var(--ink) !important;
    border-right: none;
}
[data-testid="stSidebarNav"] span {
    color: #c8c4bc !important;
    font-size: 13px;
    font-weight: 400;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

/* 사이드바 홈 레이블 교체 */
[data-testid="stSidebarNav"] ul li:first-child span {
    visibility: hidden;
    position: relative;
    display: inline-block;
    width: 100%;
}
[data-testid="stSidebarNav"] ul li:first-child span::after {
    content: "SILLAGE";
    visibility: visible;
    position: absolute;
    left: 0;
    top: 0;
    font-family: 'DM Serif Display', serif;
    font-size: 15px;
    letter-spacing: 0.08em;
    color: #f0ece6;
    white-space: nowrap;
}

/* 최상단 상태 바 */
.status-bar {
    display: flex;
    align-items: center;
    gap: 16px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 2.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--rule);
}
.status-dot {
    width: 6px; height: 6px;
    background: var(--active);
    border-radius: 50%;
    display: inline-block;
}
.status-divider { color: var(--rule); }

/* 헤더 */
.masthead {
    margin-bottom: 3rem;
}
.masthead-title {
    font-family: 'DM Serif Display', serif;
    font-size: 64px;
    line-height: 1;
    letter-spacing: -0.02em;
    color: var(--ink);
    margin-bottom: 1rem;
}
.masthead-sub {
    font-size: 16px;
    font-weight: 300;
    color: var(--muted);
    line-height: 1.7;
    max-width: 520px;
}

/* 핵심 수치 배너 */
.kpi-bar {
    display: flex;
    gap: 0;
    border: 1px solid var(--rule);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 3rem;
}
.kpi-cell {
    flex: 1;
    padding: 1.2rem 1.8rem;
    border-right: 1px solid var(--rule);
    background: white;
}
.kpi-cell:last-child { border-right: none; }
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: var(--ink);
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}

/* 플랫폼 소개 */
.intro-block {
    max-width: 680px;
    margin-bottom: 3.5rem;
    padding-left: 1.5rem;
    border-left: 2px solid var(--gold);
}
.intro-block p {
    font-size: 15px;
    line-height: 1.9;
    color: #3a3a36;
    margin-bottom: 1.2rem;
}
.intro-block p:last-child { margin-bottom: 0; }

/* 데이터 품질 범례 */
.legend-title {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1rem;
}
.legend-row {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 0.7rem;
    font-size: 13px;
}
.legend-stars { color: var(--gold); font-size: 12px; min-width: 36px; }
.legend-tag {
    font-weight: 500;
    letter-spacing: 0.06em;
    color: var(--ink);
    min-width: 90px;
}
.legend-desc { color: var(--muted); }
.legend-count {
    font-size: 11px;
    font-weight: 500;
    color: var(--active);
    margin-left: 4px;
}

/* 구분선 */
.section-rule {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 3rem 0;
}

/* 6개 페이지 카드 */
.page-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: var(--rule);
    border: 1px solid var(--rule);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 3.5rem;
}
.page-card {
    background: white;
    padding: 2rem 2.2rem;
    text-decoration: none !important;
    color: var(--ink) !important;
    display: block;
    transition: background 0.15s;
}
.page-card:hover { background: #f5f3ef; }
.page-card-num {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.page-card-title {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    margin-bottom: 0.5rem;
}
.page-card-desc {
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
}

/* 파이프라인 다이어그램 */
.pipeline-title {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 1.5rem;
}
.pipeline-wrap {
    display: flex;
    flex-direction: column;
    gap: 0;
    max-width: 560px;
}
.pipeline-row {
    display: flex;
    align-items: stretch;
}
.pipeline-node {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0.9rem 1.4rem;
    border: 1px solid var(--rule);
    border-bottom: none;
    background: white;
    flex: 1;
}
.pipeline-row:last-child .pipeline-node { border-bottom: 1px solid var(--rule); }
.pipeline-node-label {
    font-size: 13px;
    font-weight: 500;
    color: var(--ink);
    min-width: 200px;
}
.pipeline-node-desc {
    font-size: 12px;
    color: var(--muted);
}
.pipeline-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 0.5rem;
    color: var(--rule);
    font-size: 18px;
}

/* 실시간 연동 */
.realtime-block {
    margin-top: 2rem;
    padding: 1.2rem 1.5rem;
    border: 1px solid var(--rule);
    border-radius: 4px;
    background: #faf9f7;
    max-width: 560px;
}
.realtime-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.8rem;
}
.realtime-row {
    font-size: 13px;
    color: #3a3a36;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.realtime-arrow { color: var(--active); font-weight: 600; }

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    stats = get_db_stats()
    now = datetime.now().strftime("%B %Y")

    # ── 상태 바
    st.markdown(f"""
    <div class="status-bar">
        <span class="status-dot"></span>
        <span>Platform Active</span>
        <span class="status-divider">—</span>
        <span>Last sync: {now}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 헤더
    st.markdown("""
    <div class="masthead">
        <div class="masthead-title">Sillage</div>
        <div class="masthead-sub">
            A fragrance ingredient intelligence platform<br>
            built on personal curation, chemical data,<br>
            and real-time industry signals.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 핵심 수치 3개
    # MAPPED / REGISTERED는 파이프라인 완성 전까지 정적 표시
    st.markdown(f"""
    <div class="kpi-bar">
        <div class="kpi-cell">
            <div class="kpi-value">3,300+</div>
            <div class="kpi-label">Ingredients</div>
        </div>
        <div class="kpi-cell">
            <div class="kpi-value">{stats['curated']}</div>
            <div class="kpi-label">Curated</div>
        </div>
        <div class="kpi-cell">
            <div class="kpi-value">4</div>
            <div class="kpi-label">Data Layers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 플랫폼 소개
    st.markdown(f"""
    <div class="intro-block">
        <p>Fragrance ingredient data is scattered across chemistry databases,
        regulatory bodies, and consumer platforms.</p>
        <p>Sillage integrates PubChem, IFRA, Pyrfume, and Parfumo into a single
        ingredient-level data pipeline — with provenance tracking at every layer.</p>
        <p>At its core: <strong>{stats['curated']} ingredients</strong> personally curated
        through direct olfactory experience. The layer no public database provides.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── 데이터 품질 범례
    st.markdown(f"""
    <div class="legend-title">Data Quality Tiers</div>
    <div class="legend-row">
        <span class="legend-stars">★★★</span>
        <span class="legend-tag">CURATED</span>
        <span class="legend-desc">직접 맡고 기록한 원료 — 전체 4-layer 완성</span>
        <span class="legend-count">{stats['curated']} ingredients</span>
    </div>
    <div class="legend-row">
        <span class="legend-stars">★★☆</span>
        <span class="legend-tag">MAPPED</span>
        <span class="legend-desc">외부 DB 자동 매핑 — 화학정보 + odor descriptor</span>
        <span class="legend-count">~1,500 ingredients</span>
    </div>
    <div class="legend-row">
        <span class="legend-stars">★☆☆</span>
        <span class="legend-tag">REGISTERED</span>
        <span class="legend-desc">IFRA 등록 원료 — Material layer만 완성</span>
        <span class="legend-count">~1,800 ingredients</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 6개 페이지 카드
    st.markdown("""
    <div class="page-grid">
        <a href="/Ingredients" class="page-card" target="_self">
            <div class="page-card-num">① Ingredients</div>
            <div class="page-card-title">Explore</div>
            <div class="page-card-desc">원료별 화학 데이터, 감각 노트, 규제 현황, 시장 빈도를 한 화면에서 탐색합니다.</div>
        </a>
        <a href="/Compare" class="page-card" target="_self">
            <div class="page-card-num">② Compare</div>
            <div class="page-card-title">Side by Side</div>
            <div class="page-card-desc">원료를 나란히 놓고 물성, 규제, 시장 빈도를 비교합니다. 조향사의 선택 흐름을 그대로 반영합니다.</div>
        </a>
        <a href="/Connections" class="page-card" target="_self">
            <div class="page-card-num">③ Connections</div>
            <div class="page-card-title">Network</div>
            <div class="page-card-desc">원료 × 산업 × 향 계열의 연결 구조를 시각화합니다.</div>
        </a>
        <a href="/Market" class="page-card" target="_self">
            <div class="page-card-num">④ Market</div>
            <div class="page-card-title">Occurrence</div>
            <div class="page-card-desc">59,325개 향수 데이터 기반 원료 등장 빈도, 브랜드 분포, 연도별 트렌드를 분석합니다.</div>
        </a>
        <a href="/Intelligence" class="page-card" target="_self">
            <div class="page-card-num">⑤ Intelligence</div>
            <div class="page-card-title">Industry Signal</div>
            <div class="page-card-desc">Reddit, IFRA RSS, Semantic Scholar에서 향료 업계 흐름을 실시간으로 수신합니다.</div>
        </a>
        <a href="/Blend" class="page-card" target="_self">
            <div class="page-card-num">⑥ Blend</div>
            <div class="page-card-title">Compose</div>
            <div class="page-card-desc">원료를 조합하고 향의 구조와 규제 상태를 시뮬레이션합니다.</div>
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 파이프라인 다이어그램
    st.markdown('<div class="pipeline-title">Data Pipeline</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pipeline-wrap">
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">PubChem × IFRA</div>
                <div class="pipeline-node-desc">원료명 + CAS + 화학정보</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">Normalization Layer</div>
                <div class="pipeline-node-desc">정규화 · 중복 제거</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">IFRA Standards</div>
                <div class="pipeline-node-desc">규제 등급 매핑</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">Pyrfume / Leffingwell</div>
                <div class="pipeline-node-desc">Odor descriptor 매핑</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">Parfumo Dataset</div>
                <div class="pipeline-node-desc">향수 빈도 분석 — 59,325 perfumes</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node">
                <div class="pipeline-node-label">66 Curated Records</div>
                <div class="pipeline-node-desc">직접 기록 병합 — 감각 데이터 원본</div>
            </div>
        </div>
        <div class="pipeline-row">
            <div class="pipeline-node" style="background:#f5f3ef;">
                <div class="pipeline-node-label" style="color:#2d6a4f; font-weight:600;">SQLite → Sillage</div>
                <div class="pipeline-node-desc">단일 파이프라인 통합</div>
            </div>
        </div>
    </div>

    <div class="realtime-block">
        <div class="realtime-label">Real-time Signals → Intelligence (⑤)</div>
        <div class="realtime-row"><span class="realtime-arrow">→</span> Reddit r/fragrance</div>
        <div class="realtime-row"><span class="realtime-arrow">→</span> IFRA RSS</div>
        <div class="realtime-row"><span class="realtime-arrow">→</span> Perfumer &amp; Flavorist</div>
        <div class="realtime-row"><span class="realtime-arrow">→</span> Semantic Scholar</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
