"""
市场信号 — 行业 ETF 周涨跌幅
使用 yfinance 批量获取，失败时静默返回空字典
"""

from datetime import datetime

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

# 行业 → ETF 映射 (etf, is_proxy)
INDUSTRY_ETF_MAP = {
    "AI / 科技":           ("XLK",  False),
    "芯片 / 半导体":        ("SOXX", False),
    "机器人 / 具身智能":    ("ROBO", False),
    "医疗健康":             ("XLV",  False),
    "金融 / 金融科技":      ("XLF",  False),
    "教育 / EdTech":        ("XLK",  True),   # proxy: tech sector
    "消费 / 零售 / 电商":   ("XLY",  False),
    "能源 / 清洁能源":      ("ICLN", False),
    "出行 / 交通":          ("IYT",  False),
    "农业 / 食品":          ("MOO",  False),
    "房产 / 建筑":          ("IYR",  False),
    "制造业 / 工业":        ("XLI",  False),
    "媒体 / 娱乐 / 内容":  ("XLC",  False),
    "宠物 / 宠物经济":      ("XLY",  True),   # proxy: consumer disc
    "潮流 / 时尚 / 运动":  ("XLY",  True),   # proxy: consumer disc
    "动漫 / 二次元 / IP":  ("XLC",  True),   # proxy: comm services
    "加密货币 / Web3 / DeFi": ("BITO", False),
    "政策 / 监管 / 社会":  ("SPY",  True),   # proxy: broad market
}


def get_market_signals() -> dict:
    """
    Returns {industry_name: {"etf": str, "change_pct": float, "is_proxy": bool}}
    Returns {} on any failure.
    """
    if not HAS_YFINANCE:
        print("  市场数据跳过（yfinance 未安装）")
        return {}

    all_tickers = list(set(etf for etf, _ in INDUSTRY_ETF_MAP.values()))
    print(f"  获取市场数据（{len(all_tickers)} 个 ETF）...")

    try:
        raw = yf.download(
            tickers=" ".join(all_tickers),
            period="10d",
            auto_adjust=True,
            progress=False,
            threads=True,
        )
        if raw.empty:
            print("  市场数据为空")
            return {}
    except Exception as e:
        print(f"  市场数据获取失败: {e}")
        return {}

    # Compute change for each ticker
    ticker_changes = {}
    for ticker in all_tickers:
        try:
            if len(all_tickers) == 1:
                closes = raw["Close"]
            else:
                closes = raw["Close"][ticker]
            closes = closes.dropna()
            if len(closes) >= 2:
                pct = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0] * 100
                ticker_changes[ticker] = round(float(pct), 2)
        except Exception:
            pass

    result = {}
    for industry, (etf, is_proxy) in INDUSTRY_ETF_MAP.items():
        if etf in ticker_changes:
            result[industry] = {
                "etf": etf,
                "change_pct": ticker_changes[etf],
                "is_proxy": is_proxy,
            }

    print(f"  市场信号: {len(result)} 个行业数据")
    return result
