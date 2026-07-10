# AI Executive Cockpit

企业级 AI 智能经营驾驶舱 Demo，基于 Vue 3、TypeScript、ECharts 与 FastAPI 构建。

## 核心能力

- 销售、库存、生产与利润 KPI 总览
- 销售趋势、区域排行与库存结构可视化
- AI 经营预警与侧边栏流式问答
- 一键生成 Markdown 月度经营分析报告
- 深色响应式界面，支持桌面与移动设备

## 技术架构

```text
Vue 3 + TypeScript + ECharts
             ↓
       Fetch / SSE
             ↓
        FastAPI Service
             ↓
    Mock 企业经营数据
```

## 本地启动

### VS Code 一键启动（推荐）

用 VS Code 打开项目根目录后，选择菜单 **终端 → 运行任务 → 启动前后端**。前端和后端会分别在独立终端启动，无需手动切换目录。

启动后访问 `http://127.0.0.1:5173`。

### 手动启动

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

前端：

```bash
cd frontend
pnpm install
pnpm dev
```

打开 `http://localhost:5173`。后端健康检查位于 `http://localhost:8000/health`。

前端要求 Node.js 20.19+；如果终端提示 `node` 或 `pnpm` 不存在，请优先使用上面的 VS Code 一键启动任务。

## 验证

```bash
cd frontend && pnpm build
cd backend && pytest -q
```
