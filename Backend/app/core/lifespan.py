from infrastructure.redis.connection import RedisConnectionManager
from infrastructure.database.connection import DBConnectionManager
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .logging_config import init_logging,_get_logger

logger = _get_logger()

class LifeSpan:

    def __init__(self):
        self.redis_manager = RedisConnectionManager()
        self.database_manager = DBConnectionManager()

    
    @asynccontextmanager
    async def lifespanhandler(self, app: FastAPI):
        init_logging()
        logger.info("Application startup initiated")
        try:
            await self.redis_manager.connect()
            logger.info("Redis connected successfully")
            await self.database_manager.connect()
            logger.info("Database connected successfully")
        
            yield

        except Exception:
            logger.exception("Failed during application startup sequence")
            raise

        finally:
            
            logger.info("Application shutdown initiated")
            
            try: 
                await self.redis_manager.close()
                logger.info("Redis Close")

            except Exception:
                logger.exception("Error While closing the Redis")
            
            try:
                await self.database_manager.close()
                logger.info("Database close")
            except Exception:

                logger.exception("Error While closing the Database")

lifespan_instance = LifeSpan()
lifespan= lifespan_instance.lifespanhandler