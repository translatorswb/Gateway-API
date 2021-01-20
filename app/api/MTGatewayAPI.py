from typing import List, Optional
from fastapi import Header, APIRouter, HTTPException
from pydantic import BaseModel 
import httpx
import os
import json
import re

gateway_mt = APIRouter()

MT_API_HOST_URL = 'http://localhost:8001/mt-api/v1'
mt_service_url = os.environ.get('MT_API_HOST_URL') or MT_API_HOST_URL
mt_service_request_headers = {'Content-Type': 'application/json'}

#HTTP operations
class ServiceRequest(BaseModel):
    src: str
    tgt: str
    text: str
    token: str

class ServiceResponse(BaseModel):
    translation: str
    usage: int


@gateway_mt.get('/', status_code=200)
async def translate(request: ServiceRequest):
    #TODO: Checks
    
    payload="{\"src\":\"%s\", \"tgt\":\"%s\", \"text\":\"%s\", \"token\":\"%s\"}"%(request.src, 
                                                                                   request.tgt, 
                                                                                   request.text, 
                                                                                   request.token)
    try:
        r = httpx.post(mt_service_url, data=payload, headers=mt_service_request_headers)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        raise HTTPException(status_code=503, detail="Translate service unavailable")

    if r.status_code == 200:
        return r.json()
    else:
        raise HTTPException(status_code=401, detail="Translate API: %s"%(r.json()['detail']))