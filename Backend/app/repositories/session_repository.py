from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:

    def __init__(self,session: AsyncSession) -> None:

        self.session = session
    

    async def get_by_token_hash(self,hashtoken : str) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM
                        chat_app.user_sessions where token_hash = :hashtoken 
                    """)
        res = await self.session.execute(query,{"hashtoken": hashtoken})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    
    async def get_by_id(self, sessionid: str |  UUID) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM 
                        chat_app.user_sessions where session_id = :sessionid
                    """)
        res = await self.session.execute(query, {"sessionid": sessionid})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    


    async def create(self, **kwargs):

        query = text("""
                        INSERT INTO chat_app.user_sessions (session_id,user_id,token_hash,device_info,user_agent,ip_address,created_at,last_activity_at,expires_at,revoked_at,session_status)
                        VALUES (:session_id,:user_id,:token_hash,:device_info,:user_agent,:ip_address,:created_at,:last_activity_at,:expires_at,:revoked_at,:session_status) 
                        RETURNING *
                    """)
        
        params = {}
        params.update(kwargs)
        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    

    async def update_activity(self, **kwargs) -> Optional[dict[str,Any]]:

        query =  text("""
                        UPDATE chat_app.user_sessions set last_activity_at = :last_activity where session_id = :session_id
                        RETURNING * 
                        """)
        params = {}
        params.update(kwargs)

        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()

        return dict(row) if row else None