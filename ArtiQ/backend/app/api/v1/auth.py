import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.middleware import limiter
from app.core.security import (
    create_access_token,
    generate_otp,
    hash_password,
    now_my_naive,
    validate_password_strength,
    verify_password,
)
from app.models.otp import OTPRecord
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    SendOTPRequest,
)
from app.schemas.common import api_response
from app.services.email_service import send_otp_email

router = APIRouter(tags=["Authentication"])


def _upsert_otp(db: Session, email: str, purpose: str) -> str:
    otp_code = generate_otp()
    expiration = now_my_naive() + datetime.timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

    record = db.query(OTPRecord).filter(OTPRecord.email == email).first()
    if record:
        record.otp = otp_code
        record.purpose = purpose
        record.attempts = 0
        record.expires_at = expiration
    else:
        record = OTPRecord(
            email=email,
            otp=otp_code,
            purpose=purpose,
            attempts=0,
            expires_at=expiration,
        )
        db.add(record)
    db.commit()
    return otp_code


def _verify_otp_or_raise(db: Session, email: str, otp: str, expected_purpose: str) -> OTPRecord:
    otp_record = db.query(OTPRecord).filter(OTPRecord.email == email).first()
    if not otp_record or otp_record.purpose != expected_purpose:
        raise HTTPException(status_code=400, detail="Invalid or missing OTP code.")

    if otp_record.expires_at < now_my_naive():
        db.delete(otp_record)
        db.commit()
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new code.")

    if otp_record.otp != otp:
        otp_record.attempts = (otp_record.attempts or 0) + 1
        if otp_record.attempts >= settings.OTP_MAX_ATTEMPTS:
            db.delete(otp_record)
            db.commit()
            raise HTTPException(
                status_code=400,
                detail="Maximum OTP attempts exceeded. Please request a new code.",
            )
        db.commit()
        remaining = settings.OTP_MAX_ATTEMPTS - otp_record.attempts
        raise HTTPException(
            status_code=400,
            detail=f"Invalid OTP code. {remaining} attempt(s) remaining.",
        )

    return otp_record


@router.post("/api/send-otp")
@router.post("/api/v1/auth/send-otp")
@limiter.limit("3/minute")
def send_otp(request: Request, req: SendOTPRequest, db: Session = Depends(get_db)):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    otp_code = _upsert_otp(db, email, purpose="register")
    try:
        send_otp_email(email, otp_code, purpose="register")
        return api_response(True, "OTP sent to your email.")
    except Exception as exc:
        print(f"[ERROR] Resend API: {str(exc)}", flush=True)
        raise HTTPException(status_code=500, detail="Failed to deliver verification email.")


@router.post("/api/register")
@router.post("/api/v1/auth/register")
@limiter.limit("5/minute")
def register_user(request: Request, req: RegisterRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    email = req.email.strip().lower()

    if not username:
        raise HTTPException(status_code=400, detail="Username is required.")

    pw_error = validate_password_strength(req.password)
    if pw_error:
        raise HTTPException(status_code=400, detail=pw_error)

    otp_record = _verify_otp_or_raise(db, email, req.otp.strip(), expected_purpose="register")

    existing_user = (
        db.query(User)
        .filter((User.username == username) | (User.email == email))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email is already registered.")

    hashed_pw = hash_password(req.password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_pw,
        is_admin=True,
        is_active=True,
        failed_login_attempts=0,
        locked_until=None,
    )

    db.add(new_user)
    db.delete(otp_record)  # Single-use OTP invalidation
    db.commit()

    return api_response(True, "Admin account created and verified successfully.")


@router.post("/api/login")
@router.post("/api/v1/auth/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    req: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    username = req.username.strip()
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    now = now_my_naive()
    if user.locked_until and user.locked_until > now:
        wait_mins = max(1, int((user.locked_until - now).total_seconds() // 60) + 1)
        raise HTTPException(
            status_code=423,
            detail=f"Account temporarily locked due to failed attempts. Try again in {wait_mins} minute(s).",
        )

    if not verify_password(req.password, user.hashed_password):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGINS:
            user.locked_until = now + datetime.timedelta(minutes=settings.LOCKOUT_MINUTES)
            user.failed_login_attempts = 0
            db.commit()
            raise HTTPException(
                status_code=423,
                detail=f"Too many failed attempts. Account locked for {settings.LOCKOUT_MINUTES} minutes.",
            )
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is not activated.")

    # Reset failed login counter on successful authentication
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()

    token = create_access_token(user.username)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_HOURS * 3600,
    )
    return api_response(True, "Login successful.")


@router.post("/api/forgot-password")
@router.post("/api/v1/auth/forgot-password")
@limiter.limit("3/minute")
def forgot_password(
    request: Request, req: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")

    user = db.query(User).filter(User.email == email).first()
    if user:
        otp_code = _upsert_otp(db, email, purpose="reset")
        try:
            send_otp_email(email, otp_code, purpose="reset")
        except Exception as exc:
            print(f"[ERROR] Resend API (Reset): {str(exc)}", flush=True)
            raise HTTPException(status_code=500, detail="Failed to send reset email.")

    return api_response(
        True,
        "If an account exists for this email, a 6-digit reset code has been sent.",
    )


@router.post("/api/reset-password")
@router.post("/api/v1/auth/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request, req: ResetPasswordRequest, db: Session = Depends(get_db)
):
    email = req.email.strip().lower()
    pw_error = validate_password_strength(req.new_password)
    if pw_error:
        raise HTTPException(status_code=400, detail=pw_error)

    otp_record = _verify_otp_or_raise(db, email, req.otp.strip(), expected_purpose="reset")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Account not found.")

    user.hashed_password = hash_password(req.new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    db.delete(otp_record)  # Single-use OTP invalidation
    db.commit()

    return api_response(True, "Password reset successful. Please sign in.")


@router.post("/api/logout")
@router.post("/api/v1/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return api_response(True, "Logged out successfully.")


@router.get("/api/user")
@router.get("/api/v1/auth/me")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return api_response(
        True,
        "Authenticated user retrieved.",
        data={"name": current_user.username, "email": current_user.email},
    )
