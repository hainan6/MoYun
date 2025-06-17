"""
Cache Manager Module
Modern Redis cache management with improved error handling and type safety
"""
from typing import Union, List, Optional, Dict, Any
import redis

from core.config.settings import config_manager


class CacheError(Exception):
    """Custom exception for cache-related errors"""
    pass


class RedisCacheManager:
    """Modern Redis cache manager with improved error handling and type safety"""
    
    def __init__(self):
        """Initialize Redis connection with configuration"""
        try:
            redis_config = config_manager.get_redis_config()
            
            self._redis_client = redis.StrictRedis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['database'],
                password=redis_config.get('password'),
                decode_responses=False,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self._redis_client.ping()
            
        except Exception as e:
            raise CacheError(f"Failed to initialize Redis connection: {e}")
    
    def set_cache(self, key: str, value: str, expire_seconds: Optional[int] = None) -> bool:
        """Set cache value"""
        try:
            self._redis_client.set(key, value)
            if expire_seconds:
                self._redis_client.expire(key, expire_seconds)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    def get_cache(self, key: str) -> Optional[str]:
        """Get cache value"""
        try:
            result = self._redis_client.get(key)
            return result.decode('utf-8') if result else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache value"""
        try:
            self._redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        try:
            self._redis_client.ping()
            return True
        except:
            return False 