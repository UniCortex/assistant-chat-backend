from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["general"])


@router.get(
    "/health",
    summary="Health check",
    response_description="Service liveness probe",
)
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})
