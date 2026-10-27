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
        try:
            await self.redis_manager.connect()
            # print("Redis start")
     
            await self.database_manager.connect()
            # print("Database start")
        
            yield

        finally:

            try: 
                await self.redis_manager.close()
                # print("Redis close")

            except Exception as e:
                print(f"Error While closing the Redis {e}")
            
            try:
                await self.database_manager.close()
                # print("Database close")
            except Exception as e:
                print(f"Error While closing the Database {e}")

lifespan_instance = LifeSpan()
lifespan= lifespan_instance.lifespanhandler