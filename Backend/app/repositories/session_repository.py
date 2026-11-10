from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

class SessionRepository:

    def __init__(self,session= AsyncSession) -> None:

        self.session = session
    

    async def get_by_token_hash(self,hashtoken : str) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM
                        chat_app.user_sessions where token_hash = :hashtoken 
                    """)
        res = await self.session.execute(query,{"hashtoken": hashtoken})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    
    
