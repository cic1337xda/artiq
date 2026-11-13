from sqlalchemy import Column, DateTime, Integer, String
from app.core.database import Base
from app.core.security import now_my_naive


class ExerciseSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    user_name = Column(String, default="Guest")
    user_age = Column(Integer, default=0)
    start_time = Column(DateTime, default=now_my_naive)
    end_time = Column(DateTime, nullable=True)
    total_reps = Column(Integer, default=0)
