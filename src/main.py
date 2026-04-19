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
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from crawlers.china_news import get_all_china_news
from crawlers.global_news import get_all_global_news
from analyzer import analyze_news, analyze_synthesis
from generator import generate_reports, generate_synthesis_reports


def run_daily():
    from datetime import datetime
    date_str = datetime.now().strftime('%Y-%m-%d')
    print(f"\n{'='*55}")
    print(f"🚀 创业情报雷达 — 日报  {date_str}")
    print(f"{'='*55}\n")

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

    print(f"✅ 分析完成，覆盖 {len(analysis.get('industries', []))} 个行业\n")
    generate_reports(china_news, global_news, analysis, date_str, mode='daily')


def _load_daily_data(n_days):
    """加载过去 n 天的日报数据"""
    from datetime import datetime, timedelta
    from pathlib import Path

    root = Path(__file__).parent.parent
    data_dir = root / 'data'
    today = datetime.now()
    results = []

    for i in range(n_days):
        day = today - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        data_file = data_dir / f"{day_str}.json"
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('analysis'):
                results.append(data)

    return results


def run_weekly():
    from datetime import datetime
    today = datetime.now()
    week_str = today.strftime('%Y-W%W')
    print(f"\n{'='*55}")
    print(f"🚀 创业情报雷达 — 周报  {week_str}")
    print(f"{'='*55}\n")

    daily_data = _load_daily_data(7)
    print(f"📦 找到过去 7 天中 {len(daily_data)} 天的数据\n")

    if len(daily_data) < 2:
        print("⚠️ 数据不足（需至少2天），先跑一次日报再生成周报")
        # Fallback: run daily analysis and use it
        china_news = get_all_china_news()
        global_news = get_all_global_news()
        analysis = analyze_news(china_news, global_news, mode='weekly')
        if analysis:
            generate_reports(china_news, global_news, analysis, week_str, mode='weekly')
        return

    synthesis = analyze_synthesis(daily_data, mode='weekly')
    if not synthesis:
        print("❌ 综合分析失败，退出")
        sys.exit(1)

    generate_synthesis_reports(synthesis, week_str, mode='weekly')


def run_monthly():
    from datetime import datetime
    today = datetime.now()
    month_str = today.strftime('%Y-%m')
    print(f"\n{'='*55}")
    print(f"🚀 创业情报雷达 — 月报  {month_str}")
    print(f"{'='*55}\n")

    daily_data = _load_daily_data(30)
    print(f"📦 找到过去 30 天中 {len(daily_data)} 天的数据\n")

    if len(daily_data) < 3:
        print("⚠️ 数据不足（需至少3天），使用当日新闻生成月报")
        china_news = get_all_china_news()
        global_news = get_all_global_news()
        analysis = analyze_news(china_news, global_news, mode='monthly')
        if analysis:
            generate_reports(china_news, global_news, analysis, month_str, mode='monthly')
        return

    synthesis = analyze_synthesis(daily_data, mode='monthly')
    if not synthesis:
        print("❌ 综合分析失败，退出")
        sys.exit(1)

    generate_synthesis_reports(synthesis, month_str, mode='monthly')


def main():
    parser = argparse.ArgumentParser(description='创业情报雷达')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'monthly'], default='daily')
    args = parser.parse_args()

    if args.mode == 'daily':
        run_daily()
    elif args.mode == 'weekly':
        run_weekly()
    elif args.mode == 'monthly':
        run_monthly()


if __name__ == '__main__':
    main()
