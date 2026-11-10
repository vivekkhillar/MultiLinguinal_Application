from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from core.lifespan import lifespan_instance


class UserRepository:

    def __init__(self) -> None:
        self.db = lifespan_instance.database_manager


    async def get_by_email(self,email: str)-> Optional[Dict[str,Any]]:
        
        # during writing the sql query need to remember the SELECT,  UPDATE everything need to be write with all caps and during sending any 
        # value while executing the query we need to send with the = : symbol
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE email = :email
                    """)

        async with self.db.get_session() as session:
            
            result = await session.execute(query, {"email": email})
            row = result.mappings().one_or_none()

            return dict(row) if row else None
    

    async def get_by_username(self,username: str)-> Optional[Dict[str,Any]]:
        
        
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE username = :username
                    """)

        async with self.db.get_session() as session:
            
            result = await session.execute(query, {"username": username})
            row = result.mappings().one_or_none()

            return dict(row) if row else None
    
    async def get_by_id(self,user_id: str | UUID)-> Optional[Dict[str,Any]]:
        
        
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE user_id = :user_id
                    """)

        async with self.db.get_session() as session:
            
            result = await session.execute(query, {"user_id": user_id})
            row = result.mappings().one_or_none()

            return dict(row) if row else None