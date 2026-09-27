from core.config import config
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession



class DBConnectionManager:

    def __init__(self):
        self.config = config()
        self.db_url = self.config.db_url
    

    async def connect(self):

        engine = create_async_engine(self.db_url, echo = False)
        AsyncSession = async_sessionmaker(bind=engine, class_= AsyncSession, expire_on_commit=False)
        