from infrastructure.redis.connection import RedisConnectionManager
from infrastructure.database.connection import DBConnectionManager
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .logging_config import logger

class LifeSpan:

    def __init__(self):
        self.redis_manager = RedisConnectionManager()
        self.database_manager = DBConnectionManager()
    
    @asynccontextmanager
    async def lifespanhandler(self, app: FastAPI):
        try:
            await self.redis_manager.connect()
            logger.info("Redis Start")
            await self.database_manager.connect()
            logger.info("Database Start")
        
            yield

        finally:

            try: 
                await self.redis_manager.close()
                logger.info("Redis Close")

            except Exception as e:
                logger.info(f"Error While closing the Redis {e}")
            
            try:
                await self.database_manager.close()
                logger.info(f"Database close")
            except Exception as e:

                logger.info(f"Error While closing the Database {e}")

lifespan_instance = LifeSpan()
lifespan= lifespan_instance.lifespanhandler