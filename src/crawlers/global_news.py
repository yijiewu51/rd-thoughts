"""
国际热点新闻爬取
支持当天 + 历史日期查询
来源：Hacker News Algolia API、The Guardian API (test key)、GitHub Trending、CoinTelegraph RSS、TechCrunch RSS
"""

import requests
import time
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json',
}


# ── HackerNews Algolia（支持历史日期） ────────────────────────────

def get_hackernews_by_date(date_str=None):
    """
    HN top stories for a specific date (or today if None).
    Uses HN Algolia API — free, no key required.
    """
    try:
        if date_str:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            start = int(dt.timestamp())
            end = start + 86400
            url = (f"https://hn.algolia.com/api/v1/search"
                   f"?tags=story"
                   f"&numericFilters=created_at_i>{start},created_at_i<{end}"
                   f"&hitsPerPage=30")
        else:
            # Today: use standard top stories API
            url = "https://hacker-news.firebaseio.com/v0/topstories.json"
            resp = requests.get(url, timeout=15)
            story_ids = resp.json()[:30]
            stories = []
            for sid in story_ids:
                if len(stories) >= 10:
                    break
                try:
                    item = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                        timeout=8
                    ).json()
                    if item and item.get('type') == 'story' and item.get('score', 0) > 50:
                        ts = item.get('time', 0)
                        pub_dt = datetime.fromtimestamp(ts) if ts else datetime.now()
                        stories.append({
                            'title': item['title'],
                            'source': 'Hacker News',
                            'hot': f"↑{item.get('score', 0)}",
                            'url': item.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                            'summary': '',
                            'date': pub_dt.strftime('%Y-%m-%d'),
                            'time': pub_dt.strftime('%H:%M'),
                        })
                except Exception:
                    continue
                time.sleep(0.1)
            print(f"  Hacker News (today): {len(stories)} 条")
            return stories

        # Historical date path via Algolia
        resp = requests.get(url, headers=HEADERS, timeout=15)
        hits = resp.json().get('hits', [])
        # Sort by points descending
        hits.sort(key=lambda x: x.get('points', 0), reverse=True)
        stories = []
        for hit in hits[:10]:
            if hit.get('title') and hit.get('points', 0) > 10:
                ts = hit.get('created_at_i', 0)
                pub_dt = datetime.fromtimestamp(ts) if ts else datetime.now()
                stories.append({
                    'title': hit['title'],
                    'source': 'Hacker News',
                    'hot': f"↑{hit.get('points', 0)}",
                    'url': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID','')}",
                    'summary': '',
                    'date': pub_dt.strftime('%Y-%m-%d'),
                    'time': pub_dt.strftime('%H:%M'),
                })
        print(f"  Hacker News ({date_str}): {len(stories)} 条")
        return stories
    except Exception as e:
        print(f"  Hacker News 失败: {e}")
        return []


# ── The Guardian（支持历史日期，免费 test key） ────────────────────

def get_guardian_by_date(date_str=None):
    """
    Guardian articles for a specific date.
    Uses api-key=test (official demo key, rate-limited but free).
    """
    try:
        if date_str:
            from_date = date_str
            to_date = date_str
        else:
            today = datetime.now().strftime('%Y-%m-%d')
            from_date = to_date = today

        url = (f"https://content.guardianapis.com/search"
               f"?from-date={from_date}&to-date={to_date}"
               f"&api-key=test&order-by=relevance"
               f"&show-fields=trailText&page-size=10"
               f"&section=world|technology|business|science")

        resp = requests.get(url, timeout=15)
        results = resp.json().get('response', {}).get('results', [])
        stories = []
        for r in results[:10]:
            title = r.get('webTitle', '')
            summary = r.get('fields', {}).get('trailText', '')
            if summary:
                soup = BeautifulSoup(summary, 'lxml')
                summary = soup.get_text(strip=True)[:150]
            if title:
                web_pub = r.get('webPublicationDate', '')  # e.g. "2026-04-19T15:30:00Z"
                pub_date = web_pub[:10] if web_pub else (date_str or datetime.now().strftime('%Y-%m-%d'))
                pub_time = web_pub[11:16] if len(web_pub) >= 16 else ''
                stories.append({
                    'title': title,
                    'source': 'The Guardian',
                    'hot': '',
                    'url': r.get('webUrl', ''),
                    'summary': summary,
                    'date': pub_date,
                    'time': pub_time,
                })
        print(f"  The Guardian ({date_str or 'today'}): {len(stories)} 条")
        return stories
    except Exception as e:
        print(f"  The Guardian 失败: {e}")
        return []


# ── GitHub Trending（仅当天） ─────────────────────────────────────

def get_github_trending():
    try:
        url = "https://github.com/trending?since=daily"
        resp = requests.get(url, headers={**HEADERS, 'Accept': 'text/html'}, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        repos = soup.select('article.Box-row')[:8]
        result = []
        for repo in repos:
            name_el = repo.select_one('h2 a')
            desc_el = repo.select_one('p')
            stars_el = repo.select_one('a[href*="/stargazers"]')
            if not name_el:
                continue
            name = name_el.get_text(strip=True).replace('\n', '').replace(' ', '')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            stars = stars_el.get_text(strip=True) if stars_el else ''
            result.append({
                'title': f"{name} — {desc}" if desc else name,
                'source': 'GitHub Trending',
                'hot': f"⭐{stars}",
                'url': f"https://github.com{name_el.get('href', '')}",
                'summary': desc[:150],
            })
        print(f"  GitHub Trending: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  GitHub Trending 失败: {e}")
        return []


# ── CoinTelegraph RSS（加密货币/Web3，支持历史日期过滤） ────────────

def get_cointelegraph_by_date(date_str=None):
    try:
        feed = feedparser.parse('https://cointelegraph.com/rss', request_headers=HEADERS)
        result = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue
            if date_str:
                pub = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub:
                    if datetime(*pub[:3]).strftime('%Y-%m-%d') != date_str:
                        continue
            pub = entry.get('published_parsed') or entry.get('updated_parsed')
            pub_date = datetime(*pub[:3]).strftime('%Y-%m-%d') if pub else (date_str or datetime.now().strftime('%Y-%m-%d'))
            pub_time = f"{pub[3]:02d}:{pub[4]:02d}" if pub else ''
            result.append({
                'title': title,
                'source': 'CoinTelegraph',
                'hot': '',
                'url': entry.get('link', ''),
                'summary': BeautifulSoup(entry.get('summary', ''), 'lxml').get_text(strip=True)[:150],
                'date': pub_date,
                'time': pub_time,
            })
            if len(result) >= 5:
                break
        label = date_str or 'today'
        print(f"  CoinTelegraph ({label}): {len(result)} 条")
        return result
    except Exception as e:
        print(f"  CoinTelegraph 失败: {e}")
        return []


# ── TechCrunch RSS（科技创业，支持历史日期过滤） ───────────────────

def get_techcrunch_by_date(date_str=None):
    try:
        feed = feedparser.parse('https://techcrunch.com/feed/', request_headers=HEADERS)
        result = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue
            if date_str:
                pub = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub:
                    if datetime(*pub[:3]).strftime('%Y-%m-%d') != date_str:
                        continue
            pub = entry.get('published_parsed') or entry.get('updated_parsed')
            pub_date = datetime(*pub[:3]).strftime('%Y-%m-%d') if pub else (date_str or datetime.now().strftime('%Y-%m-%d'))
            pub_time = f"{pub[3]:02d}:{pub[4]:02d}" if pub else ''
            result.append({
                'title': title,
                'source': 'TechCrunch',
                'hot': '',
                'url': entry.get('link', ''),
                'summary': BeautifulSoup(entry.get('summary', ''), 'lxml').get_text(strip=True)[:150],
                'date': pub_date,
                'time': pub_time,
            })
            if len(result) >= 5:
                break
        label = date_str or 'today'
        print(f"  TechCrunch ({label}): {len(result)} 条")
        return result
    except Exception as e:
        print(f"  TechCrunch 失败: {e}")
        return []


# ── 公开接口 ──────────────────────────────────────────────────────

def get_all_global_news(date_str=None):
    """
    获取国际热点新闻。
    date_str=None → 今天实时新闻
    date_str='YYYY-MM-DD' → 该日期的历史新闻
    """
    is_today = date_str is None
    label = "今日" if is_today else date_str
    print(f"📡 正在获取国际热点新闻（{label}）...")

    hn = get_hackernews_by_date(date_str)
    guardian = get_guardian_by_date(date_str)
    gh = get_github_trending() if is_today else []
    ct = get_cointelegraph_by_date(date_str)
    tc = get_techcrunch_by_date(date_str)

    all_news = hn + guardian + tc + ct + gh
    seen = set()
    unique = []
    for item in all_news:
        key = item['title'][:20]
        if key not in seen and item['title']:
            seen.add(key)
            unique.append(item)
        if len(unique) >= 20:
            break

    print(f"✅ 国际新闻共 {len(unique)} 条")
    return unique
