# Centralized dependency providers for database sessions,
# repositories, security utilities, and application services.


from typing import Annotated,AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

# import the dependencies from file
from core.lifespan import lifespan_instance
from repositories.user_repository import UserRepository
from repositories.session_repository import SessionRepository
from security.password import PasswordHashing
from security.jwt import JWT
from services.authentication_service import AuthenticationService
from security.session_token import SessionToken
from core.config import config

# get the session details from the fast api
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:

    async with lifespan_instance.database_manager.get_session() as session:
        yield session # Function initialized but due to yield it kept into the hold process call then it will return the session

# Pass the session details in to the get_user_repository so the 
def get_user_repository(session : Annotated[AsyncSession,Depends(get_db_session)]) -> UserRepository:
    return UserRepository(session)

def get_session_repository(session: Annotated[AsyncSession,Depends(get_db_session)]) -> SessionRepository:
    return SessionRepository(session)

# Create a object of the password hasher then send into the authentication service so no need to create an object of that
def get_password_hasher() -> PasswordHashing:
    return PasswordHashing()

def get_session_token() -> SessionToken:
    return SessionToken()

def get_jwt_handler() -> JWT:
    return JWT()

# Seding the function into the service function
def get_authentication_service(
    user_repository : Annotated[UserRepository, Depends(get_user_repository)],
    session_repository: Annotated[SessionRepository,Depends(get_session_repository)],
    password_hasher : Annotated[PasswordHashing,Depends(get_password_hasher)],
    session_token : Annotated[SessionToken,Depends(get_session_token)],
    jwt : Annotated[JWT,Depends(get_jwt_handler)]
)-> AuthenticationService:

    return AuthenticationService(
            session_repository=session_repository,
            user_repository=user_repository,
            password_hasher=password_hasher,
            session_token = session_token,
            jwt = jwt,
            config_details=config(),
        )

