# tenants/models.py
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import datetime

class TenantBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    government_id: Optional[str] = None
    emergency_contact: Optional[Dict] = None

class TenantCreate(TenantBase):
    pass

class TenantUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    government_id: Optional[str] = None
    emergency_contact: Optional[Dict] = None

class TenantResponse(TenantBase):
    id: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


