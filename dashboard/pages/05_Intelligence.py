"""
05_Intelligence.py
------------------
Sillage — Fragrance Industry Signal
섹션 1: Community Pulse (Reddit r/fragrance — PRAW)
섹션 2: Industry News (IFRA RSS + Perfumer & Flavorist RSS)
섹션 3: Academic Signal (Semantic Scholar API — 무료, 키 불필요)

API 키 관리:
  Reddit PRAW → .env (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT)
  Semantic Scholar → 키 불필요
  RSS → 키 불필요
"""

import streamlit as st
import os
import re
from datetime import datetime, timedelta
from collections import Counter

st.set_page_config(
    page_title="Intelligence — Sillage",
    page_icon="◈",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Serif+Display&display=swap');

:root {
    --ink:    #1a1a18;
    --paper:  #faf9f7;
    --muted:  #6b6860;
    --rule:   #e4e0d8;
    --active: #2d6a4f;
    --gold:   #b5935a;
}

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--paper);
    color: var(--ink);
}
[data-testid="stSidebar"] { background-color: var(--ink) !important; }
[data-testid="stSidebarNav"] span {
    color: #c8c4bc !important;
    font-size: 13px; font-weight: 400;
    letter-spacing: 0.04em; text-transform: uppercase;
}

.pg-eyebrow {
    font-size: 11px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.4rem;
}
.pg-title {
    font-family: 'DM Serif Display', serif;
    font-size: 40px; color: var(--ink);
    margin-bottom: 0.3rem; line-height: 1;
}
.pg-sub { font-size: 14px; color: var(--muted); margin-bottom: 2rem; }

.sec-label {
    font-size: 10px; font-weight: 500;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--muted); margin-bottom: 0.8rem; margin-top: 2rem;
    padding-bottom: 0.5rem; border-bottom: 1px solid var(--rule);
}
.section-rule {
    border: none; border-top: 1px solid var(--rule); margin: 2rem 0;
}
.sec-header {
    font-family: 'DM Serif Display', serif;
    font-size: 22px; color: var(--ink);
    margin-bottom: 0.3rem; margin-top: 2rem;
}
.sec-source {
    font-size: 11px; color: var(--muted);
    margin-bottom: 1.2rem;
}

/* 순위 행 */
.rank-row {
    display: flex; align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--rule);
    gap: 12px; font-size: 13px;
}
.rank-num  { color: var(--muted); min-width: 28px; font-size: 12px; }
.rank-name { font-weight: 500; flex: 1; }
.rank-bar-wrap { flex: 2; }
.rank-bar-bg   { background: var(--rule); height: 3px; border-radius: 2px; }
.rank-bar-fill { background: var(--ink);  height: 3px; border-radius: 2px; }
.rank-count { color: var(--muted); font-size: 12px; min-width: 60px; text-align: right; }

/* 트렌딩 키워드 */
.kw-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.6rem 0; border-bottom: 1px solid var(--rule);
    font-size: 13px;
}
.kw-name  { font-weight: 400; color: var(--ink); }
.kw-delta { font-weight: 500; color: var(--active); font-size: 12px; }

/* 뉴스 카드 */
.news-row {
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--rule);
}
.news-title { font-size: 14px; font-weight: 500; color: var(--ink); }
.news-meta  { font-size: 12px; color: var(--muted); margin-top: 3px; }

/* 논문 카드 */
.paper-row {
    padding: 0.9rem 0;
    border-bottom: 1px solid var(--rule);
}
.paper-title { font-size: 14px; font-weight: 500; color: var(--ink); }
.paper-meta  { font-size: 12px; color: var(--muted); margin-top: 3px; }

/* placeholder */
.intel-placeholder {
    background: white;
    border: 1px solid var(--rule);
    border-left: 3px solid var(--gold);
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    font-size: 13px; color: var(--muted);
    border-radius: 0 3px 3px 0;
    line-height: 1.7;
}

.empty-state {
    font-size: 13px; color: var(--muted);
    padding: 1rem 0;
    border-top: 1px solid var(--rule);
    border-bottom: 1px solid var(--rule);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# Reddit PRAW 로드
# API 키: .env → REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
# 키 없으면 placeholder 표시
# ─────────────────────────────────────────
def get_reddit_client():
    """
    .env에서 Reddit API 키 로드
    praw 라이브러리 사용 (requirements.txt에 이미 있음)
    반환: praw.Reddit 인스턴스 또는 None
    """
    try:
        import praw
        from dotenv import load_dotenv
        load_dotenv()

        client_id     = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent    = os.getenv("REDDIT_USER_AGENT", "sillage-platform/1.0")

        if not client_id or not client_secret:
            return None

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )
        return reddit
    except Exception:
        return None


@st.cache_data(ttl=1800)  # 30분 캐시 — 과도한 요청 방지
def fetch_reddit_posts(days: int):
    """
    r/fragrance에서 최근 N일 게시글 수집
    - 원료명 언급 빈도 집계
    - 향수명, 브랜드명 집계
    - 키워드 트렌드 집계

    rate limit: PRAW는 분당 60회 제한
    → 한 번 호출 시 최대 500개 게시글만 수집
    """
    reddit = get_reddit_client()
    if reddit is None:
        return None

    try:
        subreddit  = reddit.subreddit("fragrance")
        cutoff     = datetime.utcnow() - timedelta(days=days)
        posts      = []

        for post in subreddit.new(limit=500):
            if datetime.utcfromtimestamp(post.created_utc) < cutoff:
                break
            posts.append({
                "title":  post.title,
                "score":  post.score,
                "comments": post.num_comments,
                "url":    f"https://reddit.com{post.permalink}",
                "text":   post.selftext,
                "created": datetime.utcfromtimestamp(post.created_utc),
            })

        return posts
    except Exception as e:
        st.error(f"Reddit API 오류: {e}")
        return None


def analyze_reddit(posts: list, curated_names: list):
    """
    게시글 텍스트에서 원료명/향수명/브랜드 빈도 집계
    curated_names: DB의 CURATED 원료명 목록 (이동 가능한 원료)
    """
    if not posts:
        return {}

    all_text = " ".join([
        p["title"] + " " + p.get("text", "") for p in posts
    ]).lower()

    # 원료 언급 빈도
    ingredient_counter = Counter()
    for name in curated_names:
        count = len(re.findall(r'\b' + re.escape(name.lower()) + r'\b', all_text))
        if count > 0:
            ingredient_counter[name] = count

    # 주요 브랜드 빈도 (하드코딩 — 업계 주요 브랜드)
    BRANDS = [
        "Dior", "Chanel", "Guerlain", "YSL", "Hermes", "Creed",
        "Tom Ford", "Jo Malone", "Maison Margiela", "Byredo",
        "Le Labo", "Diptyque", "Serge Lutens", "Amouage",
    ]
    brand_counter = Counter()
    for brand in BRANDS:
        count = len(re.findall(
            r'\b' + re.escape(brand.lower()) + r'\b', all_text
        ))
        if count > 0:
            brand_counter[brand] = count

    return {
        "ingredients": ingredient_counter.most_common(10),
        "brands":      brand_counter.most_common(5),
        "post_count":  len(posts),
    }


# ─────────────────────────────────────────
# RSS 피드 로드
# IFRA + Perfumer & Flavorist
# 키 불필요, feedparser 사용
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)  # 1시간 캐시
def fetch_rss(url: str, max_items: int = 5):
    """
    RSS 피드 파싱
    feedparser 라이브러리 사용
    requirements.txt에 없으면 추가 필요
    """
    try:
        import feedparser
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:max_items]:
            items.append({
                "title":   entry.get("title", "—"),
                "date":    entry.get("published", "—"),
                "link":    entry.get("link", "#"),
                "summary": entry.get("summary", "")[:200],
            })
        return items
    except Exception as e:
        return []


# ─────────────────────────────────────────
# Semantic Scholar API
# 무료, API 키 불필요
# rate limit: 100 req/5min
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_semantic_scholar(query: str, limit: int = 5):
    """
    Semantic Scholar 공개 API
    엔드포인트: https://api.semanticscholar.org/graph/v1/paper/search
    키 불필요
    """
    try:
        import requests
        url    = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query":  query,
            "limit":  limit,
            "fields": "title,year,externalIds,authors",
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []

        data   = resp.json()
        papers = []
        for paper in data.get("data", []):
            doi = (paper.get("externalIds") or {}).get("DOI", "")
            papers.append({
                "title":   paper.get("title", "—"),
                "year":    paper.get("year", "—"),
                "doi":     doi,
                "doi_url": f"https://doi.org/{doi}" if doi else "",
            })
        return papers
    except Exception as e:
        return []


# ─────────────────────────────────────────
# DB — CURATED 원료명 로드
# ─────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_curated_names():
    import sqlite3
    db_path = "data/fragrance_db.sqlite"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    import pandas as pd
    df = pd.read_sql(
        "SELECT name, data_source FROM ingredients", conn
    )
    conn.close()
    return df[
        df["data_source"].str.contains(
            "notion_manual|user", case=False, na=False
        )
    ]["name"].tolist()


# ─────────────────────────────────────────
# 섹션 1 — Community Pulse
# ─────────────────────────────────────────
def render_community_pulse(days: int, curated_names: list):
    st.markdown("""
    <div class="sec-header">Community Pulse</div>
    <div class="sec-source">
        source: Reddit r/fragrance · PRAW 실시간
        · API 키: .env → REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET
    </div>
    """, unsafe_allow_html=True)

    reddit_client = get_reddit_client()

    if reddit_client is None:
        st.markdown("""
        <div class="intel-placeholder">
            <strong>Reddit API 키가 설정되지 않았습니다.</strong><br>
            .env 파일에 아래를 추가하세요:<br>
            <code>REDDIT_CLIENT_ID=your_id</code><br>
            <code>REDDIT_CLIENT_SECRET=your_secret</code><br>
            <code>REDDIT_USER_AGENT=sillage-platform/1.0</code><br><br>
            키 발급: <a href="https://www.reddit.com/prefs/apps" target="_blank">
            reddit.com/prefs/apps</a> (무료)
        </div>
        """, unsafe_allow_html=True)
        return

    with st.spinner("Reddit r/fragrance 데이터 수집 중..."):
        posts = fetch_reddit_posts(days)

    if not posts:
        st.markdown(
            '<div class="empty-state">데이터를 가져올 수 없습니다.</div>',
            unsafe_allow_html=True
        )
        return

    result = analyze_reddit(posts, curated_names)

    c1, c2 = st.columns(2)

    with c1:
        # TOP INGREDIENTS
        st.markdown('<div class="sec-label">Top Ingredients</div>',
                    unsafe_allow_html=True)
        ingredients = result.get("ingredients", [])
        if ingredients:
            max_count = ingredients[0][1] if ingredients else 1
            for i, (name, count) in enumerate(ingredients, 1):
                bar_pct = round(count / max_count * 100)
                # CURATED 원료만 링크 연결 가능
                in_archive = name in curated_names
                name_html = (
                    f'<a href="/01_Ingredients" target="_self" '
                    f'style="color:var(--ink);text-decoration:underline;">'
                    f'{name}</a>'
                    if in_archive else name
                )
                st.markdown(f"""
                <div class="rank-row">
                    <span class="rank-num">{i}</span>
                    <span class="rank-name">{name_html}</span>
                    <div class="rank-bar-wrap">
                        <div class="rank-bar-bg">
                            <div class="rank-bar-fill"
                                 style="width:{bar_pct}%;"></div>
                        </div>
                    </div>
                    <span class="rank-count">{count:,}회</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
                밑줄 원료 클릭 → Ingredients 페이지 이동
                (CURATED 원료만 가능)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty-state">언급된 원료 없음</div>',
                unsafe_allow_html=True
            )

        # TOP BRANDS
        st.markdown('<div class="sec-label">Top Brands</div>',
                    unsafe_allow_html=True)
        brands = result.get("brands", [])
        if brands:
            for i, (brand, count) in enumerate(brands, 1):
                st.markdown(f"""
                <div class="rank-row">
                    <span class="rank-num">{i}</span>
                    <span class="rank-name">{brand}</span>
                    <span class="rank-count">{count:,}회</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="empty-state">데이터 없음</div>',
                unsafe_allow_html=True
            )

    with c2:
        # TOP FRAGRANCES
        # Reddit 게시글 제목에서 자동 추출 불가 — placeholder
        st.markdown('<div class="sec-label">Top Fragrances</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="intel-placeholder">
            향수명 자동 추출은 NLP 매핑 필요.<br>
            Parfumo CSV 연동 후 향수명 사전 기반으로 구현 예정.
        </div>
        """, unsafe_allow_html=True)

        # TRENDING KEYWORDS
        # 빈도 급상승 계산: 기간 비교 필요 → 현재 단일 기간만 수집
        st.markdown('<div class="sec-label">Trending Keywords</div>',
                    unsafe_allow_html=True)
        st.markdown("""
        <div class="intel-placeholder">
            Trending 계산은 두 기간 비교 필요.<br>
            (현재 기간 vs 이전 기간 빈도 차이)<br>
            Reddit 수집 파이프라인 안정화 후 구현 예정.
        </div>
        """, unsafe_allow_html=True)

        # 수집 통계
        st.markdown(f"""
        <div style="font-size:11px;color:var(--muted);
                    margin-top:1rem;padding-top:0.5rem;
                    border-top:1px solid var(--rule);">
            수집된 게시글: {result.get('post_count', 0):,}개 ·
            기간: 최근 {days}일
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 섹션 2 — Industry News
# ─────────────────────────────────────────
def render_industry_news():
    st.markdown("""
    <div class="sec-header">Industry News</div>
    <div class="sec-source">
        source: IFRA RSS · Perfumer &amp; Flavorist RSS
        · 키 불필요
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="sec-label">Regulatory Updates — IFRA</div>',
                    unsafe_allow_html=True)

        # IFRA는 공개 RSS가 없음 — 공식 사이트 뉴스 페이지 fetch
        # 현재: placeholder, v2에서 스크래핑 또는 RSS 확인 후 구현
        st.markdown("""
        <div class="intel-placeholder">
            IFRA 공식 RSS 피드 확인 중.<br>
            현재: <a href="https://ifrafragrance.org/news"
            target="_blank">ifrafragrance.org/news</a> 참조<br>
            v2에서 자동 파싱 구현 예정.
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="sec-label">Industry News — Perfumer &amp; Flavorist</div>',
                    unsafe_allow_html=True)

        # Perfumer & Flavorist RSS
        PF_RSS = "https://www.perfumerflavorist.com/rss/news"
        items  = fetch_rss(PF_RSS, max_items=5)

        if items:
            for item in items:
                st.markdown(f"""
                <div class="news-row">
                    <div class="news-title">
                        <a href="{item['link']}" target="_blank"
                           style="color:var(--ink);text-decoration:none;">
                           {item['title']}
                        </a>
                    </div>
                    <div class="news-meta">{item['date']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="intel-placeholder">
                Perfumer &amp; Flavorist RSS 연결 중.<br>
                네트워크 상태 또는 RSS URL 변경 시
                자동으로 재시도합니다.
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 섹션 3 — Academic Signal
# ─────────────────────────────────────────
def render_academic():
    st.markdown("""
    <div class="sec-header">Academic Signal</div>
    <div class="sec-source">
        source: Semantic Scholar API · 무료 · API 키 불필요
        · rate limit: 100 req/5min
    </div>
    """, unsafe_allow_html=True)

    # 검색 쿼리 — 향료 특화
    # "fragrance ingredient" 로 좁혀서 향료 외 노이즈 최소화
    QUERY = "fragrance ingredient perfume aroma"

    with st.spinner("Semantic Scholar 논문 검색 중..."):
        papers = fetch_semantic_scholar(QUERY, limit=5)

    if papers:
        for paper in papers:
            doi_html = (
                f'<a href="{paper["doi_url"]}" target="_blank" '
                f'style="color:var(--active);">DOI →</a>'
                if paper["doi_url"] else "DOI 없음"
            )
            st.markdown(f"""
            <div class="paper-row">
                <div class="paper-title">{paper['title']}</div>
                <div class="paper-meta">
                    {paper['year']} · {doi_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="intel-placeholder">
            Semantic Scholar API 연결 중.<br>
            네트워크 상태 확인 후 재시도합니다.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:11px;color:var(--muted);margin-top:0.5rem;">
        검색 쿼리: "fragrance ingredient perfume aroma" ·
        Semantic Scholar 공개 API
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# 메인
# ─────────────────────────────────────────
def main():
    st.markdown("""
    <div class="pg-eyebrow">Sillage — Industry Signal</div>
    <div class="pg-title">Intelligence</div>
    <div class="pg-sub">
        Fragrance Industry Signal —
        Reddit · News · Regulation · Academic
    </div>
    """, unsafe_allow_html=True)

    curated_names = load_curated_names()

    # ── 기간 필터 ────────────────────────────
    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    col_filter, _ = st.columns([2, 3])
    with col_filter:
        days = st.slider(
            "기간 설정 (일)",
            min_value=1,
            max_value=90,
            value=30,
            step=1,
            help="Reddit 수집 기간. 최대 90일."
        )
        # 빠른 선택 버튼
        c7, c30, c90 = st.columns(3)
        with c7:
            if st.button("7일"):
                days = 7
        with c30:
            if st.button("30일"):
                days = 30
        with c90:
            if st.button("90일"):
                days = 90

    st.markdown('<hr style="border:none;border-top:1px solid var(--rule);margin:1rem 0;">',
                unsafe_allow_html=True)

    # ── 섹션 1: Community Pulse ─────────────
    render_community_pulse(days, curated_names)

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 섹션 2: Industry News ────────────────
    render_industry_news()

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 섹션 3: Academic Signal ──────────────
    render_academic()

    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)

    # ── 하단 연결 안내 ───────────────────────
    st.markdown('<div class="sec-label">연동 구조</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:12px;color:var(--muted);line-height:1.9;">
        이 페이지는 업계 전체 흐름을 다룹니다.<br>
        특정 원료의 실시간 신호는
        <a href="/01_Ingredients" target="_self"
           style="color:var(--ink);font-weight:500;">
           Ingredients → Intelligence 탭
        </a>에서 확인하세요.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()