from typing import Dict, Type
from .base import BaseProvider
from .tongyi import TongyiProvider
from .baichuan import BaichuanProvider

class ProviderFactory:
    """AI提供商工厂"""
    
    _providers: Dict[str, Type[BaseProvider]] = {
        "tongyi": TongyiProvider,
        "baichuan": BaichuanProvider,
        # 后续可以添加其他提供商
        # "openai": OpenAIProvider,
    }
    
    @classmethod
    def create(cls, provider_type: str) -> BaseProvider:
        """创建提供商实例"""
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return provider_class()

    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._providers.keys()) 