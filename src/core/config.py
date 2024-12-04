from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Assistant API"
    
    # 通义千问配置
    DASHSCOPE_API_KEY: Optional[str] = None
    TONGYI_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Redis配置
    REDIS_ENABLED: bool = False  # 设置为 False 可以禁用 Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CHAT_HISTORY_EXPIRE: int = 3600  # 对话历史过期时间（秒）
    
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

settings = Settings() 