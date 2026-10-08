from app.core.database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {"status": "healthy"}


@api_router.get("/health/database")
def database_health_check(db:Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}  