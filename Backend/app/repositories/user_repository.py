from uuid import UUID
from typing import Any, Dict, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

class UserRepository:

    def __init__(self,session : AsyncSession) -> None:
        self.session = session

    async def get_by_email(self,email: str)-> Optional[Dict[str,Any]]:
        
        # during writing the sql query need to remember the SELECT,  UPDATE everything need to be write with all caps and during sending any 
        # value while executing the query we need to send with the = : symbol
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE email = :email
                    """)

        
            
        result = await self.session.execute(query, {"email": email})
        row = result.mappings().one_or_none()

        return dict(row) if row else None
    

    async def get_by_username(self,username: str)-> Optional[Dict[str,Any]]:
        
        
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE username = :username
                    """)
            
        result = await self.session.execute(query, {"username": username})
        row = result.mappings().one_or_none()

        return dict(row) if row else None
    
    async def get_by_id(self,user_id: str | UUID)-> Optional[Dict[str,Any]]:
        
        
        query = text(
                    """ 
                        SELECT * 
                        FROM chat_app.users 
                        WHERE user_id = :user_id
                    """)

        
            
        result = await self.session.execute(query, {"user_id": user_id})
        row = result.mappings().one_or_none()

        return dict(row) if row else None


    async def create(self, **kwargs) -> Optional[Dict[str,Any]] :

        required_fields = ["username", "email", "password_hash", "first_name", "preferred_language_id"]

        for fields in required_fields:
            if fields not in kwargs or kwargs[fields] is None:
                raise ValueError(f"{fields} are required")
        
        params : Dict[str,Any] = {
            "username" : kwargs['username'],
            "email" : kwargs['email'],
            "password_hash" : kwargs['password_hash'],
            "first_name": kwargs['first_name'],
            "last_name" : kwargs.get('last_name'),
            "preferred_language_id" : kwargs['preferred_language_id']
        }

        query = text("""
                        INSERT into chat_app.users(username, email, password_hash, first_name, last_name, preferred_language_id)
                        VALUES(:username,:email,:password_hash,:first_name,:last_name,:preferred_language_id)
                        RETURNING user_id, username, email, first_name, last_name, account_status  
                    """)
        
        async with self.session.begin_nested():
            res = await self.session.execute(query, params)
            row = res.mappings().one()

        return dict(row)