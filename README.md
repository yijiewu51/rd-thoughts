# 🧠 创业情报雷达

每日自动爬取全网热点新闻，Claude AI 深度分析 12 大行业创业机会。

**🔗 在线查看：** https://yijiewu51.github.io/rd-thoughts/

## 功能

- 📡 **新闻源**：微博热搜、百度热搜、知乎热榜、36氪、Hacker News、Reddit
- 🤖 **AI 分析**：12 大行业全覆盖，每个行业 2 个具体创业方向
- 📊 **三种频率**：日报（每天）/ 周报（每周日）/ 月报（每月1号）
- 📝 **双格式**：Markdown（GitHub 查看）+ HTML（网页查看）

## 行业覆盖

🤖 AI/科技 · 🏥 医疗健康 · 💰 金融/金融科技 · 📚 教育/EdTech
🛍️ 消费/零售/电商 · ⚡ 能源/清洁能源 · 🚗 出行/交通 · 🌾 农业/食品
🏠 房产/建筑 · 🏭 制造业/工业 · 🎬 媒体/娱乐/内容 · 📋 政策/监管/社会

## 部署步骤

### 1. Fork / 创建仓库

在 GitHub 创建新仓库 `rd-thoughts`，将本项目代码推送上去。

### 2. 添加 API Key

进入仓库 **Settings → Secrets and variables → Actions → New repository secret**

- Name: `ANTHROPIC_API_KEY`
- Value: 你的 Anthropic API Key（`sk-ant-...`）

### 3. 开启 GitHub Pages

进入仓库 **Settings → Pages**

- Source: `Deploy from a branch`
- Branch: `main`，文件夹: `/docs`
- 点击 Save

几分钟后访问 `https://yijiewu51.github.io/rd-thoughts/`

### 4. 手动触发第一次运行

进入仓库 **Actions → 📊 每日情报报告 → Run workflow**

## 本地运行

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-xxx
python src/main.py --mode daily
```

## 文件结构

```
├── src/
│   ├── crawlers/
│   │   ├── china_news.py    # 微博、百度、知乎、36kr
│   │   └── global_news.py   # Hacker News、Reddit
│   ├── analyzer.py          # Claude API 分析
│   ├── generator.py         # 生成 Markdown + HTML
│   └── main.py              # 入口
├── docs/                    # GitHub Pages（自动生成）
├── reports/                 # Markdown 报告（自动生成）
├── data/                    # 原始数据 JSON（自动生成）
└── .github/workflows/       # 定时任务
```
