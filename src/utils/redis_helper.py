import json
import redis
from typing import List, Dict, Optional
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

    async def save_chat_history(self, request_id: str, messages: List[Dict]) -> bool:
        """保存对话历史"""
        try:
            key = f"chat:history:{request_id}"
            self.redis.set(
                key,
                json.dumps(messages, ensure_ascii=False),
                ex=settings.CHAT_HISTORY_EXPIRE
            )
            return True
        except Exception:
            return False

    async def get_chat_history(self, request_id: str) -> Optional[List[Dict]]:
        """获取对话历史"""
        try:
            key = f"chat:history:{request_id}"
            data = self.redis.get(key)
            if data and isinstance(data, str):
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return None

redis_client = RedisClient() 