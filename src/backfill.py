#!/usr/bin/env python3
"""
数据补充脚本
用今天的新闻 + Claude 分析，生成过去 N 天的数据文件
用于首次启动时快速建立历史数据库
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
    print(f"🔄 数据补充模式：补充过去 {n_days} 天")
    print(f"{'='*55}\n")

    # Scrape news once — reuse across all days
    china_news = get_all_china_news()
    global_news = get_all_global_news()

    if not china_news and not global_news:
        print("❌ 新闻获取失败，退出")
        sys.exit(1)

    print(f"\n📊 爬取完成：中国 {len(china_news)} 条 / 国际 {len(global_news)} 条\n")

    dates_to_fill = []
    for i in range(n_days, 0, -1):  # oldest first
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

    print(f"\n需要补充 {len(dates_to_fill)} 天的数据\n")

    success = 0
    for i, date_str in enumerate(dates_to_fill, 1):
        print(f"[{i}/{len(dates_to_fill)}] 📅 分析 {date_str}...")
        analysis = analyze_news(china_news, global_news, mode='daily')

        if analysis:
            analysis['date'] = date_str  # Override with correct date
            raw = {
                'date': date_str,
                'mode': 'daily',
                'china_news': china_news,
                'global_news': global_news,
                'analysis': analysis,
            }
            with open(data_dir / f"{date_str}.json", 'w', encoding='utf-8') as f:
                json.dump(raw, f, ensure_ascii=False, indent=2)
            print(f"    ✅ 已保存 data/{date_str}.json")
            success += 1
        else:
            print(f"    ❌ 分析失败，跳过")

        # Brief pause between API calls
        if i < len(dates_to_fill):
            time.sleep(3)

    print(f"\n✅ 补充完成：{success}/{len(dates_to_fill)} 天成功")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='补充历史数据')
    parser.add_argument('--days', type=int, default=7, help='补充天数（默认7天）')
    parser.add_argument('--force', action='store_true', help='强制重新生成（覆盖已有数据）')
    args = parser.parse_args()
    backfill(n_days=args.days, skip_existing=not args.force)
