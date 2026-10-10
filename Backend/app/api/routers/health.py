from fastapi import APIRouter, HTTPException,status
from services.health_service import health_check


router = APIRouter(prefix= "/health", tags= ["health"])

@router.get("",status_code=status.HTTP_200_OK)
async def health():

    try:
        result = await health_check.check_health()
        return result

    except RuntimeError as e:
        payload = e.args[0] if e.args and isinstance(e.args[0], dict) else {"status": "unhealthy", "detail": str(e)}
        raise HTTPException(
            status_code= status.HTTP_503_SERVICE_UNAVAILABLE,
            detail= payload
        ) from e

    
