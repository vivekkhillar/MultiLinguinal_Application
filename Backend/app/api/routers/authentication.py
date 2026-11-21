from fastapi import APIRouter, HTTPException,status,Depends
from typing import Annotated
from services.authentication_service import AuthenticationService
from sqlalchemy.exc import SQLAlchemyError
from schemas.authentication import RegisterRequest,RegisterResponse,LoginResponse,LoginRequest
from api.dependencies import get_authentication_service
from core.exception import (UsernameAlreadyExistsError,EmailAlreadyExistsError,InvalidPreferredLanguageError)
from core.logging_config import _get_logger

logger = _get_logger()

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
            status_code= status.HTTP_409_CONFLICT,
            detail = str(e),
        ) from e

    except RuntimeError as e:
        payload = e.args[0] if e.args and isinstance(e.args[0], dict) else {"status": "unhealthy", "detail": str(e)}
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail= payload
        ) from e
    
    except SQLAlchemyError as e:
        logger.exception("Unexpected database error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while registering the user.",
        ) from e

    
@router.post("/login", response_model = LoginResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest , auth_service : Annotated[AuthenticationService,Depends(get_authentication_service)]):

    try:
        result = await auth_service.login(**request.model_dump())
        return result

    

    except RuntimeError as e:
        payload = e.args[0] if e.args and isinstance(e.args[0], dict) else {"status": "unhealthy", "detail": str(e)}
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail= payload
        ) from e

