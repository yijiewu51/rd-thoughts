"""
报告生成器
输入：新闻数据 + Claude 分析结果
输出：Markdown 文件 + HTML 文件
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# 行业主题色
INDUSTRY_COLORS = {
    "AI / 科技": "#6366f1",
    "芯片 / 半导体": "#0ea5e9",
    "机器人 / 具身智能": "#7c3aed",
    "医疗健康": "#10b981",
    "金融 / 金融科技": "#f59e0b",
    "教育 / EdTech": "#3b82f6",
    "消费 / 零售 / 电商": "#ec4899",
    "能源 / 清洁能源": "#84cc16",
    "出行 / 交通": "#06b6d4",
    "农业 / 食品": "#a78bfa",
    "房产 / 建筑": "#78716c",
    "制造业 / 工业": "#64748b",
    "媒体 / 娱乐 / 内容": "#8b5cf6",
    "宠物 / 宠物经济": "#f97316",
    "潮流 / 时尚 / 运动": "#e11d48",
    "动漫 / 二次元 / IP": "#d946ef",
    "加密货币 / Web3 / DeFi": "#f7931a",
    "政策 / 监管 / 社会": "#ef4444",
}

DIFFICULTY_STYLE = {
    "低": ("🟢", "#c6f6d5", "#276749"),
    "中": ("🟡", "#fefcbf", "#744210"),
    "高": ("🔴", "#fed7d7", "#822727"),
}


def get_industry_color(name):
    for key, color in INDUSTRY_COLORS.items():
        if key in name or name in key:
            return color
    return "#667eea"


# ─────────────────────────── Markdown ───────────────────────────

def generate_markdown(china_news, global_news, analysis, date_str):
    lines = []
    lines.append(f"# 🧠 创业情报日报 — {date_str}\n")
    lines.append(f"> 由 Claude AI 自动生成 · 数据来源：微博、百度、知乎、36氪、Hacker News、Reddit\n")

    # Overall summary
    if analysis.get('overall_summary'):
        lines.append("## 📊 今日趋势总结\n")
        lines.append(f"{analysis['overall_summary']}\n")

    # Top 3
    if analysis.get('top3'):
        lines.append("## 🏆 今日最佳创业机会 TOP 3\n")
        for pick in analysis['top3']:
            medal = ["🥇", "🥈", "🥉"][pick['rank'] - 1]
            lines.append(f"### {medal} #{pick['rank']} {pick['title']}")
            lines.append(f"**行业：** {pick['industry']}")
            lines.append(f"\n{pick['reason']}\n")

    # News
    lines.append("## 📰 今日热点新闻\n")
    lines.append("### 🇨🇳 中国热点\n")
    for i, item in enumerate(china_news[:10], 1):
        title = item['title']
        url = item.get('url', '')
        source = item['source']
        if url:
            lines.append(f"{i}. [{title}]({url}) `{source}`")
        else:
            lines.append(f"{i}. {title} `{source}`")
        if item.get('summary'):
            lines.append(f"   > {item['summary'][:120]}")
    lines.append("")

    lines.append("### 🌍 国际热点\n")
    for i, item in enumerate(global_news[:10], 1):
        title = item['title']
        url = item.get('url', '')
        source = item['source']
        if url:
            lines.append(f"{i}. [{title}]({url}) `{source}`")
        else:
            lines.append(f"{i}. {title} `{source}`")
    lines.append("")

    # Industry analysis
    lines.append("## 💡 行业创业机会分析\n")
    for ind in analysis.get('industries', []):
        emoji = ind.get('emoji', '📌')
        name = ind.get('name', '')
        lines.append(f"---\n### {emoji} {name}\n")

        if ind.get('news_connection'):
            lines.append(f"**📌 新闻关联：** {ind['news_connection']}\n")
        if ind.get('trend'):
            lines.append(f"**📈 核心趋势：** {ind['trend']}\n")

        for opp in ind.get('opportunities', []):
            lines.append(f"#### 💡 {opp['title']}\n")
            lines.append(f"{opp.get('description', '')}\n")
            lines.append(f"| 项目 | 内容 |")
            lines.append(f"|------|------|")
            lines.append(f"| 商业模式 | {opp.get('business_model', '-')} |")
            lines.append(f"| AI 赋能 | {opp.get('ai_angle', '-')} |")
            lines.append(f"| 目标客户 | {opp.get('target_customer', '-')} |")
            lines.append(f"| 市场规模 | {opp.get('market_size', '-')} |")
            lines.append(f"| 难度 | {opp.get('difficulty', '-')} |")
            lines.append(f"| 紧迫性 | {opp.get('urgency', '-')} |")
            lines.append(f"| 🚀 第一步 | {opp.get('first_step', '-')} |")
            lines.append("")

        if ind.get('watch_out'):
            lines.append(f"> ⚠️ **注意：** {ind['watch_out']}\n")

    lines.append("\n---")
    lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')} · [查看所有报告](https://yijiewu51.github.io/rd-thoughts/)*")

    return "\n".join(lines)


# ─────────────────────────── HTML ───────────────────────────

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB',
               'Microsoft YaHei', 'Noto Sans CJK SC', sans-serif;
  background: #f0f4f8;
  color: #1a202c;
  line-height: 1.7;
  font-size: 15px;
}
a { color: inherit; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── Header ── */
.header {
  background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
  color: white;
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  position: sticky;
  top: 0;
  z-index: 200;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.header-left { display: flex; align-items: center; gap: 16px; }
.header-logo { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.5px; }
.header-logo span { color: #a5b4fc; }
.header-date { font-size: 0.85rem; background: rgba(255,255,255,0.1); padding: 4px 12px;
  border-radius: 20px; color: rgba(255,255,255,0.8); }
.header-nav a {
  color: rgba(255,255,255,0.75); font-size: 0.85rem;
  padding: 5px 14px; border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.2);
  margin-left: 8px; transition: all 0.2s;
}
.header-nav a:hover { background: rgba(255,255,255,0.12); text-decoration: none; }
.header-nav a.active { background: rgba(165,180,252,0.2); border-color: #a5b4fc; color: white; }

/* ── Layout ── */
.layout {
  display: flex;
  max-width: 1360px;
  margin: 0 auto;
  padding: 28px 20px;
  gap: 24px;
  align-items: flex-start;
}

/* ── Sidebar ── */
.sidebar {
  width: 190px;
  flex-shrink: 0;
  position: sticky;
  top: 80px;
}
.sidebar-box {
  background: white;
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.sidebar-box h3 {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #f1f5f9;
}
.sidebar-box a {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 10px; border-radius: 8px;
  font-size: 0.82rem; color: #475569;
  margin-bottom: 2px; transition: all 0.15s;
}
.sidebar-box a:hover { background: #f8fafc; color: #1e293b; text-decoration: none; }
.sidebar-box a .dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}

/* ── Main ── */
.main { flex: 1; min-width: 0; }
section { margin-bottom: 24px; }

/* ── Card base ── */
.card {
  background: white; border-radius: 14px;
  padding: 24px; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}

/* ── Summary ── */
.summary-card { border-left: 4px solid #6366f1; }
.section-title {
  font-size: 1rem; font-weight: 700; color: #1e293b;
  margin-bottom: 14px; display: flex; align-items: center; gap: 8px;
}
.summary-text { font-size: 0.925rem; color: #334155; line-height: 1.8; }

/* ── Top 3 ── */
.picks-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.pick-card {
  background: white; border-radius: 12px; padding: 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border-top: 3px solid #e2e8f0;
  transition: transform 0.2s, box-shadow 0.2s;
}
.pick-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.pick-card:nth-child(1) { border-top-color: #f6ad55; }
.pick-card:nth-child(2) { border-top-color: #a0aec0; }
.pick-card:nth-child(3) { border-top-color: #c05621; }
.pick-medal { font-size: 1.8rem; line-height: 1; margin-bottom: 10px; }
.pick-industry { font-size: 0.72rem; color: #94a3b8; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
.pick-title { font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.pick-reason { font-size: 0.8rem; color: #64748b; line-height: 1.6; }

/* ── News ── */
.news-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.news-col-title {
  font-size: 0.875rem; font-weight: 600; color: #374151;
  margin-bottom: 12px; padding-bottom: 8px;
  border-bottom: 2px solid #f1f5f9;
  display: flex; align-items: center; gap: 6px;
}
.news-item {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 9px 0; border-bottom: 1px solid #f8fafc;
}
.news-item:last-child { border-bottom: none; }
.news-num { font-size: 0.72rem; color: #cbd5e1; font-weight: 700; min-width: 18px; padding-top: 2px; }
.news-body { flex: 1; }
.news-title-link { font-size: 0.85rem; color: #1e293b; display: block; margin-bottom: 2px; }
.news-title-link:hover { color: #6366f1; text-decoration: none; }
.news-meta { font-size: 0.72rem; color: #94a3b8; display: flex; gap: 8px; align-items: center; }
.news-source-badge {
  background: #f1f5f9; padding: 1px 7px; border-radius: 10px; color: #64748b;
}
.news-hot { color: #f87171; }
.news-date { color: #94a3b8; font-size: 0.7rem; }

/* ── Industry card ── */
.industry-card {
  background: white; border-radius: 14px; padding: 24px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border-left: 4px solid #e2e8f0;
  margin-bottom: 20px;
}
.industry-header {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px; flex-wrap: wrap;
}
.industry-emoji { font-size: 1.6rem; }
.industry-name { font-size: 1.15rem; font-weight: 700; color: #0f172a; }
.industry-meta-row {
  background: #f8fafc; border-radius: 10px; padding: 14px 16px;
  margin-bottom: 16px;
  display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
}
.meta-block .meta-label {
  font-size: 0.7rem; color: #94a3b8; margin-bottom: 3px;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.meta-block .meta-value { font-size: 0.85rem; color: #334155; }

.opps-title { font-size: 0.875rem; font-weight: 600; color: #475569; margin-bottom: 12px; }

/* ── Opportunity card ── */
.opp-card {
  border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px;
  margin-bottom: 12px; transition: border-color 0.2s;
}
.opp-card:hover { border-color: #c7d2fe; }
.opp-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
.opp-title { font-size: 0.95rem; font-weight: 700; color: #1e293b; }
.opp-tags { display: flex; gap: 5px; flex-shrink: 0; }
.tag {
  font-size: 0.68rem; padding: 2px 8px; border-radius: 10px;
  font-weight: 600; white-space: nowrap;
}
.opp-desc { font-size: 0.855rem; color: #475569; line-height: 1.75; margin-bottom: 12px; }
.opp-details { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.detail-item { background: #f8fafc; border-radius: 7px; padding: 8px 10px; }
.detail-item.action { grid-column: span 2; background: #eff6ff; border-left: 3px solid #3b82f6; }
.detail-label { font-size: 0.68rem; color: #94a3b8; margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.05em; }
.detail-value { font-size: 0.82rem; color: #334155; }
.detail-item.action .detail-label { color: #3b82f6; }
.detail-item.action .detail-value { color: #1d4ed8; font-weight: 500; }

.watch-out {
  background: #fff7ed; border-radius: 8px; padding: 10px 14px;
  font-size: 0.82rem; color: #92400e; margin-top: 12px;
  border-left: 3px solid #f59e0b;
}

/* ── Market badge ── */
.market-badge {
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 9px; border-radius: 20px; font-size: 0.72rem;
  font-weight: 700; letter-spacing: 0.02em; margin-left: auto;
}
.market-badge.up { background: #dcfce7; color: #166534; }
.market-badge.down { background: #fee2e2; color: #991b1b; }
.market-badge.flat { background: #f1f5f9; color: #64748b; }
.market-badge .badge-etf { opacity: 0.7; font-weight: 500; margin-right: 2px; }
.sparkline-wrap { margin-left: 8px; opacity: 0.8; }

/* ── Filter bar ── */
.filter-bar {
  background: white; border-radius: 14px; padding: 14px 18px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07); margin-bottom: 20px;
  display: flex; flex-wrap: wrap; gap: 7px; align-items: center;
}
.filter-label {
  font-size: 0.72rem; color: #94a3b8; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em; margin-right: 4px;
}
.filter-btn {
  padding: 4px 12px; border-radius: 20px; border: 1px solid #e2e8f0;
  background: white; cursor: pointer; font-size: 0.78rem; color: #475569;
  font-family: inherit; transition: all 0.15s; white-space: nowrap;
}
.filter-btn:hover { background: #f8fafc; border-color: #c7d2fe; color: #4338ca; }
.filter-btn.active { background: #eef2ff; border-color: #6366f1; color: #4338ca; font-weight: 600; }
.filter-btn.preset { background: #f0fdf4; border-color: #86efac; color: #166534; }
.filter-btn.preset.active { background: #dcfce7; border-color: #4ade80; }
.industry-card.hidden-industry { display: none; }

/* ── Funding sidebar ── */
.funding-item {
  padding: 8px 0; border-bottom: 1px solid #f1f5f9;
  font-size: 0.8rem;
}
.funding-item:last-child { border-bottom: none; }
.funding-title { color: #1e293b; margin-bottom: 3px; line-height: 1.4; }
.funding-title a { color: inherit; }
.funding-title a:hover { color: #6366f1; text-decoration: none; }
.funding-meta { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.funding-amount { font-weight: 700; color: #059669; font-size: 0.75rem; }
.funding-tag {
  background: #f1f5f9; color: #64748b; padding: 1px 7px;
  border-radius: 10px; font-size: 0.68rem;
}
.funding-source { color: #94a3b8; font-size: 0.68rem; }

/* ── AI Chat ── */
.chat-btn {
  position: fixed; bottom: 28px; right: 28px; z-index: 1000;
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white; font-size: 1.4rem; border: none; cursor: pointer;
  box-shadow: 0 4px 20px rgba(99,102,241,0.5);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.chat-btn:hover { transform: scale(1.08); box-shadow: 0 6px 28px rgba(99,102,241,0.6); }

.chat-panel {
  position: fixed; right: 0; top: 0; bottom: 0; z-index: 1001;
  width: 380px; max-width: 100vw;
  background: #0f172a; display: flex; flex-direction: column;
  box-shadow: -4px 0 32px rgba(0,0,0,0.4);
  transform: translateX(100%); transition: transform 0.3s cubic-bezier(.4,0,.2,1);
}
.chat-panel.open { transform: translateX(0); }
.chat-header {
  padding: 16px 18px; background: #1e1b4b;
  display: flex; align-items: center; justify-content: space-between;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  flex-shrink: 0;
}
.chat-header-title { color: white; font-weight: 700; font-size: 0.95rem; display: flex; align-items: center; gap: 8px; }
.chat-header-sub { color: #a5b4fc; font-size: 0.72rem; margin-top: 1px; }
.chat-close {
  background: none; border: none; color: rgba(255,255,255,0.5);
  font-size: 1.3rem; cursor: pointer; padding: 4px 8px; border-radius: 6px;
}
.chat-close:hover { background: rgba(255,255,255,0.1); color: white; }
.chat-messages {
  flex: 1; overflow-y: auto; padding: 16px;
  display: flex; flex-direction: column; gap: 12px;
  scrollbar-width: thin; scrollbar-color: #334155 transparent;
}
.chat-msg { display: flex; gap: 8px; align-items: flex-start; max-width: 100%; }
.chat-msg.user { flex-direction: row-reverse; }
.chat-avatar {
  width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem;
}
.chat-msg.user .chat-avatar { background: #6366f1; }
.chat-msg.ai .chat-avatar { background: #1e293b; border: 1px solid #334155; }
.chat-bubble {
  padding: 10px 14px; border-radius: 14px; font-size: 0.83rem;
  line-height: 1.65; max-width: calc(100% - 44px);
}
.chat-msg.user .chat-bubble {
  background: #6366f1; color: white; border-bottom-right-radius: 4px;
}
.chat-msg.ai .chat-bubble {
  background: #1e293b; color: #e2e8f0; border-bottom-left-radius: 4px;
  white-space: pre-wrap;
}
.chat-msg.ai .chat-bubble.loading { color: #64748b; }
.chat-suggestions {
  padding: 0 16px 12px; display: flex; flex-wrap: wrap; gap: 6px; flex-shrink: 0;
}
.chat-sugg {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 5px 11px; border-radius: 20px; font-size: 0.73rem;
  cursor: pointer; font-family: inherit; transition: all 0.15s;
}
.chat-sugg:hover { border-color: #6366f1; color: #a5b4fc; background: #1e1b4b; }
.chat-input-row {
  padding: 12px 14px; border-top: 1px solid rgba(255,255,255,0.06);
  display: flex; gap: 8px; flex-shrink: 0;
}
.chat-input {
  flex: 1; background: #1e293b; border: 1px solid #334155; border-radius: 22px;
  padding: 9px 16px; color: white; font-size: 0.85rem; font-family: inherit;
  outline: none; resize: none; max-height: 100px; line-height: 1.4;
}
.chat-input:focus { border-color: #6366f1; }
.chat-input::placeholder { color: #475569; }
.chat-send {
  width: 38px; height: 38px; border-radius: 50%; background: #6366f1;
  border: none; color: white; cursor: pointer; font-size: 1rem;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  transition: background 0.15s;
}
.chat-send:hover { background: #4f46e5; }
.chat-send:disabled { background: #334155; cursor: not-allowed; }
.chat-key-prompt {
  padding: 20px; color: #94a3b8; font-size: 0.83rem; text-align: center;
}
.chat-key-input {
  width: 100%; margin-top: 10px; background: #1e293b; border: 1px solid #334155;
  border-radius: 8px; padding: 8px 12px; color: white; font-size: 0.83rem;
  font-family: inherit; outline: none;
}
.chat-key-input:focus { border-color: #6366f1; }
.chat-key-save {
  margin-top: 8px; width: 100%; padding: 8px; background: #6366f1;
  border: none; border-radius: 8px; color: white; cursor: pointer;
  font-size: 0.83rem; font-family: inherit;
}

/* ── Footer ── */
.footer {
  text-align: center; padding: 32px 20px;
  font-size: 0.8rem; color: #94a3b8;
}
.footer a { color: #6366f1; }

/* ── Mobile ── */
@media (max-width: 900px) {
  .layout { flex-direction: column; padding: 16px; }
  .sidebar { width: 100%; position: static; }
  .sidebar-box { display: flex; flex-wrap: wrap; gap: 6px; }
  .sidebar-box h3 { width: 100%; }
  .sidebar-box a { margin-bottom: 0; }
  .picks-grid { grid-template-columns: 1fr; }
  .news-grid { grid-template-columns: 1fr; }
  .opp-details { grid-template-columns: 1fr; }
  .detail-item.action { grid-column: span 1; }
  .industry-meta-row { grid-template-columns: 1fr; }
}
"""


def difficulty_tag_html(level, label_prefix=""):
    icon, bg, fg = DIFFICULTY_STYLE.get(level, ("⚪", "#f1f5f9", "#64748b"))
    return f'<span class="tag" style="background:{bg};color:{fg}">{icon} {label_prefix}{level}</span>'


def build_sidebar_links(industries):
    links = []
    for ind in industries:
        emoji = ind.get('emoji', '📌')
        name = ind.get('name', '')
        color = get_industry_color(name)
        anchor = name.replace('/', '-').replace(' ', '')
        links.append(
            f'<a href="#{anchor}">'
            f'<span class="dot" style="background:{color}"></span>'
            f'{emoji} {name}</a>'
        )
    return "\n".join(links)


def build_news_col_html(news_list, flag, label):
    items_html = []
    for i, item in enumerate(news_list[:10], 1):
        title = item['title']
        url = item.get('url', '')
        source = item['source']
        hot = item.get('hot', '')
        pub_date = item.get('date', '')
        pub_time = item.get('time', '')
        datetime_str = f"{pub_date} {pub_time}".strip() if pub_date else ''
        title_part = (
            f'<a class="news-title-link" href="{url}" target="_blank" rel="noopener">{title}</a>'
            if url else
            f'<span class="news-title-link">{title}</span>'
        )
        hot_part = f'<span class="news-hot">{hot}</span>' if hot else ''
        date_part = f'<span class="news-date">{datetime_str}</span>' if datetime_str else ''
        items_html.append(f"""
        <div class="news-item">
          <span class="news-num">{i}</span>
          <div class="news-body">
            {title_part}
            <div class="news-meta">
              <span class="news-source-badge">{source}</span>
              {date_part}
              {hot_part}
            </div>
          </div>
        </div>""")
    return f"""
    <div>
      <div class="news-col-title">{flag} {label}</div>
      {''.join(items_html)}
    </div>"""


def build_opp_html(opp):
    diff_tag = difficulty_tag_html(opp.get('difficulty', '-'), "难度 ")
    urg_tag = difficulty_tag_html(opp.get('urgency', '-'), "紧迫 ")
    return f"""
    <div class="opp-card">
      <div class="opp-header">
        <div class="opp-title">💡 {opp.get('title', '')}</div>
        <div class="opp-tags">{diff_tag}{urg_tag}</div>
      </div>
      <p class="opp-desc">{opp.get('description', '')}</p>
      <div class="opp-details">
        <div class="detail-item">
          <div class="detail-label">商业模式</div>
          <div class="detail-value">{opp.get('business_model', '-')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">AI 赋能</div>
          <div class="detail-value">{opp.get('ai_angle', '-')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">目标客户</div>
          <div class="detail-value">{opp.get('target_customer', '-')}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">市场规模</div>
          <div class="detail-value">{opp.get('market_size', '-')}</div>
        </div>
        <div class="detail-item action" style="grid-column:span 2">
          <div class="detail-label">🚀 第一步行动</div>
          <div class="detail-value">{opp.get('first_step', '-')}</div>
        </div>
      </div>
    </div>"""


def compute_industry_trend_data(data_dir: Path) -> dict:
    """读取最近7天 JSON，统计每天各行业高紧迫机会数，用于 sparkline。"""
    today = datetime.now()
    trend = {}
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    for date_str in dates:
        fpath = data_dir / f"{date_str}.json"
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text(encoding='utf-8'))
            for ind in data.get('analysis', {}).get('industries', []):
                name = ind.get('name', '')
                high_count = sum(1 for o in ind.get('opportunities', []) if o.get('urgency') == '高')
                trend.setdefault(name, {})
                trend[name][date_str] = high_count
        except Exception:
            pass
    # Normalise to ordered lists
    result = {}
    for name, day_map in trend.items():
        result[name] = [day_map.get(d, 0) for d in dates]
    return result


def build_market_badge_html(signal: dict) -> str:
    if not signal:
        return ''
    pct = signal.get('change_pct')
    etf = signal.get('etf', '')
    is_proxy = signal.get('is_proxy', False)
    if pct is None:
        return ''
    if pct > 0.3:
        cls, arrow = 'up', '▲'
    elif pct < -0.3:
        cls, arrow = 'down', '▼'
    else:
        cls, arrow = 'flat', '—'
    proxy_note = '*' if is_proxy else ''
    return f'<span class="market-badge {cls}"><span class="badge-etf">{etf}{proxy_note}</span>{arrow} {pct:+.1f}%</span>'


def build_filter_bar_html(industries: list) -> str:
    btns = []
    preset_ids = ['AI-科技', '宠物-宠物经济', '教育-EdTech', '消费-零售-电商', '加密货币-Web3-DeFi']
    for ind in industries:
        name = ind.get('name', '')
        emoji = ind.get('emoji', '')
        anchor = name.replace('/', '-').replace(' ', '')
        color = get_industry_color(name)
        btns.append(
            f'<button class="filter-btn" data-id="{anchor}" '
            f'style="border-color:{color}20">{emoji} {name}</button>'
        )
    preset_ids_js = json.dumps(preset_ids)
    btns_html = '\n      '.join(btns)
    return f"""
    <div class="filter-bar" id="filter-bar">
      <span class="filter-label">筛选</span>
      <button class="filter-btn active" id="filter-all">全部</button>
      <button class="filter-btn preset" id="filter-preset">🔥 重点赛道</button>
      {btns_html}
    </div>
    <script>
    (function(){{
      var PRESET = {preset_ids_js};
      var KEY = 'rd_filter_v1';
      var sel = null;
      function save(v){{ try{{ localStorage.setItem(KEY, JSON.stringify(v)); }}catch(e){{}} }}
      function apply(ids){{
        document.querySelectorAll('.industry-card').forEach(function(c){{
          c.classList.toggle('hidden-industry', !(!ids || ids.includes(c.id)));
        }});
        document.querySelectorAll('.filter-btn[data-id]').forEach(function(b){{
          b.classList.toggle('active', !!(ids && ids.includes(b.dataset.id)));
        }});
        document.getElementById('filter-all').classList.toggle('active', !ids);
        document.getElementById('filter-preset').classList.toggle('active',
          !!(ids && ids.length===PRESET.length && PRESET.every(function(p){{return ids.includes(p);}})));
      }}
      function toggle(id){{
        var cur = sel ? sel.slice() : [];
        var i = cur.indexOf(id);
        if(i>=0) cur.splice(i,1); else cur.push(id);
        sel = cur.length ? cur : null; apply(sel); save(sel);
      }}
      document.getElementById('filter-all').onclick = function(){{ sel=null; apply(null); save(null); }};
      document.getElementById('filter-preset').onclick = function(){{ sel=PRESET.slice(); apply(sel); save(sel); }};
      document.querySelectorAll('.filter-btn[data-id]').forEach(function(b){{
        b.onclick = function(){{ toggle(b.dataset.id); }};
      }});
      try{{ var s=JSON.parse(localStorage.getItem(KEY)); if(s&&s.length){{ sel=s; apply(sel); }} }}catch(e){{}}
    }})();
    </script>"""


def build_funding_sidebar_html(funding_news: list) -> str:
    if not funding_news:
        return ''
    items = []
    for f in funding_news[:6]:
        title = f.get('title', '')
        url = f.get('url', '')
        amount = f.get('amount', '')
        tag = f.get('industry_tag', '')
        source = f.get('source', '')
        title_part = f'<a href="{url}" target="_blank" rel="noopener">{title}</a>' if url else title
        amount_part = f'<span class="funding-amount">{amount}</span>' if amount else ''
        items.append(f"""
        <div class="funding-item">
          <div class="funding-title">{title_part}</div>
          <div class="funding-meta">
            {amount_part}
            <span class="funding-tag">{tag}</span>
            <span class="funding-source">{source}</span>
          </div>
        </div>""")
    return f"""
    <div class="sidebar-box" style="margin-top:16px">
      <h3>💰 融资动态</h3>
      {''.join(items)}
    </div>"""


def build_industry_html(ind, trend_values=None, market_signal=None):
    name = ind.get('name', '')
    emoji = ind.get('emoji', '📌')
    color = get_industry_color(name)
    anchor = name.replace('/', '-').replace(' ', '')
    opps_html = "".join(build_opp_html(o) for o in ind.get('opportunities', []))
    watch = ind.get('watch_out', '')
    watch_html = f'<div class="watch-out">⚠️ {watch}</div>' if watch else ''

    market_badge = build_market_badge_html(market_signal) if market_signal else ''

    # Sparkline canvas
    spark_html = ''
    if trend_values and any(v > 0 for v in trend_values):
        vals_json = json.dumps(trend_values)
        spark_html = f'<canvas class="sparkline-wrap" id="spark-{anchor}" data-values=\'{vals_json}\' width="80" height="28"></canvas>'

    return f"""
    <div class="industry-card" id="{anchor}" style="border-left-color:{color}">
      <div class="industry-header">
        <span class="industry-emoji">{emoji}</span>
        <span class="industry-name">{name}</span>
        {spark_html}
        {market_badge}
      </div>
      <div class="industry-meta-row">
        <div class="meta-block">
          <div class="meta-label">📌 新闻关联</div>
          <div class="meta-value">{ind.get('news_connection', '-')}</div>
        </div>
        <div class="meta-block">
          <div class="meta-label">📈 核心趋势</div>
          <div class="meta-value">{ind.get('trend', '-')}</div>
        </div>
      </div>
      <div class="opps-title">创业机会</div>
      {opps_html}
      {watch_html}
    </div>"""


def build_top3_html(top3):
    medals = ["🥇", "🥈", "🥉"]
    cards = []
    for pick in top3:
        medal = medals[pick['rank'] - 1]
        cards.append(f"""
        <div class="pick-card">
          <div class="pick-medal">{medal}</div>
          <div class="pick-industry">{pick.get('industry', '')}</div>
          <div class="pick-title">{pick.get('title', '')}</div>
          <div class="pick-reason">{pick.get('reason', '')}</div>
        </div>""")
    return "\n".join(cards)


def generate_html(china_news, global_news, analysis, date_str, mode='daily',
                  archive_links=None, market_data=None, funding_news=None, trend_data=None):
    mode_label = {"daily": "日报", "weekly": "周报", "monthly": "月报"}.get(mode, "报告")
    industries = analysis.get('industries', [])
    market_data = market_data or {}
    funding_news = funding_news or []
    trend_data = trend_data or {}

    # Embed report context for AI chat (compact JSON)
    chat_context = json.dumps({
        'date': date_str,
        'summary': analysis.get('overall_summary', ''),
        'top3': analysis.get('top3', []),
        'industries': [
            {
                'name': ind.get('name', ''),
                'trend': ind.get('trend', ''),
                'opportunities': [
                    {'title': o.get('title', ''), 'description': o.get('description', ''),
                     'urgency': o.get('urgency', ''), 'first_step': o.get('first_step', '')}
                    for o in ind.get('opportunities', [])
                ]
            }
            for ind in industries
        ]
    }, ensure_ascii=False)

    sidebar_links = build_sidebar_links(industries)
    china_col = build_news_col_html(china_news, "🇨🇳", "中国热点")
    global_col = build_news_col_html(global_news, "🌍", "国际热点")
    filter_bar = build_filter_bar_html(industries)
    funding_sidebar = build_funding_sidebar_html(funding_news)

    industry_sections = "\n".join(
        build_industry_html(
            ind,
            trend_values=trend_data.get(ind.get('name', '')),
            market_signal=market_data.get(ind.get('name', ''))
        )
        for ind in industries
    )
    top3_html = build_top3_html(analysis.get('top3', []))

    archive_section = ""
    if archive_links:
        items = "\n".join(
            f'<li><a href="{link["url"]}">{link["label"]}</a></li>'
            for link in archive_links[-20:][::-1]
        )
        archive_section = f"""
        <div class="card" style="margin-top:24px">
          <div class="section-title">📁 历史报告</div>
          <ul style="list-style:none;columns:2;gap:16px">
            {items}
          </ul>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>创业情报{mode_label} — {date_str}</title>
  <meta name="theme-color" content="#6366f1">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="情报雷达">
  <link rel="apple-touch-icon" href="icon-192.png">
  <link rel="manifest" href="manifest.json">
  <style>{CSS}</style>
  <script src="https://cdn.bootcdn.net/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"
          onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js'"></script>
</head>
<body>

<header class="header">
  <div class="header-left">
    <div class="header-logo">🧠 创业情报<span>雷达</span></div>
    <span class="header-date">{date_str} · {mode_label}</span>
  </div>
  <nav class="header-nav">
    <a href="index.html" class="active">最新</a>
    <a href="archive.html">归档</a>
  </nav>
</header>

<div class="layout">

  <aside class="sidebar">
    <div class="sidebar-box">
      <h3>行业导航</h3>
      {sidebar_links}
    </div>
    {funding_sidebar}
  </aside>

  <main class="main">

    <!-- 趋势总结 -->
    <section>
      <div class="card summary-card">
        <div class="section-title">📊 今日趋势总结</div>
        <p class="summary-text">{analysis.get('overall_summary', '')}</p>
      </div>
    </section>

    <!-- Top 3 -->
    <section>
      <div class="section-title" style="margin-bottom:14px">🏆 今日最佳创业机会 TOP 3</div>
      <div class="picks-grid">
        {top3_html}
      </div>
    </section>

    <!-- 热点新闻 -->
    <section>
      <div class="card">
        <div class="section-title">📰 今日热点新闻</div>
        <div class="news-grid">
          {china_col}
          {global_col}
        </div>
      </div>
    </section>

    <!-- 行业分析 -->
    <section>
      <div class="section-title" style="margin-bottom:16px">💡 全行业创业机会分析</div>
      {filter_bar}
      {industry_sections}
    </section>

    {archive_section}

  </main>
</div>

<footer class="footer">
  由 Claude AI 自动生成 · {date_str} ·
  数据来源：微博 / 百度 / 知乎 / 36氪 / Hacker News / TechCrunch / CoinTelegraph ·
  <a href="https://github.com/yijiewu51/rd-thoughts" target="_blank">GitHub</a>
</footer>

<!-- AI Chat -->
<button class="chat-btn" id="chat-toggle" title="问问 AI">💬</button>

<div class="chat-panel" id="chat-panel">
  <div class="chat-header">
    <div>
      <div class="chat-header-title">🧠 AI 创业顾问</div>
      <div class="chat-header-sub">基于今日报告内容 · {date_str}</div>
    </div>
    <button class="chat-close" id="chat-close">✕</button>
  </div>
  <div class="chat-messages" id="chat-messages">
    <div class="chat-msg ai">
      <div class="chat-avatar">🤖</div>
      <div class="chat-bubble">你好！我已读取今日报告的全部内容，可以回答你关于各行业机会、创业策略、市场分析的问题。有什么想深入了解的？</div>
    </div>
  </div>
  <div class="chat-suggestions" id="chat-suggestions">
    <button class="chat-sugg">🔥 今天最值得做的机会是？</button>
    <button class="chat-sugg">₿ Web3 机会详细分析</button>
    <button class="chat-sugg">🐾 宠物行业怎么切入？</button>
    <button class="chat-sugg">💰 50万预算选哪个赛道？</button>
    <button class="chat-sugg">📈 和上周比有什么变化？</button>
  </div>
  <div class="chat-input-row">
    <textarea class="chat-input" id="chat-input" placeholder="问任何关于创业机会的问题..." rows="1"></textarea>
    <button class="chat-send" id="chat-send">➤</button>
  </div>
</div>

<script>
window.__REPORT__ = {chat_context};

(function() {{
  var KEY_STORE = 'ds_api_key';
  var panel = document.getElementById('chat-panel');
  var msgs = document.getElementById('chat-messages');
  var input = document.getElementById('chat-input');
  var sendBtn = document.getElementById('chat-send');
  var history = [];

  document.getElementById('chat-toggle').onclick = function() {{ panel.classList.toggle('open'); }};
  document.getElementById('chat-close').onclick = function() {{ panel.classList.remove('open'); }};

  document.querySelectorAll('.chat-sugg').forEach(function(b) {{
    b.onclick = function() {{
      input.value = b.textContent.replace(/^[^\s]+\s/, '');
      send();
    }};
  }});

  input.addEventListener('keydown', function(e) {{
    if (e.key === 'Enter' && !e.shiftKey) {{ e.preventDefault(); send(); }}
  }});
  sendBtn.onclick = send;

  function getKey() {{ return localStorage.getItem(KEY_STORE); }}

  function addMsg(role, text, loading) {{
    var d = document.createElement('div');
    d.className = 'chat-msg ' + (role === 'user' ? 'user' : 'ai');
    var bubble = loading ? '<div class="chat-bubble loading">思考中…</div>' :
      '<div class="chat-bubble">' + text.replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>') + '</div>';
    d.innerHTML = '<div class="chat-avatar">' + (role==='user'?'👤':'🤖') + '</div>' + bubble;
    msgs.appendChild(d);
    msgs.scrollTop = msgs.scrollHeight;
    return d;
  }}

  function buildSystem() {{
    var r = window.__REPORT__;
    var inds = (r.industries||[]).map(function(i) {{
      var opps = (i.opportunities||[]).map(function(o) {{
        return o.title + '（' + o.description + '，紧迫度:' + o.urgency + '，第一步:' + o.first_step + '）';
      }}).join('；');
      return i.name + '——趋势:' + i.trend + '；机会:' + opps;
    }}).join('\\n');
    return '你是创业顾问AI，基于' + r.date + '的市场分析报告回答用户问题。\\n\\n报告摘要：' + r.summary + '\\n\\n各行业详情：\\n' + inds + '\\n\\n请用中文回答，结合报告数据，给出具体可行的建议。';
  }}

  function send() {{
    var text = input.value.trim();
    if (!text) return;
    var key = getKey();
    if (!key) {{ promptKey(); return; }}
    input.value = '';
    sendBtn.disabled = true;
    addMsg('user', text);
    history.push({{'role':'user','content':text}});
    var placeholder = addMsg('ai', '', true);
    var messages = [{{'role':'system','content':buildSystem()}}].concat(history);
    fetch('https://api.deepseek.com/v1/chat/completions', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json','Authorization':'Bearer '+key}},
      body: JSON.stringify({{model:'deepseek-chat',messages:messages,stream:true,max_tokens:1000}})
    }}).then(function(resp) {{
      if(!resp.ok) throw new Error('API错误 '+resp.status);
      var bubble = placeholder.querySelector('.chat-bubble');
      bubble.className = 'chat-bubble';
      bubble.textContent = '';
      var full = '';
      var reader = resp.body.getReader();
      var dec = new TextDecoder();
      function read() {{
        return reader.read().then(function(r) {{
          if(r.done) {{ history.push({{'role':'assistant','content':full}}); sendBtn.disabled=false; return; }}
          dec.decode(r.value).split('\\n').forEach(function(line) {{
            line = line.replace(/^data: /,'').trim();
            if(!line||line==='[DONE]') return;
            try {{
              var d = JSON.parse(line).choices[0].delta.content;
              if(d) {{ full+=d; bubble.textContent=full; msgs.scrollTop=msgs.scrollHeight; }}
            }} catch(e) {{}}
          }});
          return read();
        }});
      }}
      return read();
    }}).catch(function(e) {{
      placeholder.querySelector('.chat-bubble').textContent = '出错了：'+e.message+'，请检查 API Key 是否正确。';
      sendBtn.disabled = false;
    }});
  }}

  function promptKey() {{
    var old = localStorage.getItem(KEY_STORE) || '';
    var k = window.prompt('请输入 DeepSeek API Key（只需输入一次，存在本地）:', old);
    if(k && k.trim()) {{ localStorage.setItem(KEY_STORE, k.trim()); send(); }}
  }}

  // Pre-fill key if provided
  if(!getKey()) {{
    // User can click chat and will be prompted
  }}
}})();

if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.register('/rd-thoughts/sw.js');
}}
if(typeof Chart !== 'undefined') {{
  document.querySelectorAll('[data-values]').forEach(function(c) {{
    var vals = JSON.parse(c.dataset.values);
    var color = (c.closest('.industry-card') || {{}}).style && c.closest('.industry-card').style.borderLeftColor || '#6366f1';
    new Chart(c, {{
      type: 'line',
      data: {{
        labels: vals.map(function(_,i){{ return i; }}),
        datasets: [{{ data: vals, borderColor: color, borderWidth: 1.5,
          fill: true, backgroundColor: 'rgba(99,102,241,0.07)',
          pointRadius: 0, tension: 0.4 }}]
      }},
      options: {{
        responsive: false, animation: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }},
        scales: {{ x: {{ display: false }}, y: {{ display: false, min: 0 }} }}
      }}
    }});
  }});
}}
</script>
</body>
</html>"""


# ─────────────────────────── Archive ───────────────────────────

def load_archive(docs_dir):
    archive_file = os.path.join(docs_dir, 'archive.json')
    if os.path.exists(archive_file):
        with open(archive_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_archive(docs_dir, archive):
    archive_file = os.path.join(docs_dir, 'archive.json')
    with open(archive_file, 'w', encoding='utf-8') as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)


def update_archive(docs_dir, date_str, url, label):
    archive = load_archive(docs_dir)
    # Remove duplicate
    archive = [a for a in archive if a['url'] != url]
    archive.append({'date': date_str, 'url': url, 'label': label})
    archive.sort(key=lambda x: x['date'])
    save_archive(docs_dir, archive)
    return archive


def generate_archive_html(archive, docs_dir):
    items_by_month = {}
    for entry in archive[::-1]:
        month = entry['date'][:7]
        items_by_month.setdefault(month, []).append(entry)

    months_html = []
    for month, entries in sorted(items_by_month.items(), reverse=True):
        items_html = "\n".join(
            f'<li><a href="{e["url"]}">{e["label"]}</a></li>'
            for e in entries
        )
        months_html.append(f"""
        <div style="margin-bottom:24px">
          <h3 style="font-size:0.9rem;color:#475569;margin-bottom:10px;border-bottom:1px solid #e2e8f0;padding-bottom:6px">{month}</h3>
          <ul style="list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px">
            {items_html}
          </ul>
        </div>""")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>归档 — 创业情报雷达</title>
  <style>{CSS}</style>
</head>
<body>
<header class="header">
  <div class="header-left">
    <div class="header-logo">🧠 创业情报<span>雷达</span></div>
    <span class="header-date">历史归档</span>
  </div>
  <nav class="header-nav">
    <a href="index.html">最新</a>
    <a href="archive.html" class="active">归档</a>
  </nav>
</header>
<div style="max-width:900px;margin:0 auto;padding:32px 20px">
  <h2 style="font-size:1.2rem;margin-bottom:24px">📁 所有历史报告</h2>
  {''.join(months_html)}
</div>
<footer class="footer">
  由 Claude AI 自动生成 · <a href="https://github.com/yijiewu51/rd-thoughts">GitHub</a>
</footer>
</body>
</html>"""

    with open(os.path.join(docs_dir, 'archive.html'), 'w', encoding='utf-8') as f:
        f.write(html)


# ─────────────────────────── Main entry ───────────────────────────

def generate_reports(china_news, global_news, analysis, date_str, mode='daily',
                     market_data=None, funding_news=None):
    """生成 Markdown + HTML，保存到 reports/ 和 docs/"""
    root = Path(__file__).parent.parent
    reports_dir = root / 'reports'
    docs_dir = root / 'docs'
    data_dir = root / 'data'

    reports_dir.mkdir(exist_ok=True)
    docs_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    prefix = {'daily': '', 'weekly': 'weekly-', 'monthly': 'monthly-'}[mode]
    filename = f"{prefix}{date_str}"

    # Save raw data JSON
    raw = {
        'date': date_str,
        'mode': mode,
        'china_news': china_news,
        'global_news': global_news,
        'analysis': analysis,
    }
    with open(data_dir / f"{filename}.json", 'w', encoding='utf-8') as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)
    print(f"  💾 数据已保存: data/{filename}.json")

    # Load archive for sidebar links
    archive = load_archive(str(docs_dir))
    report_url = f"{filename}.html"
    mode_label = {"daily": "日报", "weekly": "周报", "monthly": "月报"}[mode]
    label = f"{date_str} {mode_label}"
    archive = update_archive(str(docs_dir), date_str, report_url, label)

    # Compute sparkline trend data from historical files
    trend_data = compute_industry_trend_data(data_dir)

    # Generate Markdown
    md_content = generate_markdown(china_news, global_news, analysis, date_str)
    md_path = reports_dir / f"{filename}.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  📝 Markdown: reports/{filename}.md")

    # Generate HTML (individual report)
    html_content = generate_html(
        china_news, global_news, analysis, date_str, mode, archive,
        market_data=market_data, funding_news=funding_news, trend_data=trend_data
    )
    html_path = docs_dir / f"{filename}.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"  🌐 HTML: docs/{filename}.html")

    # Update index.html (always = latest daily report)
    if mode == 'daily':
        index_path = docs_dir / 'index.html'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  🏠 index.html 已更新")

    # Update archive.html
    generate_archive_html(archive, str(docs_dir))
    print(f"  📁 archive.html 已更新")

    print(f"\n✅ 报告生成完毕！")
    return str(html_path)


# ─────────────────────────── Synthesis (周报/月报) HTML ───────────────────────────

def generate_synthesis_html(synthesis, date_str, mode, archive=None):
    """生成周报/月报综合分析 HTML"""
    period = "本周" if mode == 'weekly' else "本月"
    mode_label = "周报" if mode == 'weekly' else "月报"

    # Strong signals
    signals_html = ""
    for sig in synthesis.get('strong_signals', []):
        days = sig.get('appeared_days', 0)
        bar_width = min(100, days * 14)
        signals_html += f"""
        <div class="signal-card">
          <div class="signal-header">
            <span class="signal-name">{sig.get('signal', '')}</span>
            <span class="signal-days">出现 {days} 天</span>
          </div>
          <div class="signal-bar"><div class="signal-fill" style="width:{bar_width}%"></div></div>
          <div class="signal-insight">{sig.get('insight', '')}</div>
          <div class="signal-industries">{' · '.join(sig.get('industries', []))}</div>
        </div>"""

    # Top 5
    top5_html = ""
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    for pick in synthesis.get('top5', []):
        rank = pick.get('rank', 1) - 1
        medal = medals[rank] if rank < len(medals) else "•"
        color = get_industry_color(pick.get('industry', ''))
        diff_tag = difficulty_tag_html(pick.get('difficulty', '-'), "难度 ")
        urg_tag = difficulty_tag_html(pick.get('urgency', '-'), "紧迫 ")
        top5_html += f"""
        <div class="opp-card" style="border-left:4px solid {color}">
          <div class="opp-header">
            <div>
              <div style="font-size:1.3rem;margin-bottom:4px">{medal}</div>
              <div class="opp-title">{pick.get('title', '')}</div>
              <div style="font-size:0.75rem;color:#94a3b8;margin-top:2px">{pick.get('industry', '')}</div>
            </div>
            <div class="opp-tags">{diff_tag}{urg_tag}</div>
          </div>
          <div style="background:#fffbeb;border-radius:7px;padding:8px 12px;margin-bottom:10px;font-size:0.82rem;color:#92400e;border-left:3px solid #f59e0b">
            ⏰ {pick.get('why_this_week', '')}
          </div>
          <p class="opp-desc">{pick.get('description', '')}</p>
          <div class="opp-details">
            <div class="detail-item"><div class="detail-label">商业模式</div><div class="detail-value">{pick.get('business_model', '-')}</div></div>
            <div class="detail-item"><div class="detail-label">AI 赋能</div><div class="detail-value">{pick.get('ai_angle', '-')}</div></div>
            <div class="detail-item action" style="grid-column:span 2"><div class="detail-label">🚀 第一步</div><div class="detail-value">{pick.get('first_step', '-')}</div></div>
          </div>
        </div>"""

    # Industry insights (one-liners)
    ind_insights_html = ""
    for ind in synthesis.get('industry_insights', []):
        color = get_industry_color(ind.get('name', ''))
        ind_insights_html += f"""
        <div style="padding:10px 14px;border-radius:8px;border-left:3px solid {color};background:white;margin-bottom:8px">
          <span style="font-size:0.85rem;font-weight:600;color:#1e293b">{ind.get('emoji','')} {ind.get('name','')}</span>
          <span style="font-size:0.82rem;color:#475569;margin-left:10px">{ind.get('one_line','')}</span>
        </div>"""

    # AI deep dive
    ai_dive = synthesis.get('ai_deep_dive', {})
    ai_dive_html = f"""
    <div class="card" style="border-left:4px solid #6366f1">
      <div class="section-title">🔬 AI 赛道深度分析</div>
      <div style="display:grid;gap:12px;margin-top:8px">
        <div style="background:#f0f4ff;border-radius:8px;padding:14px">
          <div style="font-size:0.8rem;font-weight:700;color:#4f46e5;margin-bottom:6px">🤖 AI / 科技</div>
          <p style="font-size:0.875rem;color:#334155">{ai_dive.get('ai_tech','')}</p>
        </div>
        <div style="background:#f0f9ff;border-radius:8px;padding:14px">
          <div style="font-size:0.8rem;font-weight:700;color:#0369a1;margin-bottom:6px">💻 芯片 / 半导体</div>
          <p style="font-size:0.875rem;color:#334155">{ai_dive.get('chip','')}</p>
        </div>
        <div style="background:#faf5ff;border-radius:8px;padding:14px">
          <div style="font-size:0.8rem;font-weight:700;color:#7c3aed;margin-bottom:6px">🦾 机器人 / 具身智能</div>
          <p style="font-size:0.875rem;color:#334155">{ai_dive.get('robot','')}</p>
        </div>
      </div>
    </div>"""

    # Next period watch
    next_html = ""
    for w in synthesis.get('next_period_watch', []):
        next_html += f"""
        <div style="display:flex;gap:12px;padding:12px;background:white;border-radius:8px;margin-bottom:8px">
          <div style="font-size:1.2rem;color:#94a3b8;font-weight:800;min-width:28px">{w.get('rank','')}</div>
          <div>
            <div style="font-size:0.9rem;font-weight:700;color:#1e293b;margin-bottom:3px">{w.get('topic','')}</div>
            <div style="font-size:0.82rem;color:#64748b">{w.get('reason','')}</div>
          </div>
        </div>"""

    archive_links = ""
    if archive:
        items = " · ".join(f'<a href="{a["url"]}" style="color:#6366f1">{a["label"]}</a>'
                           for a in archive[-10:][::-1])
        archive_links = f'<div style="font-size:0.8rem;color:#94a3b8;margin-top:8px">{items}</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>创业情报{mode_label} — {date_str}</title>
  <style>
{CSS}
.signal-card {{background:white;border-radius:10px;padding:16px;margin-bottom:12px;box-shadow:0 1px 4px rgba(0,0,0,0.07)}}
.signal-header {{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}}
.signal-name {{font-size:0.9rem;font-weight:700;color:#1e293b}}
.signal-days {{font-size:0.75rem;background:#dbeafe;color:#1e40af;padding:2px 10px;border-radius:20px;font-weight:600}}
.signal-bar {{height:6px;background:#f1f5f9;border-radius:3px;margin-bottom:8px}}
.signal-fill {{height:100%;background:linear-gradient(90deg,#6366f1,#8b5cf6);border-radius:3px}}
.signal-insight {{font-size:0.84rem;color:#475569;margin-bottom:6px}}
.signal-industries {{font-size:0.75rem;color:#94a3b8}}
  </style>
</head>
<body>
<header class="header">
  <div class="header-left">
    <div class="header-logo">🧠 创业情报<span>雷达</span></div>
    <span class="header-date">{date_str} · {mode_label}</span>
  </div>
  <nav class="header-nav">
    <a href="index.html">最新日报</a>
    <a href="archive.html">归档</a>
  </nav>
</header>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-box">
      <h3>本页导航</h3>
      <a href="#summary">📊 总结</a>
      <a href="#signals">📡 强信号</a>
      <a href="#top5">🏆 TOP 5 机会</a>
      <a href="#ai-dive">🔬 AI 深度</a>
      <a href="#industry">💡 行业洞见</a>
      <a href="#next">🔭 下期预判</a>
    </div>
  </aside>

  <main class="main">

    <section id="summary">
      <div class="card summary-card">
        <div class="section-title">📊 {period}趋势总结</div>
        <p class="summary-text">{synthesis.get('period_summary', '')}</p>
      </div>
    </section>

    <section id="signals">
      <div class="section-title" style="margin-bottom:14px">📡 {period}强信号（反复出现的主题）</div>
      {signals_html}
    </section>

    <section id="top5">
      <div class="section-title" style="margin-bottom:14px">🏆 {period}最值得关注的 TOP 5 创业机会</div>
      {top5_html}
    </section>

    <section id="ai-dive">
      {ai_dive_html}
    </section>

    <section id="industry">
      <div class="card">
        <div class="section-title">💡 各行业本{period[1]}核心洞见</div>
        <div style="margin-top:12px">
          {ind_insights_html}
        </div>
      </div>
    </section>

    <section id="next">
      <div class="card">
        <div class="section-title">🔭 下{period[1]}重点关注方向</div>
        <div style="margin-top:12px">
          {next_html}
        </div>
      </div>
    </section>

    {archive_links}

  </main>
</div>

<footer class="footer">
  由 Claude AI 自动生成 · {date_str} · {mode_label} ·
  <a href="https://github.com/yijiewu51/rd-thoughts" target="_blank">GitHub</a>
</footer>
</body>
</html>"""


def generate_synthesis_markdown(synthesis, date_str, mode):
    period = "本周" if mode == 'weekly' else "本月"
    mode_label = "周报" if mode == 'weekly' else "月报"
    lines = [f"# 🧠 创业情报{mode_label} — {date_str}\n"]
    lines.append(f"> 基于过去{'7天' if mode=='weekly' else '30天'}日报综合分析\n")

    lines.append(f"## 📊 {period}趋势总结\n{synthesis.get('period_summary','')}\n")

    lines.append("## 📡 强信号\n")
    for sig in synthesis.get('strong_signals', []):
        lines.append(f"**{sig.get('signal','')}** — 出现 {sig.get('appeared_days',0)} 天")
        lines.append(f"{sig.get('insight','')}\n")

    lines.append("## 🏆 TOP 5 创业机会\n")
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣"]
    for pick in synthesis.get('top5', []):
        r = pick.get('rank',1)-1
        lines.append(f"### {medals[r] if r<5 else ''} {pick.get('title','')} `{pick.get('industry','')}`\n")
        lines.append(f"> ⏰ {pick.get('why_this_week','')}\n")
        lines.append(f"{pick.get('description','')}\n")
        lines.append(f"| 商业模式 | {pick.get('business_model','-')} |")
        lines.append(f"| AI赋能 | {pick.get('ai_angle','-')} |")
        lines.append(f"| 第一步 | {pick.get('first_step','-')} |\n")

    dive = synthesis.get('ai_deep_dive', {})
    lines.append("## 🔬 AI 赛道深度分析\n")
    lines.append(f"**🤖 AI / 科技：** {dive.get('ai_tech','')}\n")
    lines.append(f"**💻 芯片 / 半导体：** {dive.get('chip','')}\n")
    lines.append(f"**🦾 机器人 / 具身智能：** {dive.get('robot','')}\n")

    lines.append("## 💡 各行业核心洞见\n")
    for ind in synthesis.get('industry_insights', []):
        lines.append(f"- **{ind.get('emoji','')} {ind.get('name','')}**：{ind.get('one_line','')}")
    lines.append("")

    lines.append(f"## 🔭 下{period[1]}关注方向\n")
    for w in synthesis.get('next_period_watch', []):
        lines.append(f"{w.get('rank','')}. **{w.get('topic','')}** — {w.get('reason','')}")

    lines.append(f"\n---\n*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)


def generate_synthesis_reports(synthesis, date_str, mode):
    """生成周报/月报的 MD + HTML"""
    root = Path(__file__).parent.parent
    docs_dir = root / 'docs'
    reports_dir = root / 'reports'
    data_dir = root / 'data'

    docs_dir.mkdir(exist_ok=True)
    reports_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    prefix = 'weekly-' if mode == 'weekly' else 'monthly-'
    filename = f"{prefix}{date_str}"
    mode_label = "周报" if mode == 'weekly' else "月报"

    # Save data
    with open(data_dir / f"{filename}.json", 'w', encoding='utf-8') as f:
        json.dump({'date': date_str, 'mode': mode, 'synthesis': synthesis}, f,
                  ensure_ascii=False, indent=2)

    # Archive
    archive = load_archive(str(docs_dir))
    archive = update_archive(str(docs_dir), date_str, f"{filename}.html", f"{date_str} {mode_label}")

    # Markdown
    md = generate_synthesis_markdown(synthesis, date_str, mode)
    with open(reports_dir / f"{filename}.md", 'w', encoding='utf-8') as f:
        f.write(md)
    print(f"  📝 Markdown: reports/{filename}.md")

    # HTML
    html = generate_synthesis_html(synthesis, date_str, mode, archive)
    with open(docs_dir / f"{filename}.html", 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  🌐 HTML: docs/{filename}.html")

    generate_archive_html(archive, str(docs_dir))
    print(f"  📁 archive.html 已更新")
    print(f"\n✅ {mode_label}生成完毕！")
    return str(docs_dir / f"{filename}.html")
