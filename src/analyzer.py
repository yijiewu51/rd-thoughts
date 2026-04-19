"""
Claude API 分析模块
输入：中国新闻 + 国际新闻
输出：按行业分类的创业机会分析 JSON
"""

import anthropic
import json
import os
from datetime import datetime

# 行业分类（全覆盖）
INDUSTRIES = [
    ("🤖", "AI / 科技"),
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
    ("📋", "政策 / 监管 / 社会"),
]

INDUSTRY_LIST_STR = "\n".join([f"  {e} {n}" for e, n in INDUSTRIES])


def build_news_text(china_news, global_news):
    china_lines = []
    for i, item in enumerate(china_news[:12], 1):
        line = f"  {i}. 【{item['source']}】{item['title']}"
        if item.get('summary'):
            line += f"\n     摘要: {item['summary'][:120]}"
        china_lines.append(line)

    global_lines = []
    for i, item in enumerate(global_news[:12], 1):
        line = f"  {i}. 【{item['source']}】{item['title']}"
        if item.get('summary'):
            line += f"\n     摘要: {item['summary'][:120]}"
        global_lines.append(line)

    return "\n".join(china_lines), "\n".join(global_lines)


def analyze_news(china_news, global_news, mode='daily'):
    """调用 Claude 进行深度分析，返回结构化 JSON"""

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("缺少环境变量 ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)
    today = datetime.now().strftime('%Y年%m月%d日')
    china_text, global_text = build_news_text(china_news, global_news)

    prompt = f"""你是一位顶级创业顾问、行业趋势分析师，深度关注 AI 赋能各行业的创业机会。

今天是 {today}，以下是今日全网热点新闻：

━━ 🇨🇳 中国热点新闻 ━━
{china_text}

━━ 🌍 国际热点新闻 ━━
{global_text}

请对以上新闻进行深度分析，覆盖以下全部 12 个行业：
{INDUSTRY_LIST_STR}

分析要求：
1. **每个行业必须输出**，即使当天无直接相关新闻，也要结合宏观趋势和新闻背景进行思考
2. 每个行业输出 2 个具体、可落地的创业方向（不是泛泛而谈）
3. 重点思考 AI 如何赋能该行业，具体到产品形态
4. 结合中国市场现状（政策、竞争格局、用户习惯）
5. 给出第一步行动：创业者明天就能开始做什么

请严格按照以下 JSON 格式返回，不要包含任何其他文字或代码块标记：

{{
  "date": "{datetime.now().strftime('%Y-%m-%d')}",
  "mode": "{mode}",
  "overall_summary": "今日整体趋势总结，3-5句话，点出最重要的宏观信号",
  "industries": [
    {{
      "emoji": "行业emoji",
      "name": "行业名称",
      "news_connection": "与今日新闻的关联点（1-2句，若无直接相关则写宏观背景）",
      "trend": "当前核心趋势（2-3句，具体有洞见）",
      "opportunities": [
        {{
          "title": "创业方向名称（简洁有力，不超过15字）",
          "description": "具体描述和商业逻辑（120-180字，要有深度）",
          "business_model": "商业模式（一句话，包含收费方式）",
          "ai_angle": "AI赋能的具体切入点（产品层面）",
          "target_customer": "目标客户（越具体越好）",
          "market_size": "市场规模估计（加上依据）",
          "difficulty": "低/中/高",
          "urgency": "低/中/高",
          "first_step": "第一步行动（具体可执行，比如：做10个用户访谈 / 搭建MVP demo / 找某类合作伙伴）"
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
      "reason": "为什么现在是最佳时机（50-80字，有说服力）"
    }},
    {{
      "rank": 2,
      "industry": "所属行业",
      "title": "创业方向名称",
      "reason": "为什么现在是最佳时机"
    }},
    {{
      "rank": 3,
      "industry": "所属行业",
      "title": "创业方向名称",
      "reason": "为什么现在是最佳时机"
    }}
  ]
}}"""

    print("🤖 Claude 正在深度分析中（预计 30-60 秒）...")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()

    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split('\n')
        response_text = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])

    try:
        data = json.loads(response_text)
        print(f"✅ 分析完成，覆盖 {len(data.get('industries', []))} 个行业")
        return data
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 解析失败，尝试提取...")
        # Try to find JSON in response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start >= 0 and end > start:
            try:
                data = json.loads(response_text[start:end])
                print(f"✅ 提取成功")
                return data
            except Exception:
                pass
        print(f"❌ 解析彻底失败: {e}")
        print("原始响应前500字符:", response_text[:500])
        return None
