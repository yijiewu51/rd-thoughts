"""
融资新闻爬取
来源：TechCrunch Venture RSS + 36kr 融资关键词过滤
"""

import re
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
from .translate import translate_items

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

FUNDING_KW = ["融资", "完成", "轮", "亿元", "万美元", "raises", "funding", "series", "seed", "million", "投资"]

INDUSTRY_KW = {
    "AI / 科技":           ["AI", "人工智能", "大模型", "LLM", "agent", "artificial intelligence"],
    "芯片 / 半导体":        ["芯片", "半导体", "chip", "semiconductor", "foundry"],
    "机器人 / 具身智能":    ["机器人", "具身", "robot", "robotics", "humanoid"],
    "医疗健康":             ["医疗", "健康", "医药", "health", "medical", "biotech", "pharma"],
    "消费 / 零售 / 电商":   ["消费", "零售", "电商", "retail", "ecommerce", "consumer", "brand"],
    "金融 / 金融科技":      ["金融", "支付", "fintech", "finance", "payment", "banking", "insurtech"],
    "教育 / EdTech":        ["教育", "edtech", "education", "learning", "tutoring"],
    "能源 / 清洁能源":      ["能源", "清洁", "新能源", "energy", "climate", "solar", "EV", "battery"],
    "加密货币 / Web3 / DeFi": ["crypto", "web3", "blockchain", "区块链", "defi", "nft", "bitcoin"],
    "出行 / 交通":          ["出行", "自动驾驶", "电动车", "mobility", "autonomous", "vehicle"],
    "宠物 / 宠物经济":      ["宠物", "pet"],
    "潮流 / 时尚 / 运动":  ["时尚", "运动", "潮流", "fashion", "sport", "athletic", "sneaker"],
    "动漫 / 二次元 / IP":  ["动漫", "二次元", "anime", "gaming", "game", "IP"],
    "媒体 / 娱乐 / 内容":  ["媒体", "内容", "娱乐", "media", "content", "streaming", "video"],
    "农业 / 食品":          ["农业", "食品", "agri", "food", "farm"],
}


def _tag_industry(text: str) -> str:
    text_lower = text.lower()
    for industry, keywords in INDUSTRY_KW.items():
        if any(kw.lower() in text_lower for kw in keywords):
            return industry
    return "科技 / 其他"


def _is_funding(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in FUNDING_KW)


def _parse_amount(text: str) -> str:
    m = re.search(r'\$\s*(\d+(?:\.\d+)?)\s*(B|M|billion|million)', text, re.IGNORECASE)
    if m:
        return m.group(0)
    m = re.search(r'(\d+(?:\.\d+)?)\s*(亿|千万|百万|万)?\s*(元|美元|欧元)?', text)
    if m:
        return m.group(0)
    return ""


def get_funding_news(date_str=None) -> list:
    results = []
    today = datetime.now().strftime("%Y-%m-%d")

    # ── TechCrunch Venture ──────────────────────────────────────
    try:
        feed = feedparser.parse("https://techcrunch.com/category/venture/feed/", request_headers=HEADERS)
        for entry in feed.entries[:25]:
            title = entry.get("title", "").strip()
            if not title:
                continue
            summary_raw = entry.get("summary", "")
            summary = BeautifulSoup(summary_raw, "lxml").get_text(strip=True)[:200]
            combined = title + " " + summary
            if not _is_funding(combined):
                continue
            if date_str:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub and datetime(*pub[:3]).strftime("%Y-%m-%d") != date_str:
                    continue
            pub = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_date = datetime(*pub[:3]).strftime("%Y-%m-%d") if pub else today
            results.append({
                "title": title,
                "amount": _parse_amount(combined),
                "industry_tag": _tag_industry(combined),
                "url": entry.get("link", ""),
                "source": "TechCrunch",
                "date": pub_date,
                "summary": summary[:120],
            })
            if len(results) >= 5:
                break
    except Exception as e:
        print(f"  TechCrunch Venture 失败: {e}")

    # ── 36kr 融资过滤 ───────────────────────────────────────────
    try:
        feed = feedparser.parse("https://36kr.com/feed", request_headers=HEADERS)
        for entry in feed.entries[:40]:
            title = entry.get("title", "").strip()
            if not title:
                continue
            summary_raw = entry.get("summary", "")
            summary = BeautifulSoup(summary_raw, "lxml").get_text(strip=True)[:200]
            combined = title + " " + summary
            if not _is_funding(combined):
                continue
            if date_str:
                pub = entry.get("published_parsed") or entry.get("updated_parsed")
                if pub and datetime(*pub[:3]).strftime("%Y-%m-%d") != date_str:
                    continue
            pub = entry.get("published_parsed") or entry.get("updated_parsed")
            pub_date = datetime(*pub[:3]).strftime("%Y-%m-%d") if pub else today
            results.append({
                "title": title,
                "amount": _parse_amount(combined),
                "industry_tag": _tag_industry(combined),
                "url": entry.get("link", ""),
                "source": "36氪",
                "date": pub_date,
                "summary": "",
            })
            if len(results) >= 8:
                break
    except Exception as e:
        print(f"  36kr 融资过滤失败: {e}")

    translate_items(results)
    print(f"  融资动态: {len(results)} 条")
    return results[:8]
