from fastapi import APIRouter

from .poll import router as poll_router
from .stream import router as stream_router
from .submit import router as submit_router

router = APIRouter(prefix="/queuing", tags=["queuing"])

router.include_router(submit_router)
router.include_router(poll_router)
router.include_router(stream_router)
