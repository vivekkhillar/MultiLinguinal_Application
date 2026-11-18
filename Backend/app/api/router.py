from fastapi import APIRouter
from api.routers.health import router as health_service
from api.routers.authentication import router as auth_service

router = APIRouter()

router.include_router(health_service)
router.include_router(auth_service)