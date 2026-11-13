import os
import resend

from app.core.config import settings
from app.core.security import now_my

resend.api_key = settings.RESEND_API_KEY


def _build_otp_email_html(otp_code: str, heading: str, description: str, has_logo: bool) -> str:
    year = now_my().year
    logo_block = (
        '<div style="width: 72px; height: 72px; border-radius: 20px; background: #18181b; border: 1px solid #333333; margin: 0 auto 24px auto; padding: 12px; box-sizing: border-box;">'
        '<img src="cid:artiq-logo" width="48" height="48" alt="ArtiQ Logo" style="display: block; width: 48px; height: 48px; object-fit: contain;" />'
        "</div>"
        if has_logo
        else '<div style="font-size: 28px; font-weight: 900; color: #ffffff; background: #18181b; width: 64px; height: 64px; line-height: 64px; border-radius: 18px; margin: 0 auto 24px auto; border: 1px solid #444444;">ArtiQ</div>'
    )

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #050505; color: #ffffff; margin: 0; padding: 40px 20px;">
        <div style="max-width: 500px; margin: 0 auto; background-color: #111113; border: 1px solid #292a2e; border-radius: 24px; padding: 40px; text-align: center; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            {logo_block}
            <h2 style="font-size: 24px; font-weight: 700; margin: 0 0 12px 0; color: #ffffff; letter-spacing: -0.5px;">{heading}</h2>
            <p style="font-size: 15px; color: #a1a1aa; line-height: 1.6; margin: 0 0 32px 0;">{description}</p>
            <div style="background: linear-gradient(135deg, #3d63dd 0%, #0A84FF 100%); color: #ffffff; font-size: 40px; font-weight: 800; letter-spacing: 10px; padding: 20px 24px 20px 34px; border-radius: 16px; display: inline-block; margin-bottom: 32px; box-shadow: 0 10px 25px rgba(10, 132, 255, 0.3);">
                {otp_code}
            </div>
            <p style="font-size: 13px; color: #71717a; margin: 0;">This verification code expires in {settings.OTP_EXPIRE_MINUTES} minutes.<br>If you did not request this code, please ignore this email.</p>
            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid #292a2e; font-size: 11px; color: #71717a; text-transform: uppercase; letter-spacing: 1px;">
                &copy; {year} ArtiQ Smart AR Physiotherapy
            </div>
        </div>
    </body>
    </html>
    """


def send_otp_email(to_email: str, otp_code: str, purpose: str = "register") -> None:
    """Send a branded 6-digit OTP email with inline ArtiQ logo via Resend."""
    if purpose == "reset":
        subject = "ArtiQ Clinical Access - Password Reset Code"
        heading = "Password Reset Verification"
        description = (
            "A password reset was requested for your ArtiQ Clinical Dashboard account. "
            "Enter the verification code below to set a new password."
        )
    else:
        subject = "ArtiQ Clinical Access - Verification Code"
        heading = "Clinical Verification"
        description = (
            "You are registering an administrator account on the ArtiQ Clinical Dashboard. "
            "Use the verification code below to verify your email address."
        )

    logo_path = os.path.join(settings.FRONTEND_DIR, "logo.png")
    attachments = []
    has_logo = os.path.isfile(logo_path)
    if has_logo:
        with open(logo_path, "rb") as logo_file:
            attachments.append(
                {
                    "content": list(logo_file.read()),
                    "filename": "logo.png",
                    "content_id": "artiq-logo",
                }
            )

    payload: dict = {
        "from": settings.RESEND_SENDER,
        "to": to_email,
        "subject": subject,
        "html": _build_otp_email_html(otp_code, heading, description, has_logo),
    }
    if attachments:
        payload["attachments"] = attachments

    resend.Emails.send(payload)
