from core.config import config
from redis.asyncio import Redis

class RedisConnectionManager:
    
    def __init__(self) -> None:
        self.conf=config()
        self.redis_host=self.conf.redis_host
        self.redis_port=self.conf.redis_port
        self.redis_timeout=self.conf.redis_timeout
        self.redis_password=self.conf.redis_password
        self._client: Redis | None = None
        
    
    # Try to connect redis database 
    async def connect(self) -> None:
        
        try:
            self._client = Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            socket_connect_timeout=self.redis_timeout,
            decode_responses=True
        )        
            await self._client.ping()

        except Exception as e:
            raise RuntimeError ("Redis connection is failed ") from e


    # Get the client details for which the redis connected
    def get_client(self) -> Redis:
        if self._client is None:
            raise RuntimeError ("Redis client is not connected")
        return self._client

    # Close the connection
    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None