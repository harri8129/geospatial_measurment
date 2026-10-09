from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_database


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    summary="Application health check",
)
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.get(
    "/database",
    summary="Database health check",
)
def database_health_check(
    db: Session = Depends(get_database),
) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from exc

    return {
        "status": "healthy",
        "database": "connected",
    }
