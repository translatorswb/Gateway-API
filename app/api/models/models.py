from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date, datetime, time, timedelta


class AdminModel(BaseModel):
    name: str = Field(...)
    password: str = Field(...)
    email: EmailStr = None

class UpdateAdminPasswordModel(AdminModel):
    new_password: str = Field(...)

class UpdateAdminModel(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class ClientModel(BaseModel):
    name: str = Field(...)
    email: EmailStr = None
    signup: datetime = None
    token_history: List[str] = []
    active_token: str = None

class UpdateClientModel(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class DeleteClientModel(BaseModel):
    name: str = Field(...)

class TokenModel(BaseModel):
    token: str = Field(unique=True)
    client: str = Field(...)
    creation_date: datetime
    toss_date: datetime
    expiry: str = None  #not implemented yet
    active: bool = Field(...)
    services: List[str] = []

class GenerateTokenModel(BaseModel):
    expiry: str = None
    services: List[str] = ['translate']

class RevokeTokenModel(BaseModel):
    client: str = Field(...)

class UsageModel(BaseModel):
    client: str = Field(...)
    token: str = Field(...)
    date: datetime = Field(...)
    service: str = Field(...)
    load: int = Field(...)

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
