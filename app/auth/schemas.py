from pydantic import BaseModel, EmailStr, constr
from app.auth.models import UserRole
#field validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=6)
    role: UserRole

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
