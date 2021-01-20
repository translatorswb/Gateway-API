from typing import List, Optional
from fastapi import Header, APIRouter, HTTPException
from pydantic import BaseModel 
import os
import json
import re

gateway_admin = APIRouter()

@gateway_admin.get('/', status_code=200)
async def index():
    return "Register superadmin"


@gateway_admin.post('/', status_code=200)
async def index():
    return "Admin login"