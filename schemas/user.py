# schemas/user.py
from pydantic import BaseModel

class UserCreateSchema(BaseModel):
    username: str
    email: str
    password: str

class UserCreateResponseSchema(BaseModel):
    user_id: int
    username: str
    email: str

# schemas/user.py
class ForgotPasswordSchema(BaseModel):
    email: str

class ResendOtpSchema(BaseModel):
    email: str

class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserLoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str

class VerifyOtpSchema(BaseModel):
    email: str
    otp:   str