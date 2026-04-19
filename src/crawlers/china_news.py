"""
中国热点新闻爬取
支持当天 + 历史日期查询
来源：微博热搜、百度热搜、知乎热榜、36kr（按日期过滤）
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta, timezone

TODAY = datetime.now().strftime('%Y-%m-%d')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}


# ── 实时热搜（仅当天） ────────────────────────────────────────────

def get_weibo_hot():
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
                    'date': TODAY,
                })
        print(f"  微博热搜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  微博热搜失败: {e}")
        return []


def get_baidu_hot():
    try:
        url = "https://top.baidu.com/board?tab=realtime"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, 'lxml')
        items = soup.select('.c-single-text-ellipsis')
        if not items:
            items = soup.select('[class*="title_"]')
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
                    'date': TODAY,
                })
        print(f"  百度热搜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  百度热搜失败: {e}")
        return []


def get_zhihu_hot():
    try:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10"
        resp = requests.get(url, headers={**HEADERS, 'x-api-version': '3.0.91'}, timeout=15)
        data = resp.json()
        result = []
        for item in data.get('data', [])[:10]:
            target = item.get('target', {})
            title = target.get('title', '')
            if title:
                result.append({
                    'title': title,
                    'source': '知乎热榜',
                    'hot': str(item.get('detail_text', '')),
                    'url': f"https://www.zhihu.com/question/{target.get('id', '')}",
                    'summary': target.get('excerpt', '')[:150],
                    'date': TODAY,
                })
        print(f"  知乎热榜: {len(result)} 条")
        return result
    except Exception as e:
        print(f"  知乎热榜失败: {e}")
        return []


# ── 36kr（支持历史日期过滤） ──────────────────────────────────────

def get_36kr_by_date(date_str=None):
    """
    从 36kr RSS 获取新闻。
    date_str=None → 最新文章
    date_str='YYYY-MM-DD' → 仅返回该日发布的文章
    """
    try:
        feed = feedparser.parse('https://36kr.com/feed', request_headers=HEADERS)
        result = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue

            # Date filtering for historical mode
            if date_str:
                pub = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub:
                    entry_date = datetime(*pub[:3]).strftime('%Y-%m-%d')
                    if entry_date != date_str:
                        continue

            summary = entry.get('summary', '')
            if summary:
                summary = BeautifulSoup(summary, 'lxml').get_text(strip=True)[:200]

            pub = entry.get('published_parsed') or entry.get('updated_parsed')
            pub_date = datetime(*pub[:3]).strftime('%Y-%m-%d') if pub else (date_str or TODAY)
            pub_time = f"{pub[3]:02d}:{pub[4]:02d}" if pub else ''
            result.append({
                'title': title,
                'source': '36氪',
                'hot': '',
                'url': entry.get('link', ''),
                'summary': summary,
                'date': pub_date,
                'time': pub_time,
            })
            if len(result) >= 10:
                break

        label = date_str or 'today'
        print(f"  36kr ({label}): {len(result)} 条")
        return result
    except Exception as e:
        print(f"  36kr 失败: {e}")
        return []


# ── 虎嗅 RSS（补充历史，约有近期文章） ───────────────────────────

def get_huxiu_by_date(date_str=None):
    try:
        feed = feedparser.parse('https://www.huxiu.com/rss/0.xml', request_headers=HEADERS)
        result = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()
            if not title:
                continue

            if date_str:
                pub = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub:
                    entry_date = datetime(*pub[:3]).strftime('%Y-%m-%d')
                    if entry_date != date_str:
                        continue

            pub = entry.get('published_parsed') or entry.get('updated_parsed')
            pub_date = datetime(*pub[:3]).strftime('%Y-%m-%d') if pub else (date_str or TODAY)
            pub_time = f"{pub[3]:02d}:{pub[4]:02d}" if pub else ''
            result.append({
                'title': title,
                'source': '虎嗅',
                'hot': '',
                'url': entry.get('link', ''),
                'summary': entry.get('summary', '')[:150],
                'date': pub_date,
                'time': pub_time,
            })
            if len(result) >= 8:
                break

        label = date_str or 'today'
        print(f"  虎嗅 ({label}): {len(result)} 条")
        return result
    except Exception as e:
        print(f"  虎嗅失败: {e}")
        return []


# ── 公开接口 ──────────────────────────────────────────────────────

def get_all_china_news(date_str=None):
    """
    获取中国热点新闻。
    date_str=None → 今天实时新闻（微博+百度+知乎+36kr）
    date_str='YYYY-MM-DD' → 该日期历史新闻（36kr+虎嗅，按日期过滤）
    """
    is_today = date_str is None
    label = "今日" if is_today else date_str
    print(f"📡 正在获取中国热点新闻（{label}）...")

    if is_today:
        weibo = get_weibo_hot()
        baidu = get_baidu_hot()
        zhihu = get_zhihu_hot()
        kr36 = get_36kr_by_date(None)
        huxiu = []
        all_news = weibo + zhihu + kr36 + baidu + huxiu
    else:
        # Historical: RSS sources with date filter
        kr36 = get_36kr_by_date(date_str)
        huxiu = get_huxiu_by_date(date_str)
        all_news = kr36 + huxiu

        # If RSS didn't have articles for that date, fall back to latest
        if len(all_news) < 3:
            print(f"  ⚠️ {date_str} 的 RSS 文章不足，使用最新文章补充")
            kr36_latest = get_36kr_by_date(None)
            huxiu_latest = get_huxiu_by_date(None)
            all_news = kr36_latest + huxiu_latest

    seen = set()
    unique = []
    for item in all_news:
        key = item['title'][:15]
        if key not in seen and item['title']:
            seen.add(key)
            unique.append(item)
        if len(unique) >= 15:
            break

    print(f"✅ 中国新闻共 {len(unique)} 条")
    return unique
