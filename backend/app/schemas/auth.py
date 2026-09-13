from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    org_id: Optional[str] = None
    role: Optional[str] = None

class OrganizationBase(BaseModel):
    name: str

class OrganizationCreate(OrganizationBase):
    slug: Optional[str] = None

class OrganizationOut(OrganizationBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    slug: str
    created_at: datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "analyst"

class UserCreate(UserBase):
    password: str
    org_name: Optional[str] = "Default Organization"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    org_id: str
    is_active: bool
    created_at: datetime
    organization: Optional[OrganizationOut] = None
