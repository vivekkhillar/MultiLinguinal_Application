from fastapi import APIRouter, HTTPException,status
from services.health_service import health_check


router = APIRouter(prefix= "/health", tags= ["health"])

@router.get("",status_code=status.HTTP_200_OK)
async def health():

    try:
        result = await health_check.check_health()
        return result

    except RuntimeError as e:

        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = str(e)
        ) from e

    
