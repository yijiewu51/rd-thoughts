#!/usr/bin/env python3
"""
数据补充脚本 — 基于真实历史新闻
- 国际：HackerNews Algolia API（按日期查询真实历史）
- 中国：36kr + 虎嗅 RSS（按日期过滤）
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from crawlers.china_news import get_all_china_news
from crawlers.global_news import get_all_global_news
from analyzer import analyze_news


def backfill(n_days=7, skip_existing=True):
    today = datetime.now()
    root = Path(__file__).parent.parent
    data_dir = root / 'data'
    data_dir.mkdir(exist_ok=True)

    print(f"\n{'='*55}")
    print(f"🔄 数据补充：过去 {n_days} 天（真实历史新闻）")
    print(f"{'='*55}\n")

    dates_to_fill = []
    for i in range(n_days, 0, -1):
        day = today - timedelta(days=i)
        date_str = day.strftime('%Y-%m-%d')
        data_file = data_dir / f"{date_str}.json"
        if skip_existing and data_file.exists():
            print(f"⏭️  {date_str} 已存在，跳过")
        else:
            dates_to_fill.append(date_str)

    if not dates_to_fill:
        print("✅ 所有日期已存在，无需补充")
        return

    print(f"需要补充 {len(dates_to_fill)} 天\n")

    success = 0
    for idx, date_str in enumerate(dates_to_fill, 1):
        print(f"\n[{idx}/{len(dates_to_fill)}] ━━ {date_str} ━━")

        # Fetch real news for this specific date
        china_news = get_all_china_news(date_str=date_str)
        global_news = get_all_global_news(date_str=date_str)

        total = len(china_news) + len(global_news)
        if total == 0:
            print(f"  ❌ 无法获取 {date_str} 的新闻，跳过")
            continue

        print(f"  📊 {date_str}：中国 {len(china_news)} 条 / 国际 {len(global_news)} 条")

        analysis = analyze_news(china_news, global_news, mode='daily')
        if analysis:
            analysis['date'] = date_str
            raw = {
                'date': date_str,
                'mode': 'daily',
                'china_news': china_news,
                'global_news': global_news,
                'analysis': analysis,
            }
            with open(data_dir / f"{date_str}.json", 'w', encoding='utf-8') as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
            print(f"  ✅ 已保存 data/{date_str}.json")
            success += 1
        else:
            print(f"  ❌ {date_str} Claude 分析失败")

        if idx < len(dates_to_fill):
            time.sleep(2)

    print(f"\n{'='*55}")
    print(f"✅ 补充完成：{success}/{len(dates_to_fill)} 天成功")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--force', action='store_true', help='覆盖已有数据')
    args = parser.parse_args()
    backfill(n_days=args.days, skip_existing=not args.force)
