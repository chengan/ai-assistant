from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel

class ProviderResponse(BaseModel):
    """统一的提供商响应格式"""
    content: str
    raw_response: Dict[str, Any]

class StreamResponse(BaseModel):
    """流式响应格式"""
    content: str
    done: bool = False

class BaseProvider(ABC):
    """AI提供商基础接口类"""
    
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], model_id: str) -> ProviderResponse:
        """聊天接口"""
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """健康检查"""
        pass 

    @abstractmethod
    def get_model_params(self, model_id: str) -> Dict[str, Any]:
        """获取模型特定参数"""
        pass

    @abstractmethod
    async def stream_chat(
        self, 
        messages: List[Dict[str, str]], 
        model_id: str
    ) -> AsyncGenerator[StreamResponse, None]:
        """流式聊天接口"""
        pass