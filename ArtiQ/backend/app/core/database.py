import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Initialize database tables and apply safe additive column migrations."""
    # Import models so SQLAlchemy metadata registers all tables
    from app.models.user import User  # noqa: F401
    from app.models.otp import OTPRecord  # noqa: F401
    from app.models.session import ExerciseSession  # noqa: F401

    while True:
        try:
            Base.metadata.create_all(bind=engine)
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE users "
                        "ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE, "
                        "ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0, "
                        "ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP NULL;"
                    )
                )
                conn.execute(
                    text(
                        "ALTER TABLE otps "
                        "ADD COLUMN IF NOT EXISTS purpose VARCHAR DEFAULT 'register', "
                        "ADD COLUMN IF NOT EXISTS attempts INTEGER DEFAULT 0;"
                    )
                )
            print("[INFO] Database connected and schema verified!", flush=True)
            break
        except OperationalError:
            print("[WARN] Database not ready yet, retrying in 3 seconds...", flush=True)
            time.sleep(3)
