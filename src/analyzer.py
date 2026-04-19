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


def analyze_news(china_news, global_news, mode='daily'):
    """调用 Claude 进行深度分析，返回结构化 JSON"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("缺少环境变量 ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime('%Y年%m月%d日')

    china_lines = [f"  {i}. 【{item['source']}】{item['title']}" +
                   (f"\n     摘要: {item['summary'][:120]}" if item.get('summary') else "")
                   for i, item in enumerate(china_news[:12], 1)]
    global_lines = [f"  {i}. 【{item['source']}】{item['title']}"
                    for i, item in enumerate(global_news[:12], 1)]

    china_text = "\n".join(china_lines)
    global_text = "\n".join(global_lines)

    prompt = f"""你是一位顶级创业顾问、行业趋势分析师，深度关注 AI 赋能各行业的创业机会。

今天是 {today}，以下是今日全网热点新闻：

━━ 🇨🇳 中国热点新闻 ━━
{china_text}

━━ 🌍 国际热点新闻 ━━
{global_text}

请对以上新闻进行深度分析，覆盖以下全部 17 个行业：
{INDUSTRY_LIST_STR}

分析要求：
1. **每个行业必须输出**，即使当天无直接相关新闻，也要结合宏观趋势进行思考
2. 【AI / 科技】是核心赛道，必须输出 **3 个创业方向**，分析要更深入（150-200字/方向）
3. 其余每个行业输出 **2 个创业方向**（120-150字/方向）
4. 重点思考 AI 如何赋能每个行业，具体到产品形态
5. 结合中国市场现状（政策、竞争格局、用户习惯）
6. 给出第一步行动：创业者明天就能开始做什么
7. 对于【芯片/半导体】【机器人/具身智能】这两个赛道，重点分析与 AI 的协同机会
8. 对于【宠物/宠物经济】【潮流/时尚/运动】【动漫/二次元/IP】这三个新兴消费赛道，重点分析 AI+内容/社区/个性化的切入点

⚠️ 格式要求（必须遵守）：
- 返回纯 JSON，不要包含任何其他文字，不要用 ```json 代码块
- JSON 字符串中绝对不能出现未转义的英文双引号，强调词语请用「」或【】，例如：「智能体」而非"智能体"

JSON 格式如下：

{{
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "mode": "{mode}",
  "overall_summary": "今日整体趋势总结，4-6句，点出最重要的宏观信号，重点突出 AI 相关",
  "industries": [
    {{
      "emoji": "行业emoji",
      "name": "行业名称",
      "news_connection": "与今日新闻的关联点（1-2句）",
      "trend": "当前核心趋势（2-3句，具体有洞见）",
      "opportunities": [
        {{
          "title": "创业方向名称（不超过15字）",
          "description": "具体描述和商业逻辑（AI赛道150-200字，其他行业120-150字）",
          "business_model": "商业模式（一句话，含收费方式）",
          "ai_angle": "AI赋能的具体切入点（产品层面，要具体）",
          "target_customer": "目标客户（越具体越好）",
          "market_size": "市场规模估计（含依据）",
          "difficulty": "低/中/高",
          "urgency": "低/中/高",
          "first_step": "第一步行动（具体可执行）"
        }}
      ],
      "watch_out": "风险或注意事项（1-2句）"
    }}
  ],
  "top3": [
    {{
      "rank": 1,
      "industry": "所属行业",
      "title": "创业方向名称",
      "reason": "为什么现在是最佳时机（60-100字，有说服力）"
    }},
    {{"rank": 2, "industry": "所属行业", "title": "创业方向名称", "reason": "理由"}},
    {{"rank": 3, "industry": "所属行业", "title": "创业方向名称", "reason": "理由"}}
  ]
}}"""

    print("🤖 Claude 正在深度分析中（17个行业，预计 60-90 秒）...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=20000,
        messages=[{"role": "user", "content": prompt}]
    )

    return _parse_response(message.content[0].text.strip())


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
