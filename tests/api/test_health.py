"""API 健康检查端点测试。"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    @pytest.fixture
    def client(self, mocker):
        mocker.patch("agent.core.agent_service.AgentService")
        from api.main import app
        return TestClient(app)

    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "agent_ready" in data
        assert "vector_store_ready" in data
