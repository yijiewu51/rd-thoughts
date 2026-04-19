"""
国际热点新闻爬取
来源：Hacker News、Reddit worldnews、Reddit technology
"""

import requests
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0; +https://github.com/yijiewu51)',
    'Accept': 'application/json',
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


def get_reddit_news(subreddit, label, limit=10):
    """Reddit 指定版块 Top Posts (今日)"""
    try:
        url = f"https://www.reddit.com/r/{subreddit}/top.json?limit={limit}&t=day"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        posts = data.get('data', {}).get('children', [])
        result = []
        for p in posts:
            d = p.get('data', {})
            if d.get('stickied') or not d.get('title'):
                continue
            result.append({
                'title': d['title'],
                'source': f'Reddit r/{subreddit}',
                'hot': f"↑{d.get('score', 0)}",
                'url': f"https://reddit.com{d.get('permalink', '')}",
                'summary': d.get('selftext', '')[:150],
            })
        print(f"  Reddit r/{subreddit}: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  Reddit r/{subreddit} 失败: {e}")
        return []


def get_all_global_news():
    """汇总所有国际热点新闻，去重后返回最多 15 条"""
    print("📡 正在获取国际热点新闻...")
    hn = get_hackernews_top()
    world = get_reddit_news('worldnews', 'worldnews', 10)
    tech = get_reddit_news('technology', 'technology', 5)

    all_news = hn + world + tech
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
