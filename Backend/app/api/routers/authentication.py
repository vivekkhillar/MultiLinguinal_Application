from fastapi import APIRouter, HTTPException,status,Depends, status
from typing import Annotated
from services.authentication_service import AuthenticationService
from schemas.authentication import RegisterRequest,RegisterResponse
from api.dependencies import get_authentication_service

router = APIRouter(prefix= "/auth", tags= ["authentication"])

@router.post("/register", response_model = RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(request: RegisterRequest , auth_service : Annotated[AuthenticationService,Depends(get_authentication_service)]):

    try:
        result = await auth_service.register(**request.model_dump())
        return result

    except RuntimeError as e:
        payload = e.args[0] if e.args and isinstance(e.args[0], dict) else {"status": "unhealthy", "detail": str(e)}
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail= payload
        ) from e

    
