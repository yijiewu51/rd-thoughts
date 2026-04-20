"""
Claude API 分析模块
输入：中国新闻 + 国际新闻
输出：按行业分类的创业机会分析 JSON
"""

import anthropic
import json
import os
from datetime import datetime
from json_repair import repair_json

# 行业分类（全覆盖，17个行业）
INDUSTRIES = [
    ("🤖", "AI / 科技"),           # AI 赛道重点，3个机会
    ("💻", "芯片 / 半导体"),
    ("🦾", "机器人 / 具身智能"),
    ("🏥", "医疗健康"),
    ("💰", "金融 / 金融科技"),
    ("📚", "教育 / EdTech"),
    ("🛍️", "消费 / 零售 / 电商"),
    ("⚡", "能源 / 清洁能源"),
    ("🚗", "出行 / 交通"),
    ("🌾", "农业 / 食品"),
    ("🏠", "房产 / 建筑"),
    ("🏭", "制造业 / 工业"),
    ("🎬", "媒体 / 娱乐 / 内容"),
    ("🐾", "宠物 / 宠物经济"),
    ("👟", "潮流 / 时尚 / 运动"),
    ("🎌", "动漫 / 二次元 / IP"),
    ("₿", "加密货币 / Web3 / DeFi"),
    ("📋", "政策 / 监管 / 社会"),
]

AI_INDUSTRY = "AI / 科技"
INDUSTRY_LIST_STR = "\n".join([f"  {e} {n}" for e, n in INDUSTRIES])


def _parse_response(response_text):
    """三层解析：标准 → 提取 → json-repair"""
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

    for attempt, text in enumerate([response_text,
                                     response_text[response_text.find('{'):response_text.rfind('}')+1]]):
        if not text or not text.strip().startswith('{'):
            continue
        try:
            data = json.loads(text)
            print(f"✅ JSON 解析成功（第{attempt+1}次尝试）")
            return data
        except json.JSONDecodeError:
            pass

    chunk = response_text[response_text.find('{'):response_text.rfind('}')+1]
    if chunk:
        try:
            repaired = repair_json(chunk, return_objects=True)
            if isinstance(repaired, dict) and repaired.get('industries'):
                print("✅ JSON 修复成功")
                return repaired
        except Exception as e:
            print(f"⚠️ JSON 修复失败: {e}")

    print("❌ 所有解析方式均失败")
    print("原始响应前300字符:", response_text[:300])
    return None


def _build_industry_prompt(china_text, global_text, today, mode, industries_spec, include_summary=True):
    """Build a prompt for a subset of industries."""
    industries_str = "\n".join(
        f"  {e} {n} — {opps}个方向，description控制在{words}字以内"
        for e, n, opps, words in industries_spec
    )
    summary_field = f'"overall_summary": "今日整体趋势总结（3-4句，重点突出AI相关）",' if include_summary else '"overall_summary": "",'
    top3_block = """
  "top3": [
    {"rank": 1, "industry": "所属行业", "title": "创业方向名称", "reason": "最佳时机理由（50字以内）"},
    {"rank": 2, "industry": "所属行业", "title": "创业方向名称", "reason": "理由"},
    {"rank": 3, "industry": "所属行业", "title": "创业方向名称", "reason": "理由"}
  ]""" if include_summary else '  "top3": []'

    return f"""你是顶级创业顾问，深度关注 AI 赋能各行业的创业机会。

今天是 {today}，以下是今日热点新闻：

━━ 🇨🇳 中国热点新闻 ━━
{china_text}

━━ 🌍 国际热点新闻 ━━
{global_text}

请分析以下行业，严格按要求输出：
{industries_str}

要求：
1. 每个行业必须输出，无直接新闻也要结合宏观趋势
2. 严格控制字数，不要超出限制
3. 结合AI赋能思考，给出具体产品形态和第一步行动
4. 结合中国市场现状

⚠️ 返回纯JSON，不含代码块，字符串内不用英文双引号（改用「」或【】）

{{
  {summary_field}
  "industries": [
    {{
      "emoji": "emoji",
      "name": "行业名称",
      "news_connection": "与新闻关联（1句）",
      "trend": "核心趋势（1-2句）",
      "opportunities": [
        {{
          "title": "方向名称（≤15字）",
          "description": "商业逻辑（严格按字数限制）",
          "business_model": "商业模式（1句）",
          "ai_angle": "AI切入点（1句）",
          "target_customer": "目标客户",
          "market_size": "市场规模",
          "difficulty": "低/中/高",
          "urgency": "低/中/高",
          "first_step": "第一步（1句可执行）"
        }}
      ],
      "watch_out": "风险（1句）"
    }}
  ],
{top3_block}
}}"""


def analyze_news(china_news, global_news, mode='daily'):
    """调用 Claude 进行深度分析（两次调用合并，确保18个行业全覆盖）"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("缺少环境变量 ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime('%Y年%m月%d日')

    china_lines = [f"  {i}. 【{item['source']}】{item['title']}" +
                   (f" — {item['summary'][:80]}" if item.get('summary') else "")
                   for i, item in enumerate(china_news[:12], 1)]
    global_lines = [f"  {i}. 【{item['source']}】{item['title']}"
                    for i, item in enumerate(global_news[:12], 1)]
    china_text = "\n".join(china_lines)
    global_text = "\n".join(global_lines)

    # Call 1: High-priority industries (3 opps each)
    BATCH1 = [
        ("🤖", "AI / 科技",           3, 80),
        ("🐾", "宠物 / 宠物经济",     3, 70),
        ("📚", "教育 / EdTech",        3, 70),
        ("🛍️", "消费 / 零售 / 电商",   3, 70),
        ("₿",  "加密货币 / Web3 / DeFi", 3, 70),
    ]
    # Call 2: Medium + low priority industries (2 and 1 opp respectively)
    BATCH2 = [
        ("💻", "芯片 / 半导体",        2, 60),
        ("🦾", "机器人 / 具身智能",    2, 60),
        ("💰", "金融 / 金融科技",      2, 50),
        ("🎬", "媒体 / 娱乐 / 内容",   2, 50),
        ("👟", "潮流 / 时尚 / 运动",   2, 50),
        ("🎌", "动漫 / 二次元 / IP",   2, 50),
        ("🚗", "出行 / 交通",          2, 50),
        ("⚡", "能源 / 清洁能源",      2, 50),
        ("🏥", "医疗健康",             1, 40),
        ("🌾", "农业 / 食品",          1, 40),
        ("🏭", "制造业 / 工业",        1, 40),
        ("🏠", "房产 / 建筑",          1, 40),
        ("📋", "政策 / 监管 / 社会",   1, 40),
    ]

    print("🤖 Claude 分析中 - 批次1（重点赛道5个）...")
    msg1 = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[{"role": "user", "content": _build_industry_prompt(
            china_text, global_text, today, mode, BATCH1, include_summary=True
        )}]
    )
    r1 = msg1.stop_reason
    print(f"  批次1: {r1}, {msg1.usage.output_tokens} tokens")
    result1 = _parse_response(msg1.content[0].text.strip())

    print("🤖 Claude 分析中 - 批次2（其余13个行业）...")
    msg2 = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=12000,
        messages=[{"role": "user", "content": _build_industry_prompt(
            china_text, global_text, today, mode, BATCH2, include_summary=False
        )}]
    )
    r2 = msg2.stop_reason
    print(f"  批次2: {r2}, {msg2.usage.output_tokens} tokens")
    result2 = _parse_response(msg2.content[0].text.strip())

    if not result1 or not result2:
        return result1 or result2

    # Merge: combine industries, use batch1's summary and top3
    merged = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'mode': mode,
        'overall_summary': result1.get('overall_summary', ''),
        'industries': result1.get('industries', []) + result2.get('industries', []),
        'top3': result1.get('top3', []),
    }
    print(f"✅ 合并完成：{len(merged['industries'])} 个行业")
    return merged


def analyze_synthesis(daily_data_list, mode='weekly'):
    """
    周报/月报综合分析
    输入：多天的 {date, overall_summary, industries, top3} 数据
    输出：跨期洞见 + 最强信号 + 精选机会
    """
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("缺少环境变量 ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    period = "本周" if mode == 'weekly' else "本月"
    n_days = len(daily_data_list)

    # Build digest of past analyses
    digests = []
    for d in daily_data_list:
        date = d.get('date', '')
        summary = d.get('analysis', {}).get('overall_summary', '')
        top3 = d.get('analysis', {}).get('top3', [])
        top3_str = " / ".join([f"【{t.get('title','')}】({t.get('industry','')})" for t in top3])
        digests.append(f"📅 {date}：{summary}\n   TOP3：{top3_str}")

        # Also include all opportunity titles per industry for frequency analysis
    all_opps = {}  # industry -> list of (date, title, description)
    for d in daily_data_list:
        for ind in d.get('analysis', {}).get('industries', []):
            name = ind.get('name', '')
            if name not in all_opps:
                all_opps[name] = []
            for opp in ind.get('opportunities', []):
                all_opps[name].append({
                    'date': d.get('date'),
                    'title': opp.get('title', ''),
                    'description': opp.get('description', '')[:100],
                    'urgency': opp.get('urgency', ''),
                    'difficulty': opp.get('difficulty', ''),
                })

    digest_text = "\n\n".join(digests)

    # Build per-industry opportunity summary
    industry_opp_text = []
    for ind_name, opps in all_opps.items():
        if not opps:
            continue
        opp_lines = [f"    - [{o['date']}] {o['title']}（紧迫:{o['urgency']} 难度:{o['difficulty']}）" for o in opps]
        industry_opp_text.append(f"  {ind_name}:\n" + "\n".join(opp_lines))
    industry_opp_text = "\n".join(industry_opp_text)

    today = datetime.now().strftime('%Y年%m月%d日')

    prompt = f"""你是顶级创业分析师，正在撰写{period}创业情报综合报告。

今天是 {today}，以下是过去 {n_days} 天的每日分析摘要：

━━ 每日摘要 ━━
{digest_text}

━━ 各行业出现的创业方向汇总 ━━
{industry_opp_text}

请基于以上 {n_days} 天的数据，生成{period}深度综合报告：

分析任务：
1. **信号强度分析**：哪些主题/机会在多天内反复出现？反复出现 = 强信号
2. **精选 TOP 5 机会**：从所有日报中找出本{period[1]}最值得关注的 5 个创业方向（跨行业）
3. **行业综合洞见**：每个行业本{period[1]}最重要的一条洞见（一句话）
4. **AI 赛道深度**：对 AI / 科技、芯片、机器人三个赛道做更深入的跨期分析
5. **下{period[1]}预判**：基于本{period[1]}信号，预测下{period[1]}最值得关注的 3 个方向

⚠️ 格式要求：返回纯 JSON，字符串内不能出现未转义英文双引号，用「」替代

{{
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "mode": "{mode}",
  "period_summary": "{period}整体总结（5-7句，点出最重要的宏观变化和信号）",
  "strong_signals": [
    {{
      "signal": "反复出现的信号主题",
      "appeared_days": 出现天数,
      "industries": ["相关行业"],
      "insight": "这个信号说明什么（2-3句深度分析）"
    }}
  ],
  "top5": [
    {{
      "rank": 1,
      "industry": "行业",
      "title": "创业方向",
      "why_this_week": "为什么本{period[1]}特别值得关注（基于信号频率和强度）",
      "description": "机会描述（150字）",
      "business_model": "商业模式",
      "ai_angle": "AI赋能点",
      "first_step": "第一步行动",
      "difficulty": "低/中/高",
      "urgency": "低/中/高"
    }}
  ],
  "industry_insights": [
    {{
      "emoji": "行业emoji",
      "name": "行业名称",
      "one_line": "本{period[1]}该行业最重要的一句话洞见"
    }}
  ],
  "ai_deep_dive": {{
    "ai_tech": "AI/科技赛道本{period[1]}最重要的跨期趋势（3-4句）",
    "chip": "芯片/半导体赛道本{period[1]}信号（2-3句）",
    "robot": "机器人/具身智能赛道本{period[1]}信号（2-3句）"
  }},
  "next_period_watch": [
    {{"rank": 1, "topic": "下{period[1]}关注方向", "reason": "理由（1-2句）"}},
    {{"rank": 2, "topic": "下{period[1]}关注方向", "reason": "理由"}},
    {{"rank": 3, "topic": "下{period[1]}关注方向", "reason": "理由"}}
  ]
}}"""

    print(f"🤖 Claude 正在生成{period}综合分析（预计 60-90 秒）...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=12000,
        messages=[{"role": "user", "content": prompt}]
    )

    return _parse_response(message.content[0].text.strip())
