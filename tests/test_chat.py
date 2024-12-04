import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.providers.tongyi import TongyiProvider
from unittest.mock import AsyncMock, patch

client = TestClient(app)

@pytest.fixture
def mock_tongyi_response():
    return {
        "output": {
            "text": "这是一个测试回复"
        },
        "request_id": "test_request_id",
        "usage": {
            "total_tokens": 10
        }
    }

@pytest.mark.asyncio
async def test_chat_endpoint(mock_tongyi_response):
    with patch.object(
        TongyiProvider,
        'chat',
        new_callable=AsyncMock,
        return_value=mock_tongyi_response
    ) as mock_chat:
        response = client.post(
            "/api/v1/chat",
            json={
                "messages": [
                    {
                        "role": "user",
                        "content": "你好"
                    }
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "这是一个测试回复"
        assert data["request_id"] == "test_request_id"
        assert "usage" in data
        mock_chat.assert_called_once()

def test_list_models():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    assert data["models"][0]["id"] == "qwen-plus" 