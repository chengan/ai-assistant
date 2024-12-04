from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import BaseProvider, ProviderResponse, StreamResponse
from ..core.config import settings
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TongyiProvider(BaseProvider):
    """通义千问适配器"""
    
    def __init__(self):
        if not settings.DASHSCOPE_API_KEY:
            raise ValueError("DASHSCOPE_API_KEY is not set")
        self.base_url = settings.TONGYI_BASE_URL
        self.api_key = settings.DASHSCOPE_API_KEY
        
    def get_model_params(self, model_id: str) -> Dict[str, Any]:
        """获取模型特定参数"""
        return {
            "result_format": "message",
            "temperature": 0.7,
            "max_tokens": 1500
        }
    
    async def chat(self, messages: List[Dict[str, str]], model_id: str) -> ProviderResponse:
        """实现对话功能"""
        try:
            request_data = {
                "model": model_id,
                "input": {
                    "messages": messages
                },
                "parameters": self.get_model_params(model_id)
            }
            
            logger.debug(f"Request to Tongyi API: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()
                
                logger.debug(f"Response from Tongyi API: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if "output" not in result or "choices" not in result["output"]:
                    raise ValueError("Invalid response format")
                
                content = result["output"]["choices"][0]["message"]["content"]
                return ProviderResponse(content=content, raw_response=result)
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
    async def check_health(self) -> bool:
        """健康检查"""
        try:
            result = await self.chat([{
                "role": "user",
                "content": "你好"
            }], "qwen-plus")
            return bool(result.content)
        except Exception:
            return False 
    
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        model_id: str
    ) -> AsyncGenerator[StreamResponse, None]:
        """实现流式对话"""
        try:
            request_data = {
                "model": model_id,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    **self.get_model_params(model_id),
                    "incremental_output": True  # 启用增量输出
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/services/aigc/text-generation/generation",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                    },
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                data = json.loads(line)
                                if "output" in data:
                                    content = data["output"]["text"]
                                    yield StreamResponse(
                                        content=content,
                                        done="finish_reason" in data
                                    )
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            logger.error(f"Error in stream chat: {str(e)}")
            raise 