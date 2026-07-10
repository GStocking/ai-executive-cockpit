from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_and_dashboard():
    assert client.get("/health").json()["status"] == "ok"
    data = client.get("/api/dashboard").json()
    assert data["kpis"]["sales"]["value"] == 12860400

def test_report():
    response = client.post("/api/report")
    assert response.status_code == 200
    assert "经营分析报告" in response.json()["report"]

def test_chat_stream():
    response = client.get("/api/chat/stream", params={"message": "分析销售增长原因"})
    assert response.status_code == 200
    tokens = [line.removeprefix("data: ") for line in response.text.splitlines() if '"token"' in line]
    import json
    answer = "".join(json.loads(token)["token"] for token in tokens)
    assert "销售增长" in answer
