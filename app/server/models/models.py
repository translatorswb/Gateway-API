from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
import datetime


class AdminModel(BaseModel):
    name: str = Field(...)
    password: str = Field(...)
    email: Optional[EmailStr] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "admin",
                "password": "secure password"
            }
        }

class UpdateAdminPasswordModel(AdminModel):
    new_password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "admin",
                "password": "old password",
                "new_password": "new secure password"
            }
        }

class ClientModel(BaseModel):
    name: str = Field(...)
    email: EmailStr = None
    # signup_ts: Optional[datetime] = None
    token_history: Optional[List[str]] = []
    active_token: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "CollectivaT",
                "email": "user@collectivat.cat"
            }
        }

class TokenModel(BaseModel):
    token: str = Field(unique=True)
    client: str = Field(...)
    expiry: Optional[str] = Field(...)
    active: bool = Field(...)

class GenerateTokenModel(BaseModel):
    client: str = Field(...)
    expiry: Optional[str] = Field(...)

class RevokeTokenModel(BaseModel):
    client: str = Field(...)

def ResponseModel(data, message):
    return {
        "data": [
            data
        ],
        "code": 200,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message
    }
