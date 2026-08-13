import redis.asyncio as redis
import json
from typing import Any, Optional
from app.core.config import settings
from loguru import logger


class RedisManager:
    """Redis manager for caching and pub/sub operations."""
    
    def __init__(self):
        self.redis_client = None
        self.pubsub = None
        
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(
                settings.redis_url,
                decode_responses=True,
                health_check_interval=30
            )
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def set_cache(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in Redis cache."""
        try:
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            await self.redis_client.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def get_cache(self, key: str) -> Optional[Any]:
        """Get a value from Redis cache."""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def delete_cache(self, key: str) -> bool:
        """Delete a key from Redis cache."""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def publish(self, channel: str, message: Any) -> bool:
        """Publish a message to a Redis channel."""
        try:
            serialized_message = json.dumps(message) if not isinstance(message, str) else message
            await self.redis_client.publish(channel, serialized_message)
            return True
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            return False
    
    async def subscribe(self, channel: str):
        """Subscribe to a Redis channel."""
        try:
            if not self.pubsub:
                self.pubsub = self.redis_client.pubsub()
            
            await self.pubsub.subscribe(channel)
            return self.pubsub
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {e}")
            return None


# Global Redis manager instance
redis_manager = RedisManager()