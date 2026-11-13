from sqlalchemy import Column, DateTime, Integer, String
from app.core.database import Base


class OTPRecord(Base):
    __tablename__ = "otps"

    email = Column(String, primary_key=True, index=True)
    otp = Column(String, nullable=False)
    purpose = Column(String, default="register")
    attempts = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
