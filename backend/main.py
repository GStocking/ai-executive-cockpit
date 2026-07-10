import asyncio
import json
from datetime import datetime

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="AI Executive Cockpit API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

KPI_DATA = {
    "sales": {"value": 12860400, "growth": 12.8, "unit": "CNY"},
    "inventory": {"value": 4230800, "change": -3.2, "healthy_rate": 68},
    "production": {"completion_rate": 94.6, "target": 93.0},
    "profit": {"margin": 18.7, "growth": 1.9},
}

ANSWERS = {
    "销售": "销售增长主要由三个因素驱动：华东区重点客户复购贡献约 41%，A 类产品均价提升带来约 3.2 个百分点增长，线上渠道新增订单同比增长 24%。建议下月继续聚焦高复购客户，同时关注华南回款周期延长的问题。",
    "风险": "当前识别到 3 项经营风险：华东区 A 类产品库存低于安全线；二号产线良品率较昨日下降 1.8%；华南区域回款周期延长 2.3 天。建议优先补充华东库存并排查二号产线参数。",
    "建议": "下月建议：一是将华东 A 类产品安全库存提高 15%；二是针对高复购客户启动分层运营；三是对二号产线执行 48 小时质量专项；四是强化华南应收账款跟进。预计可支撑销售环比增长 6%—8%。",
}

class ReportResponse(BaseModel):
    report: str
    generated_at: str

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-executive-cockpit"}

@app.get("/api/dashboard")
async def dashboard():
    return {"period": "2026-07", "updated_at": datetime.now().isoformat(), "kpis": KPI_DATA}

@app.get("/api/chat/stream")
async def chat_stream(message: str = Query(min_length=1, max_length=500)):
    answer = next((value for key, value in ANSWERS.items() if key in message), "从当前经营数据看，整体态势稳中向好：销售额环比增长 12.8%，生产完成率达到 94.6%，综合利润率连续三个月增长。建议重点跟进库存预警和华南区域回款周期。")
    async def stream():
        for token in answer:
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.012)
        yield f"data: {json.dumps({'done': True})}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.post("/api/report", response_model=ReportResponse)
async def generate_report():
    await asyncio.sleep(0.8)
    report = """# 2026 年 7 月经营分析报告

## 一、经营概览

本月经营态势整体 **稳中向好**。累计销售额达到 **1,286.04 万元**，环比增长 **12.8%**；生产完成率 **94.6%**，超过目标 1.6 个百分点；综合利润率提升至 **18.7%**。

| 核心指标 | 本月表现 | 趋势 |
|---|---:|---|
| 销售额 | 1,286.04 万元 | ↑ 12.8% |
| 库存总值 | 423.08 万元 | ↓ 3.2% |
| 生产完成率 | 94.6% | ↑ 2.4% |
| 综合利润率 | 18.7% | ↑ 1.9% |

## 二、关键洞察

1. **增长质量改善**：销售增长与利润率提升同步，说明本月增长不依赖低价促销。
2. **库存效率提升**：库存总值下降 3.2%，但华东区 A 类产品已低于安全线，需要定向补货。
3. **生产总体稳定**：整体履约超过目标，二号产线良品率短期波动需持续监测。

## 三、下月行动建议

- 将华东 A 类产品安全库存提高 15%，建立每日补货提醒。
- 对高复购客户开展分层运营，巩固重点客户贡献。
- 对二号产线执行 48 小时质量专项，定位参数偏差。
- 强化华南区域应收账款跟进，缩短回款周期。

> AI 结论：在控制库存和产线风险的前提下，下月销售额有望保持 6%—8% 的环比增长。"""
    return ReportResponse(report=report, generated_at=datetime.now().isoformat())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
