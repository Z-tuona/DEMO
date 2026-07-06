# 🎙️ 直播带货话术、弹幕互动与销售复盘 Agent

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Streamlit-1.41-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/SQLite-async-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/LLM-Claude%20%7C%20GPT--4o-7B61FF" alt="LLM">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
</p>

面向直播电商的**多 Agent 协作运营系统**，覆盖商品管理、AI 话术生成、弹幕智能问答、工具调用、合规审核和直播复盘全流程。

> 💡 无需 LLM API Key 也能运行 — 内置模板模式，完整展示工具调用与 Agent 协作链路。

---

## 📖 目录

- [✨ 核心功能](#-核心功能)
- [🏗️ 系统架构](#-系统架构)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置说明](#-配置说明)
- [📁 项目结构](#-项目结构)
- [🤖 Agent 详解](#-agent-详解)
- [🔧 工具函数](#-工具函数)
- [📡 API 文档](#-api-文档)
- [🖥️ 前端页面](#-前端页面)
- [🧪 测试](#-测试)
- [📊 数据说明](#-数据说明)
- [🛠️ 技术栈](#-技术栈)

---

## ✨ 核心功能

| 模块 | 功能 | 技术亮点 |
|------|------|----------|
| 📦 **商品管理** | 12 个种子商品（6 大品类），支持 CRUD | FastAPI REST API + SQLite ORM |
| 🎙️ **AI 话术生成** | 5 种直播话术，适配不同人设与受众 | LLM Function Calling + 模板降级 |
| 💬 **弹幕智能问答** | 意图识别 → 情感分析 → 工具调用 → 异议处理 | 4 工具并行调用 + 关键词规则引擎 |
| 🛡️ **合规审核** | 广告法检查、绝对化用语过滤、医疗用语拦截 | 关键词规则 + LLM 深度审核双重保障 |
| 📊 **复盘报告** | 高频问题 TOP10、情感分布、转化阻碍、排品建议 | 自动数据分析 + 优化建议生成 |
| 🤖 **多 Agent 协作** | 主播 / 客服 / 场控 / 合规 4 个 Agent 通过编排器协作 | Orchestrator 模式 + 状态管理 |
| 🔄 **实时通信** | WebSocket 双向实时弹幕交互 | FastAPI WebSocket + Streamlit 实时渲染 |

---

## 🏗️ 系统架构

```
┌────────────────────────────────────────────────────────────┐
│                       Streamlit 前端                        │
│  首页概览 │ 商品管理 │ 直播模拟 │ 弹幕测试 │ 复盘报告        │
└──────────────────────┬─────────────────────────────────────┘
                       │ REST API + WebSocket
┌──────────────────────▼─────────────────────────────────────┐
│                   FastAPI 后端 (端口 8000)                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LiveStreamOrchestrator                   │   │
│  │              (多 Agent 编排器)                        │   │
│  │                                                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐ │   │
│  │  │ Host     │  │ Service  │  │ Control  │  │Compl-│ │   │
│  │  │ Agent    │  │ Agent    │  │ Agent    │  │iance │ │   │
│  │  │ 主播-话术 │  │ 客服-问答 │  │ 场控-节奏 │  │合规-审核│ │   │
│  │  └──────────┘  └────┬─────┘  └──────────┘  └──┬───┘ │   │
│  │                      │                         │      │   │
│  │         ┌────────────┼─────────────────────────┘      │   │
│  │         ▼            ▼            ▼            ▼       │   │
│  │    ┌──────────────────────────────────────────────┐   │   │
│  │    │            Function Calling Tools             │   │   │
│  │    │  💰优惠计算 │ 📦库存查询 │ 🎯商品推荐 │ 😊情感分析 │   │   │
│  │    └──────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  SQLite 数据库    │  │  LLM API 适配层   │                │
│  │  5 张业务表       │  │  Anthropic/OpenAI │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### 弹幕处理全链路

```
用户弹幕："这个精华液敏感肌能用吗？"
    │
    ▼
[情感分析]  sentiment: "questioning", intent: "audience"
    │
    ▼
[意图路由]  → Service Agent (客服)
    │
    ▼
[工具调用]  recommend_products(tags=["敏感肌"])
    │          → 返回匹配商品列表
    ▼
[生成回复]  "亲～这款精华液专为敏感肌研发，含神经酰胺修复成分
             温和无刺激，很多敏感肌宝宝都在用哦～"
    │
    ▼
[合规审核]  Compliance Agent → 通过 ✓
    │
    ▼
[输出]  WebSocket 广播 + 数据库记录
```

---

## 🚀 快速开始

### 环境要求

- **Python** ≥ 3.11
- **pip** 最新版

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/Z-tuona/live-stream-agent.git
cd live-stream-agent

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

### 启动

**方式一：一键启动 (Windows)**

双击 `start.bat`，自动启动前后端。

**方式二：手动启动**

```bash
# 终端 1 — 启动后端 API 服务 (端口 8000)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 终端 2 — 启动 Streamlit 前端 (端口 8501)
streamlit run frontend/app.py
```

浏览器打开 **http://localhost:8501**

> 💡 首次启动会自动初始化 12 个种子商品到 SQLite 数据库。

---

## ⚙️ 配置说明

在项目根目录创建 `.env` 文件（可选，不配置则使用模板模式）：

```env
# ========== LLM 提供商 ==========
# 选项: anthropic | openai
LLM_PROVIDER=anthropic

# ========== Anthropic Claude ==========
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_MODEL=claude-sonnet-4-20250514

# ========== OpenAI / 兼容 API ==========
# LLM_PROVIDER=openai
# OPENAI_API_KEY=sk-xxx
# OPENAI_MODEL=gpt-4o
# OPENAI_BASE_URL=https://api.openai.com/v1       # 可替换为其他兼容端点

# ========== LLM 参数 ==========
LLM_TEMPERATURE=0.7      # 0-1，主播话术建议 0.7-0.8，客服建议 0.3-0.5
LLM_MAX_TOKENS=2048

# ========== 数据库 ==========
DATABASE_URL=sqlite+aiosqlite:///live_stream.db
```

### 模板模式 vs LLM 模式

| 模式 | 话术生成 | 弹幕回复 | 合规审核 | 工具调用 |
|------|----------|----------|----------|----------|
| **模板模式** (无 API Key) | 预设话术模板 | 关键词匹配回复 | 规则引擎 | ✅ 正常调用 |
| **LLM 模式** (有 API Key) | AI 实时生成 | AI 智能回复 | 规则 + LLM 双重 | ✅ 正常调用 |

---

## 📁 项目结构

```
live-stream-agent/
│
├── backend/                          # 后端服务
│   ├── main.py                       # FastAPI 入口 — REST + WebSocket
│   ├── config.py                     # 配置管理 (LLM/数据库/合规规则)
│   ├── database.py                   # SQLite 异步引擎初始化
│   ├── models.py                     # ORM 模型 (5 张表)
│   ├── schemas.py                    # Pydantic 请求/响应模型
│   │
│   ├── agents/                       # 🤖 Agent 核心
│   │   ├── base.py                   # Agent 基类 (LLM + Function Calling)
│   │   ├── host_agent.py             # 主播 Agent — 话术生成
│   │   ├── service_agent.py          # 客服 Agent — 弹幕问答 + 异议处理
│   │   ├── control_agent.py          # 场控 Agent — 节奏管理
│   │   ├── compliance_agent.py       # 合规 Agent — 内容审核
│   │   └── orchestrator.py           # 多 Agent 编排器
│   │
│   ├── tools/                        # 🔧 工具函数
│   │   ├── discount.py               # 优惠计算 (满减/打折/买赠/优惠券)
│   │   ├── inventory.py              # 库存查询
│   │   ├── recommend.py              # 商品推荐 (品类/预算/标签)
│   │   └── sentiment.py              # 情感分析 (关键词规则引擎)
│   │
│   ├── services/                     # 🏗️ 业务服务层
│   │   ├── product_service.py        # 商品 CRUD + 种子数据
│   │   ├── session_service.py        # 场次管理 + 弹幕日志 + 工具调用日志
│   │   └── report_service.py         # 复盘报告生成
│   │
│   └── data/                         # 📦 种子数据
│       ├── seed_products.py          # 12 个商品 (6 大品类)
│       └── seed_danmaku.py           # 50+ 条弹幕 (6 类场景)
│
├── frontend/                         # 前端界面
│   ├── app.py                        # Streamlit 主入口 + 路由
│   ├── pages/
│   │   ├── products_page.py          # 商品管理页
│   │   ├── live_simulation_page.py   # 直播模拟页 (核心交互)
│   │   ├── danmaku_test_page.py      # 弹幕批量测试页
│   │   └── reports_page.py           # 复盘报告页
│   └── components/                   # UI 组件
│
├── tests/                            # 测试
│   ├── test_tools.py                 # 工具函数单元测试 (21 项)
│   ├── test_agents.py                # Agent 集成测试
│   └── test_integration.py           # 端到端测试
│
├── requirements.txt                  # Python 依赖
├── start.bat                         # Windows 一键启动脚本
├── .env.example                      # 环境变量模板
└── README.md
```

---

## 🤖 Agent 详解

### Host Agent — 主播"小优"

- **职责:** 5 种阶段话术生成（开场暖场 / 产品介绍 / 促销互动 / 答疑解惑 / 收尾预告）
- **特点:** 热情真诚、善于互动、口语化表达
- **temperature:** 0.8（较高，追求创意）

### Service Agent — 客服专家

- **职责:** 弹幕问答、优惠计算、商品推荐、异议处理
- **工具:** 4 个 Function Calling 工具，自动判断何时调用
- **异议策略库:** 4 类异议（价格/信任/质量/体验）× 4 种策略
- **temperature:** 0.5（较低，追求准确）

### Control Agent — 场控

- **职责:** 直播节奏管理、库存预警、阶段切换决策
- **决策引擎:** 规则优先（毫秒级）→ LLM 补充分析
- **节奏规则:** 暖场 5-8 分钟 / 产品 10-15 分钟 / 每 15 分钟促销插播

### Compliance Agent — 合规审查

- **职责:** 广告法审查、绝对化用语拦截、医疗功效检测
- **双重审核:** 关键词规则（快速）+ LLM 深度审核（精准）
- **违规词库:** 30+ 绝对化用语 + 10+ 医疗宣称词 + 8+ 价格风险词

---

## 🔧 工具函数

| 工具 | 函数签名 | 功能 |
|------|----------|------|
| `calculate_discount` | `(product_id, quantity, coupon_code?) → 优惠明细` | 满减/打折/买N送M/优惠券 自动叠加计算 |
| `check_inventory` | `(product_id) → 库存状态` | 充足(≥200) / 紧张(50-200) / 即将售罄(<50) / 售罄 |
| `recommend_products` | `(budget, category, tags, limit) → 推荐列表` | 按预算/品类/标签(敏感肌/学生党/送礼…)匹配，输出匹配度评分 |
| `analyze_sentiment` | `(message) → 情感分析` | 6 种情感 + 5 种意图 + 4 类异议检测，毫秒级关键词规则引擎 |

---

## 📡 API 文档

启动后端后，访问 **http://localhost:8000/docs** 查看 Swagger UI。

### 主要端点

```
GET    /api/health                         # 健康检查
GET    /api/products                       # 商品列表 (?category=护肤品)
GET    /api/products/{id}                  # 商品详情
POST   /api/products                       # 创建商品
POST   /api/sessions                       # 创建直播场次
GET    /api/sessions                       # 场次列表 (?status=live)
POST   /api/sessions/{id}/start            # 开始直播
POST   /api/sessions/{id}/end              # 结束直播
POST   /api/sessions/{id}/script           # 生成话术 {stage, product_id, style}
POST   /api/sessions/{id}/danmaku          # 发送弹幕 {user_name, message, product_id}
GET    /api/sessions/{id}/danmaku          # 弹幕历史 (?limit=100)
GET    /api/sessions/{id}/report           # 查看复盘报告
POST   /api/sessions/{id}/report/generate  # 生成复盘报告
WS     /ws/{session_id}                    # WebSocket 实时通信
```

### WebSocket 消息协议

| 类型 | 方向 | 说明 |
|------|------|------|
| `danmaku_submit` | 客户端 → 服务端 | 发送弹幕 |
| `danmaku_ack` | 服务端 → 客户端 | 弹幕已接收 |
| `agent_thinking` | 服务端 → 广播 | Agent 处理状态 |
| `tool_call` | 服务端 → 广播 | 工具调用详情 |
| `agent_response` | 服务端 → 广播 | Agent 最终回复 |
| `script_request` | 客户端 → 服务端 | 请求生成话术 |
| `script_ready` | 服务端 → 广播 | 话术生成完毕 |
| `control` | 客户端 → 服务端 | 场控操作指令 |

---

## 🖥️ 前端页面

### 🏠 首页概览
系统功能一览、Agent 架构图、快速开始指南

### 💰 商品管理
- 商品卡片 3 列展示，库存状态颜色标识
- 品类筛选下拉框
- 添加商品表单（卖点/价格/优惠规则/库存等）

### 🎙️ 直播模拟（核心页面）
三栏布局实时互动：

| 左栏 | 中栏 | 右栏 |
|------|------|------|
| 商品选择 + 详情 | 弹幕输入 + 发送 | 场控面板 |
| 话术生成 + 预览 | 弹幕滚动区 | 工具调用日志 |
| 合规审核提醒 | Agent 回复区 | 快捷操作按钮 |

### 💬 弹幕测试
- 50+ 预设弹幕逐条 / 批量发送
- 按类型筛选（价格/规格/售后/人群/优惠/异常）
- 自动统计：回复率 / 异议数 / 工具调用数

### 📊 复盘报告
- 情感分布柱状图
- 高频问题 TOP10 进度条
- 转化阻碍分析（展开详情）
- 优化建议 + 下场排品策略

---

## 🧪 测试

```bash
# 工具函数单元测试 (21 项)
python tests/test_tools.py

# Agent 集成测试 (模板模式)
python tests/test_agents.py

# 端到端测试
python tests/test_integration.py
```

### 测试覆盖

| 测试模块 | 测试项数 | 覆盖内容 |
|----------|----------|----------|
| 折扣计算 | 7 | 基础折扣、满减、买赠、VIP 券、新人券、无效商品、起购限制 |
| 库存查询 | 3 | 充足库存、紧张库存、无效商品 |
| 商品推荐 | 4 | 标签推荐、品类筛选、预算筛选、学生党场景 |
| 情感分析 | 7 | 价格问题、规格咨询、人群咨询、投诉检测、信任异议、兴奋情绪、闲聊 |

---

## 📊 数据说明

### 商品数据（12 个，6 大品类）

| 品类 | 商品 | 价格区间 |
|------|------|----------|
| 🧴 护肤品 ×4 | 焕颜精华液、修复面膜、氨基酸洁面乳、防晒霜 | ¥69 - ¥199 |
| 📱 数码 ×2 | 蓝牙降噪耳机、便携充电宝 | ¥139 - ¥499 |
| 🍪 食品 ×2 | 益生菌固体饮料、坚果礼盒 | ¥128 - ¥179 |
| 👕 服装 ×2 | 速干运动T恤、舒适休闲鞋 | ¥89 - ¥299 |
| 👶 母婴 ×1 | 儿童早教机 | ¥359 |
| 🏠 家居 ×1 | 智能保温杯 | ¥149 |

### 弹幕数据（50+ 条，6 类场景）

| 类型 | 数量 | 示例 |
|------|------|------|
| 💰 价格 (price) | 8 | "太贵了吧""比某宝贵" |
| 📋 规格 (specs) | 10 | "什么成分""保质期" |
| 🛡️ 售后 (after_sales) | 8 | "能退吗""快递几天" |
| 👥 人群 (audience) | 10 | "孕妇能用吗""送女友" |
| 🎫 优惠 (discount) | 8 | "买两件怎么算" |
| ⚠️ 异常 (abnormal) | 11 | "假货""智商税" |

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| **Web 框架** | FastAPI (async) | 0.115 |
| **实时通信** | WebSocket | — |
| **前端** | Streamlit | 1.41 |
| **数据库** | SQLite + SQLAlchemy (async) | 2.0 |
| **LLM SDK** | Anthropic + OpenAI | 0.42 / 1.58 |
| **Agent 编排** | LangGraph + LangChain Core | 0.2 / 0.3 |
| **数据校验** | Pydantic | 2.10 |
| **测试** | pytest + pytest-asyncio | 8.3 |
| **Python** | ≥ 3.11 | — |

---

## 📝 License

MIT License — 自由使用、修改和分发。

---

<p align="center">
  <sub>Built with ❤️ for live-stream e-commerce operators</sub>
</p>
