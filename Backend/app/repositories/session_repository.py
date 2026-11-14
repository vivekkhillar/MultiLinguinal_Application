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
                        chat_app.user_sessions where session_id = :session_id
                    """)
        parsed_id = UUID(str(session_id)) if not isinstance(session_id,UUID) else session_id
        res = await self.session.execute(query, {"session_id": parsed_id})
        row = res.mappings().one_or_none()
        return dict(row) if row else None
    


    async def create(self, **kwargs : Any) -> Optional[dict[str,Any]]:

        required_fields = ["user_id", "token_hash", "expires_at"]

        for field in required_fields:
            if field not in kwargs or kwargs[field] is None:
                raise ValueError(f"{field} is required")

        params: Dict[str, Any] = {
            "user_id": UUID(str(kwargs["user_id"])) if not isinstance(kwargs["user_id"], UUID) else kwargs["user_id"],
            "token_hash": kwargs["token_hash"],
            "expires_at": kwargs["expires_at"],
            "device_info": kwargs.get("device_info"),
            "user_agent": kwargs.get("user_agent"),
            "ip_address": kwargs.get("ip_address"),
            "session_status": "ACTIVE",
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
        
        query =  text("""
                        UPDATE chat_app.user_sessions set last_activity_at = CURRENT_TIMESTAMP where session_id = :session_id
                        RETURNING * 
                        """)

        parsed_id = UUID(str(session_id)) if not isinstance(session_id, UUID) else session_id
        res = await self.session.execute(query, {"session_id": parsed_id})
        row = res.mappings().one_or_none()

        return dict(row) if row else None
    
    async def revoke(self, session_id:UUID) -> Optional[dict[str,Any]]:

        query = text("""UPDATE chat_app.user_sessions set revoked_at = CURRENT_TIMESTAMP , session_status = 'REVOKED' 
                        where session_id = :session_id
                        AND session_status != 'REVOKED'
                        RETURNING * """)
        parsed_id = UUID(str(session_id)) if not isinstance(session_id, UUID) else session_id
        res = await self.session.execute(query, {"session_id": parsed_id})
        row = res.mappings().one_or_none()

        return dict(row) if row else None

