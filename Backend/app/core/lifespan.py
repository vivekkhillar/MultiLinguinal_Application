from infrastructure.redis.connection import RedisConnectionManager
from fastapi import FastAPI
from contextlib import asynccontextmanager

class LifeSpan:

    def __init__(self):
        self.redis_manager = RedisConnectionManager()
    
    @asynccontextmanager
    async def lifespanhandler(self, app: FastAPI):

        print("Redis start")
        await self.redis_manager.connect()

        yield
        print("Redis close")
        await self.redis_manager.close()


lifespan_instance = LifeSpan()
lifespan= lifespan_instance.lifespanhandler