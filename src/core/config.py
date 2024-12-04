from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from enum import Enum
import os

class EnvironmentType(str, Enum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    VERCEL = "vercel"

class Settings(BaseSettings):
    # 环境配置
    ENVIRONMENT: EnvironmentType = Field(
        default=EnvironmentType.LOCAL,
        description="运行环境"
    )
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Assistant API"
    
    # 通义千问配置
    DASHSCOPE_API_KEY: Optional[str] = None
    TONGYI_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    TONGYI_COMPATIBLE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Redis配置
    REDIS_ENABLED: bool = Field(
        default=False,
        description="是否启用Redis"
    )
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CHAT_HISTORY_EXPIRE: int = 3600
    
    # 百川配置
    BAICHUAN_API_KEY: Optional[str] = None
    BAICHUAN_SECRET_KEY: Optional[str] = None
    BAICHUAN_BASE_URL: str = "https://api.baichuan-ai.com/v1"
    
    # 使用新的配置方式
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )

    def get_environment_settings(self) -> dict:
        """根据环境返回特定配置"""
        base_settings = {
            "REDIS_ENABLED": self.REDIS_ENABLED,
            "API_V1_STR": self.API_V1_STR,
        }
        
        env_settings = {
            EnvironmentType.LOCAL: {
                "REDIS_ENABLED": True,
                "REDIS_HOST": "localhost",
            },
            EnvironmentType.DEVELOPMENT: {
                "REDIS_ENABLED": True,
                "REDIS_HOST": "redis.dev.example.com",
            },
            EnvironmentType.PRODUCTION: {
                "REDIS_ENABLED": True,
                "REDIS_HOST": "redis.prod.example.com",
            },
            EnvironmentType.VERCEL: {
                "REDIS_ENABLED": False,  # Vercel 环境禁用 Redis
            }
        }
        
        # 更新基础配置
        base_settings.update(env_settings.get(self.ENVIRONMENT, {}))
        return base_settings

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 应用环境特定的配置
        env_settings = self.get_environment_settings()
        for key, value in env_settings.items():
            setattr(self, key, value)

settings = Settings() 