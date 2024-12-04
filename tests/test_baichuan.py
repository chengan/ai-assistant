import pytest
from unittest.mock import AsyncMock, patch
from src.providers.baichuan import BaichuanProvider

@pytest.fixture
def mock_baichuan_response():
    return {
        "data": {
            "messages": [{
                "role": "assistant",
                "content": "这是百川的测试回复"
            }]
        },
        "usage": {
            "total_tokens": 42,
            "prompt_tokens": 10,
            "completion_tokens": 32
        }
    }

@pytest.mark.asyncio
async def test_baichuan_chat():
    provider = BaichuanProvider()
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_baichuan_response
        mock_post.return_value.raise_for_status = AsyncMock()
        
        response = await provider.chat([{
            "role": "user",
            "content": "你好"
        }], "Baichuan2-53B")
        
        assert response.content == "这是百川的测试回复"
        assert response.raw_response == mock_baichuan_response 