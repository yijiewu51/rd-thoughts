#!/usr/bin/env python3
"""
创业情报雷达 — 主入口
用法：
  python src/main.py --mode daily    # 每天运行
  python src/main.py --mode weekly   # 每周运行（周日）
  python src/main.py --mode monthly  # 每月运行（1号）
"""

import argparse
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from crawlers.china_news import get_all_china_news
from crawlers.global_news import get_all_global_news
from analyzer import analyze_news
from generator import generate_reports


def run_daily():
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*50}")
    print(f"🚀 创业情报雷达 — 日报  {date_str}")
    print(f"{'='*50}\n")

    china_news = get_all_china_news()
    global_news = get_all_global_news()

    if not china_news and not global_news:
        print("❌ 所有新闻源均失败，退出")
        sys.exit(1)

    print(f"\n📊 汇总：中国 {len(china_news)} 条 / 国际 {len(global_news)} 条\n")

    analysis = analyze_news(china_news, global_news, mode='daily')
    if not analysis:
        print("❌ Claude 分析失败，退出")
        sys.exit(1)

    generate_reports(china_news, global_news, analysis, date_str, mode='daily')


def run_weekly():
    """读取过去7天的日报数据，生成周报"""
    import json
    import glob
    from datetime import datetime, timedelta
    from pathlib import Path
    from analyzer import analyze_news
    from generator import generate_reports

    root = Path(__file__).parent.parent
    data_dir = root / 'data'

    today = datetime.now()
    week_str = today.strftime('%Y-W%W')
    print(f"\n{'='*50}")
    print(f"🚀 创业情报雷达 — 周报  {week_str}")
    print(f"{'='*50}\n")

    # Collect past 7 days of data
    all_china, all_global = [], []
    seen_titles = set()

    for i in range(7):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        data_file = data_dir / f"{day_str}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get('china_news', []):
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    all_china.append(item)
            for item in data.get('global_news', []):
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    all_global.append(item)

    if not all_china and not all_global:
        print("⚠️ 没有找到过去7天的数据，使用实时数据")
        all_china = get_all_china_news()
        all_global = get_all_global_news()

    print(f"📊 本周汇总：中国 {len(all_china)} 条 / 国际 {len(all_global)} 条\n")

    analysis = analyze_news(all_china[:15], all_global[:15], mode='weekly')
    if not analysis:
        sys.exit(1)

    generate_reports(all_china[:15], all_global[:15], analysis, week_str, mode='weekly')


def run_monthly():
    """读取过去30天的日报数据，生成月报"""
    import json
    from datetime import datetime, timedelta
    from pathlib import Path

    root = Path(__file__).parent.parent
    data_dir = root / 'data'

    today = datetime.now()
    month_str = today.strftime('%Y-%m')
    print(f"\n{'='*50}")
    print(f"🚀 创业情报雷达 — 月报  {month_str}")
    print(f"{'='*50}\n")

    all_china, all_global = [], []
    seen_titles = set()

    for i in range(30):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        data_file = data_dir / f"{day_str}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for item in data.get('china_news', []):
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    all_china.append(item)
            for item in data.get('global_news', []):
                if item['title'] not in seen_titles:
                    seen_titles.add(item['title'])
                    all_global.append(item)

    if not all_china and not all_global:
        print("⚠️ 没有找到过去30天的数据，使用实时数据")
        all_china = get_all_china_news()
        all_global = get_all_global_news()

    print(f"📊 本月汇总：中国 {len(all_china)} 条 / 国际 {len(all_global)} 条\n")

    # For monthly, take top items (most recent / most represented)
    analysis = analyze_news(all_china[:15], all_global[:15], mode='monthly')
    if not analysis:
        sys.exit(1)

    generate_reports(all_china[:15], all_global[:15], analysis, month_str, mode='monthly')


def main():
    parser = argparse.ArgumentParser(description='创业情报雷达')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly'], default='daily',
                        help='运行模式：daily（默认）/ weekly / monthly')
    args = parser.parse_args()

    if args.mode == 'daily':
        run_daily()
    elif args.mode == 'weekly':
        run_weekly()
    elif args.mode == 'monthly':
        run_monthly()


if __name__ == '__main__':
    main()
