from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class SendOTPRequest(BaseModel):
    email: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    otp: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str
