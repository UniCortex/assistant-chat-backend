from fastapi import APIRouter

from app.presentation.http.controllers.general.health import router as health_router
from app.presentation.http.controllers.queuing.router import router as queuing_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(queuing_router)
