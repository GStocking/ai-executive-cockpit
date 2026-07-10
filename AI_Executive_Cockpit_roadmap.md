# AI Executive Cockpit

> 企业级 AI 智能经营驾驶舱

## Project Overview

AI Executive Cockpit 是一个面向企业经营分析场景的 AI 应用 Demo。

基于 Vue3 + TypeScript + ECharts 构建企业级数据驾驶舱，
结合 LLM 能力实现 AI 智能问答、流式响应以及经营分析报告生成。

项目目标：

1. 展示企业数据可视化能力
2. 展示 AI 应用前端交互能力
3. 展示 SSE 流式通信能力
4. 展示企业级前后端工程设计能力

---

# 一、系统边界

## 本项目包含

### Frontend

- Dashboard 数据驾驶舱
- AI Chat 智能助手
- ECharts 数据可视化
- SSE 流式消息展示
- Markdown AI报告展示
- Vue3工程化结构

### Backend

- FastAPI服务
- AI Chat接口
- SSE Streaming接口
- Mock企业业务数据
- Prompt管理

## 不包含内容

- ❌ 用户登录
- ❌ 权限系统
- ❌ RBAC
- ❌ 数据库设计
- ❌ 微服务
- ❌ Docker部署
- ❌ Kubernetes
- ❌ 消息队列
- ❌ 多租户
- ❌ 复杂Agent框架
- ❌ 工作流引擎

目标：

> 展示 AI 企业应用前端交付能力，而不是构建完整商业系统。

---

# 二、最终能力展示

## 1. Executive Dashboard

展示：

- 销售额
- 库存
- 生产完成率
- 利润率

图表：

- 销售趋势
- 区域销售排行
- 库存状态
- 生产状态

技术：

- ECharts
- Vue组件封装
- 数据驱动渲染

---

## 2. AI Chat Assistant

支持：

- Chat UI
- 消息状态管理
- Loading
- Error处理
- Streaming Response

---

## 3. SSE Streaming

实现：

Backend Token Stream

↓

Frontend

↓

实时逐字展示

用于模拟 GPT 流式输出体验。

---

## 4. AI Report

支持：

输入：

生成7月经营分析报告

输出：

Markdown格式经营分析报告。

---

# 三、技术选型

## Frontend

- Vue3
- TypeScript
- Vite
- Pinia
- VueUse
- UnoCSS
- ECharts
- Axios
- markdown-it

要求：

- script setup
- Composition API
- VueUse hooks

---

## Backend

- FastAPI
- Python
- OpenAI API
- SSE

---

# 四、项目目录设计

```
ai-executive-cockpit

├── frontend
│
├── src
│   ├── api
│   ├── components
│   │   ├── charts
│   │   ├── dashboard
│   │   └── chat
│   ├── composables
│   ├── stores
│   ├── views
│   └── main.ts
│
├── backend
│
│   ├── api
│   ├── services
│   ├── schemas
│   └── main.py
│
├── README.md
└── docs
    └── roadmap.md
```

---

# 五、代码设计原则

## Vue3

必须：

```vue
<script setup lang="ts">

</script>
```

禁止：

- Options API
- mixin

---

## VueUse

使用：

- useFetch
- useAsyncState
- useDebounceFn
- useEventSource
- useResizeObserver

用途：

- API状态管理
- SSE监听
- 响应式处理

---

## 分层设计

```
View

↓

Business Component

↓

Composable

↓

API Layer

↓

Backend Service
```

---

# 六、7天开发计划

# Day1 项目初始化

完成：

Frontend:

- Vue3 + TS
- Vite
- UnoCSS
- Vue Router
- Pinia
- VueUse

Backend:

- FastAPI初始化
- CORS配置

验收：

- 前端正常启动
- 后端正常启动

---

# Day2 Dashboard基础

完成：

- 页面布局
- KPI Card
- Header
- Sidebar

组件：

- KpiCard
- DashboardLayout

---

# Day3 ECharts

完成：

组件：

- LineChart
- BarChart
- PieChart
- GaugeChart

要求：

- resize
- 生命周期管理
- 动态数据更新

使用：

useResizeObserver

---

# Day4 AI Chat

完成：

- Chat页面
- 消息列表
- 输入框
- Loading状态

组件：

- ChatMessage
- ChatInput
- TypingIndicator

---

# Day5 SSE Streaming

完成：

Backend:

/chat/stream

Frontend:

useEventSource

能力：

- token流式返回
- 错误处理
- 连接关闭

---

# Day6 AI Report

完成：

流程：

Dashboard Data

↓

Prompt Template

↓

LLM

↓

Markdown

Frontend：

markdown-it渲染。

---

# Day7 优化与发布

完成：

## UI

- 深色主题
- 动画
- 响应式

## README

包含：

- 项目介绍
- 架构图
- 技术栈
- 截图
- 启动方式

## Git提交

```
feat: initialize project

feat: build dashboard

feat: integrate echarts

feat: implement ai chat

feat: add sse streaming

feat: generate ai report

docs: update README
```

---

# 七、启动方式

## Frontend

```
cd frontend

pnpm install

pnpm dev
```

访问：

```
http://localhost:5173
```

---

## Backend

```
cd backend

pip install -r requirements.txt

python main.py
```

---

# 八、面试展示流程

3分钟：

1. Dashboard展示经营指标

2. AI Chat：

输入：

分析销售下降原因

展示：

SSE流式回答

3. AI生成经营报告

4. 介绍架构：

```
Vue3

↓

Composable

↓

API Layer

↓

FastAPI

↓

LLM
```

---

# 项目完成标准

[x] Vue3

[x] TypeScript

[x] setup语法

[x] VueUse

[x] UnoCSS

[x] ECharts

[x] Dashboard

[x] AI Chat

[x] SSE

[x] 前后端分离

[x] README

[x] 正常启动


READY FOR INTERVIEW
