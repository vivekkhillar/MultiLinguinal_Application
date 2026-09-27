from core.config import config
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession



class DBConnectionManager:

    def __init__(self):
        self.config = config()
        self.db_url = self.config.db_url
        self.engine : Optional[AsyncEngine] = None
        self.session_maker: Optional[async_sessionmaker[AsyncSession]] = None

    async def connect(self):

        self.engine = create_async_engine(self.db_url, echo = False,pool_size = 10, max_overflow = 20)
        self.session_maker = async_sessionmaker(bind=engine, class_= AsyncSession, expire_on_commit=False)
        
    
    async def close(self):

        if self.engine:
            await self.engine.dispose()

    @asynccontextmanager
    async def get_session(self):
        
        if not self.session_maker:

            raise RuntimeError("Data base is not connected. call connect the data base using await_connect() first")

        async with self.session_maker as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    
