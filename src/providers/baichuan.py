from typing import List, Dict, Any
import httpx
import json
import time
import hmac
import hashlib
import base64
from .base import BaseProvider, ProviderResponse
from ..core.config import settings
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class BaichuanProvider(BaseProvider):
    """百川API适配器"""
    
    def __init__(self):
        if not settings.BAICHUAN_API_KEY or not settings.BAICHUAN_SECRET_KEY:
            raise ValueError("BAICHUAN_API_KEY or BAICHUAN_SECRET_KEY is not set")
        self.base_url = settings.BAICHUAN_BASE_URL
        self.api_key = settings.BAICHUAN_API_KEY
        self.secret_key = settings.BAICHUAN_SECRET_KEY

    def get_model_params(self, model_id: str) -> Dict[str, Any]:
        """获取模型特定参数"""
        return {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1500
        }
    
    def _generate_signature(self, timestamp: int) -> str:
        """生成签名"""
        payload = f"{self.api_key}:{timestamp}"
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    async def chat(self, messages: List[Dict[str, str]], model_id: str) -> ProviderResponse:
        """实现对话功能"""
        try:
            timestamp = int(time.time())
            signature = self._generate_signature(timestamp)
            
            request_data = {
                "model": model_id,
                "messages": messages,
                "parameters": self.get_model_params(model_id)
            }
            
            logger.debug(f"Request to Baichuan API: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "X-BC-Timestamp": str(timestamp),
                        "X-BC-Signature": signature,
                        "X-BC-Sign-Algo": "hmac_sha256",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()
                
                logger.debug(f"Response from Baichuan API: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if "data" not in result or "messages" not in result["data"]:
                    raise ValueError("Invalid response format")
                
                content = result["data"]["messages"][0]["content"]
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
            }], "Baichuan2-53B")
            return bool(result.content)
        except Exception:
            return False 