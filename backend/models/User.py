from pydantic import BaseModel, EmailStr
from typing import Optional


# Pydantic Schemas
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str
    phone: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    password: Optional[str]
    role: Optional[str]
    phone: Optional[str]


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    role: str
    phone: Optional[str]