"""
简单翻译工具 — 调用 Google Translate 免费接口，无需 API Key
仅用于将英文新闻标题翻译为中文
"""

import requests
import time

_CACHE = {}


def translate_to_zh(text: str) -> str:
    """将英文文本翻译为中文，失败时返回原文。"""
    if not text or not text.strip():
        return text
    # Check if mostly Chinese already
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    if chinese_chars / max(len(text), 1) > 0.3:
        return text
    if text in _CACHE:
        return _CACHE[text]
    try:
        resp = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text},
            timeout=6,
        )
        data = resp.json()
        translated = ''.join(seg[0] for seg in data[0] if seg[0])
        _CACHE[text] = translated
        return translated
    except Exception:
        return text


def translate_items(items: list, field: str = 'title') -> list:
    """批量翻译列表中每个 item 的指定字段，原地修改并返回。"""
    for item in items:
        original = item.get(field, '')
        if original:
            item[field] = translate_to_zh(original)
            time.sleep(0.05)  # 轻微限速，避免被封
    return items
