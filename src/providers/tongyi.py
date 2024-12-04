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
        self.api_key = settings.DASHSCOPE_API_KEY
        self.base_url = settings.TONGYI_BASE_URL
        self.compatible_url = f"{settings.TONGYI_COMPATIBLE_URL}/chat/completions"
    
    def get_model_params(self, model_id: str) -> Dict[str, Any]:
        """获取模型特定参数"""
        return {
            "result_format": "message",
            "temperature": 0.7,
            "max_tokens": 1500
        }
    
    async def chat(self, messages: List[Dict[str, str]], model_id: str) -> ProviderResponse:
        """实现对话功能（使用原始API）"""
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
        """实现流式对话（使用兼容模式API）"""
        try:
            request_data = {
                "model": model_id,
                "messages": messages,
                "stream": True,
                "stream_options": {
                    "include_usage": True
                }
            }
            
            logger.info(f"Stream request data: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST",
                    self.compatible_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_data
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                # 处理 SSE 格式数据
                                if line.startswith('data: '):
                                    line = line[6:]  # 移除 'data: ' 前缀
                                if line == '[DONE]':
                                    continue
                                    
                                data = json.loads(line)
                                logger.debug(f"Received stream data: {json.dumps(data, ensure_ascii=False)}")
                                
                                if "choices" in data and data["choices"]:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    done = data["choices"][0].get("finish_reason") is not None
                                    
                                    if content:  # 只在有内容时才yield
                                        yield StreamResponse(
                                            content=content,
                                            done=done
                                        )
                                    
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse stream data: {line}, error: {str(e)}")
                                continue
                                
        except Exception as e:
            logger.error(f"Error in stream chat: {str(e)}", exc_info=True)
            raise 