import main
from fastapi.testclient import TestClient


app = main.app


def test_health(monkeypatch):
    monkeypatch.setattr(main, "init_db", lambda: None)
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
