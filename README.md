# 银行活动聚合

自动聚合银行/平台优惠活动，支持 AI 解析和 Telegram 推送。

## 功能特性

- ✅ 手动提交活动内容，AI 自动提取结构化信息
- ✅ Telegram Bot 实时推送新活动
- ✅ SQLite 数据库存储，支持多终端同步
- ✅ 活动去重和过期归档
- ✅ CLI 工具，方便命令行操作

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd bank-promotion/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的配置：

```bash
cp .env.example .env
```

需要配置：
- `TELEGRAM_BOT_TOKEN`: Telegram Bot Token
- `TELEGRAM_CHAT_ID`: 你的 Telegram Chat ID
- `DEEPSEEK_API_KEY`: DeepSeek API Key

### 3. 获取 Telegram 配置

1. 在 Telegram 中搜索 `@BotFather`，发送 `/newbot` 创建 Bot
2. 获取 Bot Token
3. 向你的 Bot 发送任意消息
4. 访问 `https://api.telegram.org/bot<TOKEN>/getUpdates` 获取 Chat ID

### 4. 启动服务

```bash
# 启动 API 服务
uvicorn app.api:app --reload --host 0.0.0.0 --port 8000
```

## 使用方法

### 方法一：CLI 工具（推荐）

```bash
python cli.py
```

选择功能：
1. AI 解析并提交活动
2. 手动提交活动
3. 查看最新活动

### 方法二：API 接口

#### 解析活动内容

```bash
curl -X POST "http://localhost:8000/api/promotions/parse" \
  -H "Content-Type: application/json" \
  -d '{"content": "粘贴的活动内容"}'
```

#### 提交活动

```bash
curl -X POST "http://localhost:8000/api/promotions/submit" \
  -H "Content-Type: application/json" \
  -d '{"title": "活动标题", "bank": "中国农业银行", ...}'
```

#### 查看最新活动

```bash
curl "http://localhost:8000/api/promotions/latest?limit=10"
```

## 项目结构

```
bank-promotion/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api.py           # FastAPI 接口
│   │   ├── database.py      # 数据库模型
│   │   ├── crud.py          # 数据库操作
│   │   ├── ai_parser.py     # AI 解析模块
│   │   └── telegram_push.py # Telegram 推送
│   ├── cli.py               # CLI 工具
│   ├── requirements.txt     # 依赖列表
│   └── .env.example         # 环境变量示例
├── frontend/                # 前端（待开发）
└── README.md
```

## 开发计划

- [x] 模块1: 数据存储层
- [x] 模块2: AI 解析模块
- [x] 模块6: Telegram 推送
- [ ] 模块3: 赚客吧爬虫
- [ ] 模块4: 银行官方渠道爬虫
- [ ] 模块5: 定时任务
- [ ] 模块7: 前端展示

## 常见问题

### Q: 如何获取 Telegram Chat ID？

1. 向你的 Bot 发送任意消息
2. 访问 `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. 在返回的 JSON 中找到 `result[0].message.chat.id`

### Q: DeepSeek API 如何获取？

1. 访问 https://platform.deepseek.com/
2. 注册账号并登录
3. 在 API Keys 页面创建新的 Key

### Q: 如何部署到 GitHub Actions？

项目已配置 GitHub Actions 工作流，推送到 GitHub 后会自动执行定时任务。

## License

MIT
