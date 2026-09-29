from infrastructure.redis.connection import RedisConnectionManager
from infrastructure.database.connection import DBConnectionManager
from fastapi import FastAPI
from contextlib import asynccontextmanager

class LifeSpan:

    def __init__(self):
        self.redis_manager = RedisConnectionManager()
        self.database_manager = DBConnectionManager()
    
    @asynccontextmanager
    async def lifespanhandler(self, app: FastAPI):

        await self.redis_manager.connect()
        print("Redis start")
        await self.database_manager.connect()
        result = await self.database_manager.ping()
        print(f"Sql Query executed : {result}")
        print("Database start")


        yield

        await self.redis_manager.close()
        print("Redis close")
        await self.database_manager.close()
        print("Database close")

lifespan_instance = LifeSpan()
lifespan= lifespan_instance.lifespanhandler