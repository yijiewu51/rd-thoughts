"""
国际热点新闻爬取
来源：Hacker News、Reddit worldnews、GitHub Trending
"""

import requests
import time
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}


def get_hackernews_top():
    """Hacker News Top Stories Top 10"""
    try:
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        resp = requests.get(url, timeout=15)
        story_ids = resp.json()[:30]

        stories = []
        for sid in story_ids:
            if len(stories) >= 10:
                break
            try:
                item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
                item = requests.get(item_url, timeout=8).json()
                if item and item.get('type') == 'story' and item.get('title') and item.get('score', 0) > 50:
                    stories.append({
                        'title': item['title'],
                        'source': 'Hacker News',
                        'hot': f"↑{item.get('score', 0)}",
                        'url': item.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                        'summary': '',
                        'comments': item.get('descendants', 0),
                    })
            except Exception:
                continue
            time.sleep(0.1)

        print(f"  Hacker News: {len(stories)} 条")
        return stories
    except Exception as e:
        print(f"  Hacker News 失败: {e}")
        return []


def get_github_trending():
    """GitHub Trending 今日趋势项目"""
    try:
        url = "https://github.com/trending?since=daily"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        repos = soup.select('article.Box-row')[:10]
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


def get_all_global_news():
    """汇总所有国际热点新闻，去重后返回最多 15 条"""
    print("📡 正在获取国际热点新闻...")
    hn = get_hackernews_top()
    gh = get_github_trending()

    all_news = hn + gh
    seen = set()
    unique = []
    for item in all_news:
        key = item['title'][:20]
        if key not in seen and item['title']:
            seen.add(key)
            unique.append(item)
        if len(unique) >= 15:
            break

    print(f"✅ 国际新闻共 {len(unique)} 条")
    return unique
