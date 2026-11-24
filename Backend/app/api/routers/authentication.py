from fastapi import APIRouter, HTTPException,status,Request,Depends,Response
from typing import Annotated
from services.authentication_service import AuthenticationService
from sqlalchemy.exc import SQLAlchemyError,OperationalError
from schemas.authentication import (
    RegisterRequest,
    RegisterResponse,
    LoginResponse,
    LoginRequest,
    LogoutResponse,
    RefreshResponse
    )

from api.dependencies import get_authentication_service
from core.exception import (
    EmailAlreadyExistsError, 
    UsernameAlreadyExistsError,
    InvalidPreferredLanguageError,
    InvalidCredentialsError,
    AccountInactiveError
)

from core.logging_config import _get_logger
from core.config import config
logger = _get_logger()
cfg = config()


router = APIRouter(prefix= "/auth", tags= ["Authentication"])

@router.post("/register", response_model = RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest , auth_service : Annotated[AuthenticationService,Depends(get_authentication_service)]):

    try:
        result = await auth_service.register(**request.model_dump())
        return result

    except (EmailAlreadyExistsError,UsernameAlreadyExistsError) as e:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail = str(e),
        ) from e
    
    except InvalidPreferredLanguageError as e:
        raise HTTPException(
            status_code= status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail = str(e),
        ) from e
    
    except OperationalError as e:
        logger.exception("Database operational error during registration")
        raise HTTPException(
              status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
              detail="Database service is temporarily unavailable.",
          ) from e

    except SQLAlchemyError as e:
        logger.exception("Unexpected database error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while registering the user.",
        ) from e

    
@router.post("/login", response_model = LoginResponse, status_code=status.HTTP_200_OK)
async def login(payload: LoginRequest , request: Request, response: Response, auth_service : Annotated[AuthenticationService,Depends(get_authentication_service)]):

    try:

        result = await auth_service.login(
            username = payload.username,
            password = payload.password,
            ip_address = request.client.host if request.client else None,
            user_agent = request.headers.get("user-agent"),
            device_info = request.headers.get("x-device-info")
        )
        
        refresh_token = result.pop("refresh_token")
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Change to True in production over HTTPS
            samesite="lax",
            max_age=cfg.SESSION_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )

        return result

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= str(e),
        )
    
    except AccountInactiveError as e:
        raise HTTPException(
            status_code = status.HTTP_403_FORBIDDEN,
            detail= str(e)
        )
    
    except OperationalError as e:
        logger.exception("Database operational error during login")
        raise HTTPException(
              status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
              detail="Database service is temporarily unavailable.",
          ) from e
        
    except SQLAlchemyError as e:
        logger.exception("Unexpected database error during login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while logging the user.",
        ) from e

@router.post("/refresh", response_model= RefreshResponse,status_code= status.HTTP_200_OK)
async def refresh():
    return {"msg": "Refreshed token dummy response"}

@router.post("/logout", response_model=LogoutResponse , status_code= status.HTTP_200_OK)
async def logout(requset: Request,response : Response, auth_service : Annotated[AuthenticationService,Depends(get_authentication_service)]):

    try:

        refresh_token = requset.cookies.get('refresh_token')
        result = await auth_service.logout(refresh_token=refresh_token)

        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            secure=False,  # Match the same flags used in set_cookie()
            samesite="lax",
        )

        return result

    except OperationalError as e:

        logger.exception("Database operational error during logout")
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service is temporarily unavailable.",
        ) from e
    
    except SQLAlchemyError as e:
        logger.exception("Unexpected database error during logout")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while logging out.",
        ) from e