import json
import redis
from typing import List, Dict, Optional
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    _instance = None
    _redis = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            try:
                if settings.REDIS_ENABLED:
                    cls._redis = redis.Redis(
                        host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB,
                        password=settings.REDIS_PASSWORD,
                        decode_responses=True
                    )
                    cls._redis.ping()
                else:
                    logger.info("Redis is disabled by configuration")
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}")
                cls._redis = None
        return cls._instance

    @property
    def redis(self) -> Optional[redis.Redis]:
        """获取 Redis 连接"""
        return self._redis

    async def save_chat_history(self, request_id: str, messages: List[Dict]) -> bool:
        """保存对话历史"""
        if not settings.REDIS_ENABLED:
            logger.debug("Redis is disabled, skipping save_chat_history")
            return False
            
        if not self.redis:
            logger.warning("Redis not available, skipping save_chat_history")
            return False
            
        try:
            key = f"chat:history:{request_id}"
            self.redis.set(
                key,
                json.dumps(messages, ensure_ascii=False),
                ex=settings.CHAT_HISTORY_EXPIRE
            )
            return True
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}")
            return False

    async def get_chat_history(self, request_id: str) -> Optional[List[Dict]]:
        """获取对话历史"""
        if not settings.REDIS_ENABLED:
            logger.debug("Redis is disabled, skipping get_chat_history")
            return None
            
        if not self.redis:
            logger.warning("Redis not available, skipping get_chat_history")
            return None
            
        try:
            key = f"chat:history:{request_id}"
            data = self.redis.get(key)
            if data and isinstance(data, str):
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return None

# 创建全局 Redis 客户端实例
redis_client = RedisClient() 