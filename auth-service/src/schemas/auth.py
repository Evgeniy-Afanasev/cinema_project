import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email: EmailStr
    login: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class UserLogin(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    login: Optional[str] = Field(default=None, min_length=3, max_length=50)
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)

class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)

class RoleRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class UserRead(BaseModel):
    id: int
    email: EmailStr
    login: str
    roles: List[RoleRead] = []
    class Config:
        from_attributes = True

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  

class RefreshRequest(BaseModel):
    refresh_token: str

class PermissionCheckRequest(BaseModel):
    login: str
    required_role: str

class LoginHistoryRead(BaseModel):
    id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime.datetime
    class Config:
        from_attributes = True
