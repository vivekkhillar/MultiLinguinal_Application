from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:

    def __init__(self,session= AsyncSession) -> None:

        self.session = session
    

    async def get_by_token_hash(self,token_hash : str) -> Optional[dict[str,Any]]:

        query = text("""
                        SELECT * FROM
                        chat_app.user_sessions where token_hash = :token_hash 
                    """)
        res = await self.session.execute(query,{"token_hash": token_hash})
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

        params: Dict[str, Any] = {
            "user_id": None,
            "token_hash": None,
            "device_info": None,
            "user_agent": None,
            "ip_address": None,
            "expires_at": None,
            "session_status": "ACTIVE",  # Default status if not provided
        }
        params.update(kwargs)
        
        query = text(
                    """
                        INSERT INTO chat_app.user_sessions (user_id,token_hash,device_info,user_agent,ip_address,expires_at,session_status)
                        VALUES (:user_id,:token_hash,:device_info,:user_agent,:ip_address,:expires_at,:session_status) 
                        RETURNING *
                    """)
        
        
        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    

    async def update_activity(self, **kwargs) -> Optional[dict[str,Any]]:
        
        from datetime import datetime,timezone

        query =  text("""
                        UPDATE chat_app.user_sessions set last_activity_at = :last_activity where session_id = :session_id
                        RETURNING * 
                        """)

        params = {
            "session_id" : None,
            "last_activity" : datetime.now(timezone.utc)
        }
        params.update(kwargs)

        res = await self.session.execute(query, params)
        row = res.mappings().one_or_none()

        return dict(row) if row else None