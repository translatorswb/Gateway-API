from typing import List, Optional
from fastapi import Header, APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import os
import json
import re

from app.server.database.database import *
from app.server.models.models import ResponseModel, ErrorResponseModel

router = APIRouter()

MT_API_HOST_URL = 'http://localhost:8001/api/v1'
mt_service_url = os.environ.get('MT_API_HOST_URL') or MT_API_HOST_URL
mt_service_request_headers = {'Content-Type': 'application/json'}

#HTTP operations
class ServiceRequest(BaseModel):
    src: str = Field(...)
    tgt: str = Field(...)
    token: str = Field(...)
    text: Optional[str] = None
    batch: Optional[str] = None
    alt: Optional[str] = None  #for alternative models


class ServiceResponse(BaseModel):
    translation: str
    usage: int


@router.post('/', status_code=200)
async def translate(request: ServiceRequest):
    #Authenticate
    token = await check_token(request.token)
    if not token:
        return ErrorResponseModel("Not authorized", 404, "Bad token")

    print("Request from %s"%token['client'])

    translate_service_url = mt_service_url + "/translate"
    print(translate_service_url)

    #TODO: Check text or batch
    
    payload="{\"src\":\"%s\", \"tgt\":\"%s\", \"text\":\"%s\", \"token\":\"%s\"}"%(request.src, 
                                                                                   request.tgt, 
                                                                                   request.text, 
                                                                                   request.token)
    try:
        r = httpx.post(translate_service_url, data=payload, headers=mt_service_request_headers)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        return ErrorResponseModel("Internal request error", 404, "Translate service unavailable")

    #TODO: Store usage
    usage = len(request.src.split())

    if r.status_code == 200:
        response = r.json()
        print(response)
        service_response = ServiceResponse(translation=response['translation'], usage=usage)
        return service_response
    else:
        return ErrorResponseModel("Translate service error", 404, r.json()['detail'])
