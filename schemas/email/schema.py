from pydantic import BaseModel, EmailStr


class VerifyEmailOTP(BaseModel):
    email: EmailStr
    otp: str


class ResendEmailOTPRequest(BaseModel):
    email: EmailStr

