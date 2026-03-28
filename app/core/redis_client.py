import redis.asyncio as redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def initialize(self):
        self.client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def close(self):
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(key)
    
    async def setex(self, key: str, time: int, value: str) -> None:
        if self.client:
            await self.client.setex(key, time, value)
    
    async def delete(self, key: str) -> None:
        if self.client:
            await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        if not self.client:
            return False
        return await self.client.exists(key) > 0

redis_client = RedisClient()
