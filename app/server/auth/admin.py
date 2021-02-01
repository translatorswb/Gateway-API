from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from passlib.context import CryptContext
import pprint

from app.server.database.database import admin_collection
from app.server.database.database_helper import admin_helper
from app.server.models.models import AdminModel

security = HTTPBasic()
hash_helper = CryptContext(schemes=["bcrypt"])

async def validate_login(credentials: AdminModel):
    admin = await admin_collection.find_one({"name": credentials.name})
    if admin:
        password = hash_helper.verify(credentials.password, admin['password'])
        if password:
            return True
    return False

