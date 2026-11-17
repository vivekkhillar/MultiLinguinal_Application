# Without the dependencies we need to create objectes everytime and for all the API is need to done the same 
# So to avoid we need to create depencdencies so that it would be the common services we were passed to the api layer where multiple time object creation will avoid

from typing import Annotated,AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# import the dependencies from file
from core.lifespan import lifespan_instance
from repositories.user_repository import UserRepository
from security.password import PasswordHashing
from services.authentication_service import AuthenticationService

async def get_db_session() -> AsyncGenerator[AsyncSession,None]:

    async with lifespan_instance.database_manager.get_session() as session:
        yield session 


def get_user_repository(session : Annotated[AsyncSession,Depends(get_db_session)]) -> UserRepository:
    return UserRepository(session)


def get_password_hasher() -> PasswordHashing:
    return PasswordHashing()

def get_authentication_service(
    user_repository : Annotated[UserRepository, Depends(get_user_repository)],
    password_hasher : Annotated[PasswordHashing,Depends(get_password_hasher)]
)-> AuthenticationService:

    return AuthenticationService(user_repository=user_repository,
        password_hasher=password_hasher)

