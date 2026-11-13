from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import now_my

router = APIRouter(tags=["Health"])


@router.get("/api/v1/health")
@router.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """Verify PostgreSQL connectivity and report service health in GMT+8."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": now_my().isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Database healthcheck failed: {str(exc)}",
        )
