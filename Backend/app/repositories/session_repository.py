from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:

    def __init__(self,session: AsyncSession) -> None:

        self.session = session
    

    async def get_by_token_hash(self,token_hash : str) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM
                        chat_app.user_sessions where token_hash = :token_hash 
                    """)
        res = await self.session.execute(query,{"token_hash": token_hash})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    
    async def get_by_id(self, session_id: str |  UUID) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM 
                        chat_app.user_sessions where session_id = :sessionid
                    """)
        res = await self.session.execute(query, {"sessionid": session_id})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    


    async def create(self, **kwargs):

        required_fields = ["user_id", "token_hash", "expires_at"]

        for field in required_fields:
            if field not in kwargs or kwargs[field] is None:
                raise ValueError(f"{field} is required")

        params: Dict[str, Any] = {
            "device_info": None,
            "user_agent": None,
            "ip_address": None,
            "session_status": "ACTIVE",
            **kwargs
        }
        
        
        query = text(
                    """
                        INSERT INTO chat_app.user_sessions (user_id,token_hash,device_info,user_agent,ip_address,expires_at,session_status)
                        VALUES (:user_id,:token_hash,:device_info,:user_agent,:ip_address,:expires_at,:session_status) 
                        RETURNING *
                    """)
        
        
        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    

    async def update_activity(self, session_id: UUID) -> Optional[dict[str,Any]]:
        
        from datetime import datetime,timezone

        query =  text("""
                        UPDATE chat_app.user_sessions set last_activity_at = :last_activity where session_id = :session_id
                        RETURNING * 
                        """)

        params = {
            "session_id" : session_id,
            "last_activity" : datetime.now(timezone.utc)
        }

        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()

        return dict(row) if row else None