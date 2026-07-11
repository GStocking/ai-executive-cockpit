"""Deterministic mock AI analysis for the local executive-cockpit demo.

This module deliberately has no model, knowledge-base, network, or persistence
dependency.  Every conclusion is derived from the business snapshot supplied by
the caller for the current request.
"""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
from typing import Any, AsyncIterator, Literal, Mapping, Sequence


DemoMode = Literal["normal", "timeout", "error"]


class MockAIError(RuntimeError):
    """Raised by the explicit error demonstration mode."""


@dataclass(frozen=True)
class Evidence:
    metric: str
    source: str
    field: str
    value: Any


@dataclass(frozen=True)
class AnalysisResult:
    answer: str
    evidence: tuple[Evidence, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "evidence": [asdict(item) for item in self.evidence],
            "limitations": list(self.limitations),
        }


_METRICS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("销售额", ("sales_amount", "revenue", "销售额")),
    ("销量", ("sales_volume", "volume", "销量")),
    ("折扣率", ("discount_rate", "折扣率")),
    ("库存周转率", ("inventory_turnover", "库存周转率")),
    ("人均产能", ("productivity_per_capita", "人均产能")),
    ("准交率", ("on_time_delivery_rate", "准交率")),
)


def _snapshot_mapping(snapshot: Any) -> Mapping[str, Any]:
    if isinstance(snapshot, Mapping):
        return snapshot
    model_dump = getattr(snapshot, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump(mode="python")
        if isinstance(dumped, Mapping):
            return dumped
    raise TypeError("business_snapshot must be a mapping or a Pydantic model")


def _kpi_container(snapshot: Mapping[str, Any]) -> tuple[Mapping[str, Any], str]:
    candidate = snapshot.get("kpis")
    return (candidate, "kpis.") if isinstance(candidate, Mapping) else (snapshot, "")


def _find_metric(container: Mapping[str, Any], aliases: tuple[str, ...]) -> tuple[str, Any] | None:
    lowered = {str(key).lower(): key for key in container}
    for alias in aliases:
        original_key = lowered.get(alias.lower())
        if original_key is not None:
            return str(original_key), container[original_key]
    return None


def _format_number(value: Any) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return str(value)
    if float(value).is_integer():
        return f"{value:,.0f}"
    return f"{value:,.2f}".rstrip("0").rstrip(".")


def _metric_cells(value: Any) -> tuple[str, str, str]:
    if not isinstance(value, Mapping):
        return str(value), "—", "—"
    current = _format_number(value.get("value", "—"))
    unit = value.get("unit")
    if unit:
        current = f"{current} {unit}"
    change = value.get("change")
    change_text = f"{float(change):+.2f}%" if isinstance(change, (int, float)) else "—"
    trend_text = {"up": "上升", "down": "下降", "flat": "持平"}.get(str(value.get("trend", "")), "—")
    return current, change_text, trend_text


def analyze(
    query: str,
    business_snapshot: Any,
    session_context: Sequence[Mapping[str, Any]] | None = None,
) -> AnalysisResult:
    """Build a deterministic Chinese analysis from the supplied snapshot.

    ``session_context`` is accepted only as ephemeral request context.  The mock
    service never stores it and does not use it to manufacture business facts.
    """
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    snapshot = _snapshot_mapping(business_snapshot)
    container, field_prefix = _kpi_container(snapshot)
    evidence: list[Evidence] = []
    metric_rows = ["| 指标 | 当前值 | 变化 | 趋势 |", "|---|---:|---:|:---:|"]
    missing: list[str] = []

    for label, aliases in _METRICS:
        found = _find_metric(container, aliases)
        if found is None:
            missing.append(label)
            metric_rows.append(f"| {label} | 暂无数据 | — | — |")
            continue
        field, value = found
        current, change, trend = _metric_cells(value)
        metric_rows.append(f"| {label} | {current} | {change} | {trend} |")
        evidence.append(Evidence(label, "mock_business_snapshot", f"{field_prefix}{field}", value))

    filters = snapshot.get("filters")
    period = snapshot.get("period") or (filters.get("range") if isinstance(filters, Mapping) else None)
    title_period = f"（{period}）" if period else ""
    available = "、".join(item.metric for item in evidence) or "无"
    answer = (
        f"## 经营分析{title_period}\n\n"
        + "\n".join(metric_rows)
        + "\n\n### 综合判断\n"
        + (f"本次仅能基于已提供的{available}指标描述当前表现；未提供对比口径、目标或明细时，不推断变化原因。" if evidence else "当前没有可用于分析的经营指标，无法形成经营判断。")
        + "\n\n### 建议\n"
        + ("优先核实变化方向异常或偏离目标的指标，再结合当前筛选范围内的业务明细决定行动。" if evidence else "请补充销售额、销量、折扣率、库存周转率、人均产能和准交率的模拟快照。")
    )

    limitations = [
        "结论仅基于本次请求携带的本地模拟业务快照，未调用真实模型或知识库。",
        "临时 session context 不会被存储，也不会形成跨会话记忆。",
    ]
    if missing:
        limitations.append(f"快照缺少指标：{'、'.join(missing)}。")
    if session_context:
        limitations.append("session context 仅作为当前请求的临时上下文；经营事实仍以业务快照为准。")

    return AnalysisResult(answer, tuple(evidence), tuple(limitations))


async def analyze_stream(
    query: str,
    business_snapshot: Any,
    session_context: Sequence[Mapping[str, Any]] | None = None,
    *,
    chunk_size: int = 12,
    delay_seconds: float = 0.01,
    demo_mode: DemoMode = "normal",
    timeout_seconds: float = 1.0,
) -> AsyncIterator[dict[str, Any]]:
    """Yield transport-neutral chunk/final events suitable for an SSE adapter."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")
    if delay_seconds < 0 or timeout_seconds < 0:
        raise ValueError("delays must not be negative")
    if demo_mode == "error":
        raise MockAIError("模拟 AI 服务错误")
    if demo_mode == "timeout":
        await asyncio.sleep(timeout_seconds)
        raise TimeoutError("模拟 AI 服务超时")
    if demo_mode != "normal":
        raise ValueError(f"unsupported demo_mode: {demo_mode}")

    result = analyze(query, business_snapshot, session_context)
    for index in range(0, len(result.answer), chunk_size):
        yield {"event": "chunk", "content": result.answer[index : index + chunk_size]}
        if delay_seconds:
            await asyncio.sleep(delay_seconds)
    yield {
        "event": "final",
        "evidence": [asdict(item) for item in result.evidence],
        "limitations": list(result.limitations),
    }


__all__ = [
    "AnalysisResult",
    "DemoMode",
    "Evidence",
    "MockAIError",
    "analyze",
    "analyze_stream",
]
