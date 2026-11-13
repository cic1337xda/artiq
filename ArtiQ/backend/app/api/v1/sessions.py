from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import now_my_naive
from app.models.session import ExerciseSession
from app.models.user import User
from app.schemas.common import api_response
from app.schemas.session import SessionStartRequest, SessionStopRequest

router = APIRouter(tags=["Exercise Sessions"])


@router.post("/api/session/start")
@router.post("/api/v1/sessions/start")
def start_session(
    req: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_session = ExerciseSession(
        user_id=current_user.id,
        user_name=req.name.strip() or "Guest",
        user_age=max(0, req.age),
        start_time=now_my_naive(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return api_response(
        True,
        "Exercise session started.",
        data={"session_id": new_session.id},
    )


@router.post("/api/session/stop")
@router.post("/api/v1/sessions/stop")
def stop_session(
    data: SessionStopRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership verification (IDOR / BOLA prevention)
    db_session = (
        db.query(ExerciseSession)
        .filter(
            ExerciseSession.id == data.session_id,
            ExerciseSession.user_id == current_user.id,
        )
        .first()
    )
    if not db_session:
        raise HTTPException(status_code=404, detail="Exercise session not found.")

    db_session.end_time = now_my_naive()
    db_session.total_reps = max(0, data.reps)
    db.commit()
    return api_response(True, "Exercise session saved.")


@router.get("/api/history")
@router.get("/api/v1/sessions/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = (
        db.query(ExerciseSession)
        .filter(ExerciseSession.user_id == current_user.id)
        .order_by(ExerciseSession.id.desc())
        .limit(15)
        .all()
    )
    history = [
        {
            "id": s.id,
            "name": s.user_name,
            "age": s.user_age,
            "start_time": s.start_time.isoformat() if s.start_time else None,
            "total_reps": s.total_reps,
        }
        for s in results
    ]
    return api_response(True, "Session history retrieved.", data=history)
