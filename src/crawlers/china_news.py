"""
中国热点新闻爬取
来源：微博热搜、百度热搜、知乎热榜、36kr RSS
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}


def get_weibo_hot():
    """微博热搜 Top 10"""
    try:
        url = "https://weibo.com/ajax/side/hotSearch"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        items = data.get('data', {}).get('realtime', [])
        result = []
        for item in items:
            if item.get('word') and len(result) < 10:
                result.append({
                    'title': item.get('note') or item.get('word', ''),
                    'source': '微博热搜',
                    'hot': str(item.get('num', '')),
                    'url': f"https://s.weibo.com/weibo?q=%23{item.get('word', '')}%23",
                    'summary': '',
                })
        print(f"  微博热搜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  微博热搜失败: {e}")
        return []


def get_baidu_hot():
    """百度热搜 Top 10"""
    try:
        url = "https://top.baidu.com/board?tab=realtime"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')

        # Try multiple selectors
        items = soup.select('.c-single-text-ellipsis')
        if not items:
            items = soup.select('[class*="title_"]')
        if not items:
            # Try extracting from script tag
            for script in soup.find_all('script'):
                if 'hotsearch' in (script.string or '').lower():
                    break

        result = []
        for item in items[:10]:
            text = item.get_text(strip=True)
            if text and len(text) > 2:
                result.append({
                    'title': text,
                    'source': '百度热搜',
                    'hot': '',
                    'url': f"https://www.baidu.com/s?wd={text}",
                    'summary': '',
                })
        print(f"  百度热搜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  百度热搜失败: {e}")
        return []


def get_zhihu_hot():
    """知乎热榜 Top 10"""
    try:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10"
        headers = {
            **HEADERS,
            'x-api-version': '3.0.91',
            'x-app-za': 'OS=Web',
        }
        resp = requests.get(url, headers=headers, timeout=15)
        data = resp.json()
        items = data.get('data', [])
        result = []
        for item in items[:10]:
            target = item.get('target', {})
            title = target.get('title', '')
            if title:
                result.append({
                    'title': title,
                    'source': '知乎热榜',
                    'hot': str(item.get('detail_text', '')),
                    'url': f"https://www.zhihu.com/question/{target.get('id', '')}",
                    'summary': target.get('excerpt', '')[:150],
                })
        print(f"  知乎热榜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  知乎热榜失败: {e}")
        return []


def get_36kr_news():
    """36kr 科技创业 RSS Top 10"""
    try:
        feed = feedparser.parse('https://36kr.com/feed', request_headers=HEADERS)
        result = []
        for entry in feed.entries[:10]:
            title = entry.get('title', '').strip()
            if title:
                summary = entry.get('summary', '')
                # Strip HTML tags from summary
                if summary:
                    soup = BeautifulSoup(summary, 'lxml')
                    summary = soup.get_text(strip=True)[:200]
                result.append({
                    'title': title,
                    'source': '36氪',
                    'hot': '',
                    'url': entry.get('link', ''),
                    'summary': summary,
                })
        print(f"  36kr: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  36kr 失败: {e}")
        return []


def get_all_china_news():
    """汇总所有中国热点新闻，去重后返回最多 15 条"""
    print("📡 正在获取中国热点新闻...")
    weibo = get_weibo_hot()
    baidu = get_baidu_hot()
    zhihu = get_zhihu_hot()
    kr36 = get_36kr_news()

    all_news = weibo + zhihu + kr36 + baidu  # Priority order
    seen = set()
    unique = []
    for item in all_news:
        key = item['title'][:15]  # Fuzzy dedup
        if key not in seen and item['title']:
            seen.add(key)
            unique.append(item)
        if len(unique) >= 15:
            break

    print(f"✅ 中国新闻共 {len(unique)} 条")
    return unique
