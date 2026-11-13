import os
import secrets
from zoneinfo import ZoneInfo


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = "ArtiQ Smart AR Physiotherapy"
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is missing in .env")

    SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(48)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 12

    RESEND_API_KEY: str | None = os.environ.get("RESEND_API_KEY")
    RESEND_SENDER: str = os.environ.get(
        "RESEND_SENDER", "ArtiQ Security <artiq@mail.flowkraft.xyz>"
    )

    MQTT_BROKER: str = os.environ.get("MQTT_BROKER", "artiq_mqtt")
    MQTT_PORT: int = int(os.environ.get("MQTT_PORT", "1883"))

    FRONTEND_DIR: str = os.environ.get("FRONTEND_DIR", "/frontend")
    TIMEZONE_NAME: str = "Asia/Kuala_Lumpur"
    TIMEZONE: ZoneInfo = ZoneInfo("Asia/Kuala_Lumpur")

    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5
    MAX_FAILED_LOGINS: int = 5
    LOCKOUT_MINUTES: int = 15


settings = Settings()
