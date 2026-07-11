import json
import time


def parse_events(text: str) -> list[dict]:
    return [json.loads(line.removeprefix("data: ")) for line in text.splitlines() if line.startswith("data: ")]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_dashboard_filters_and_two_second_snapshot(client):
    params = {"range": "7d", "region": "east", "category": "womens"}
    first = client.get("/api/dashboard", params=params)
    assert first.status_code == 200
    data = first.json()
    assert data["filters"] == params
    assert data["refresh_interval_ms"] == 2000
    assert data["sales_amount"]["unit"] == "CNY"
    second = client.get("/api/dashboard", params=params).json()
    assert second["snapshot_id"] == data["snapshot_id"]


def test_chat_sse_and_shared_snapshot(client):
    snapshot = client.get("/api/dashboard").json()
    response = client.post("/api/chat/stream", json={"requestId": "req-1", "message": "分析经营情况", "snapshot": snapshot})
    assert response.status_code == 200
    events = parse_events(response.text)
    assert events[0]["type"] == "start"
    assert events[0]["snapshotId"] == snapshot["snapshot_id"]
    assert events[-1]["type"] == "done"
    assert {item["metric"] for item in events[-1]["evidence"]} == {
        "销售额", "销量", "折扣率", "库存周转率", "人均产能", "准交率"
    }
    assert events[-1]["limitations"]
    assert any(event["type"] == "delta" for event in events)


def test_chat_uses_mock_ai_analysis(client):
    response = client.post("/api/chat/stream", json={"requestId": "mock-adapter", "message": "请分析经营情况"})
    events = parse_events(response.text)
    answer = "".join(event.get("content", "") for event in events)
    assert "经营分析" in answer
    assert "| 指标 | 当前值 | 变化 | 趋势 |" in answer
    assert "value=" not in answer
    assert any(item["source"] == "mock_business_snapshot" for item in events[-1]["evidence"])


def test_duplicate_request(client):
    payload = {"requestId": "same", "message": "分析"}
    assert parse_events(client.post("/api/chat/stream", json=payload).text)[-1]["type"] == "done"
    events = parse_events(client.post("/api/chat/stream", json=payload).text)
    assert events == [events[0]]
    assert events[0]["type"] == "duplicate"
    assert events[0]["status"] == "completed"


def test_timeout_with_retry(client):
    response = client.post("/api/chat/stream", json={"requestId": "slow", "message": "模拟超时", "timeoutMs": 50, "maxRetries": 1})
    events = parse_events(response.text)
    assert [event["type"] for event in events] == ["start", "retry", "timeout"]


def test_cancel_unknown(client):
    response = client.post("/api/chat/missing/cancel")
    assert response.json() == {"task_id": "missing", "status": "not_found"}


def test_validation(client):
    assert client.get("/api/dashboard", params={"range": "bad"}).status_code == 422
    assert client.post("/api/chat/stream", json={"requestId": "x", "message": ""}).status_code == 422
