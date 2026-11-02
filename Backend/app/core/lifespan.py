from contextlib import asynccontextmanager
from fastapi import FastAPI
from infrastructure.redis.connection import RedisConnectionManager
from infrastructure.database.connection import DBConnectionManager
from .logging_config import init_logging, _get_logger


class LifeSpan:

    def __init__(self):
        self.redis_manager = RedisConnectionManager()
        self.database_manager = DBConnectionManager()

    @asynccontextmanager
    async def lifespanhandler(self, app: FastAPI):
        # 1. Initialize logging infrastructure first
        init_logging()
        # 2. Acquire fully configured logger instance
        logger = _get_logger()

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
                logger.info("Redis connection closed")
            except Exception:
                logger.exception("Error while closing Redis")

            try:
                await self.database_manager.close()
                logger.info("Database connection closed")
            except Exception:
                logger.exception("Error while closing Database")

            logger.info("Application shutdown complete")


lifespan_instance = LifeSpan()
lifespan = lifespan_instance.lifespanhandler