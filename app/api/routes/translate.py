from typing import List, Optional, Dict
from fastapi import Header, APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import os
import json
import re

from app.api.database.database import *
from app.api.models.models import ResponseModel, ErrorResponseModel
from app.api.database.database import check_token, register_usage

router = APIRouter()

MT_API_HOST_URL = 'http://localhost:8001/api/v1'
mt_service_url = os.environ.get('MT_API_HOST_URL') or MT_API_HOST_URL

SERVICE_ID = 'translate'

#HTTP operations
class ServiceRequest(BaseModel):
    src: str = Field(...)
    tgt: str = Field(...)
    token: str = Field(...)
    text: Optional[str] = None
    batch: Optional[List[str]] = None
    alt: Optional[str] = None  #for alternative models

class SentenceResponse(BaseModel):
    translation: str
    usage: int

class BatchResponse(BaseModel):
    translation: List[str]
    usage: int

class LanguagesResponse(BaseModel):
    languages: Dict
    models: Dict

@router.get('/')
async def languages():
    translate_url = mt_service_url + "/translate/languages"
    try:
        r = httpx.get(translate_url)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        #return ErrorResponseModel("Internal request error", 503, "Translate service unavailable")
        raise HTTPException(status_code=503, detail="Translate service unavailable")

    if r.status_code == 200:
        response = r.json()
        languages_response = LanguagesResponse(languages=response['languages'], models=response['models'])
        return languages_response
    else:
        #return ErrorResponseModel("Translate service error", 500, r.json()['detail'])
        raise HTTPException(status_code=500, detail="Translate service error: %s"%r.json()['detail'])


@router.post('/', status_code=200)
async def translate(request: ServiceRequest):
    #Authenticate
    token = await check_token(request.token)
    if not token:
        #return ErrorResponseModel("Not authorized", 401, "Bad token")
        raise HTTPException(status_code=401, detail="Token not found in database")

    #Check if token has service permission
    if not SERVICE_ID in token['services']:
        #return ErrorResponseModel("Not authorized", 403, "Token not authorized to service: %s"%SERVICE_ID)
        raise HTTPException(status_code=403, detail="Token not authorized to service: %s"%SERVICE_ID)

    print("Request from %s"%token['client'])

    batch_request = False
    if request.text:
        translate_service_url = mt_service_url + "/translate"

        if request.alt:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'text':request.text}
        else:
            json_data = {'src':request.src, 'tgt':request.tgt, 'text':request.text}
        
        usage_load = len(request.text.split())
        

    elif request.batch:
        batch_request = True
        translate_service_url = mt_service_url + "/translate/batch"

        if request.alt:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'texts':request.batch}
        else:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'texts':request.batch}

        usage_load = sum([len(text.split()) for text in request.batch])
    else:
        #return ErrorResponseModel("Request error", 400, "Need input in batch or text")
        raise HTTPException(status_code=400, detail="Need input in batch or text")

    try:
        r = httpx.post(translate_service_url, json=json_data)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        #return ErrorResponseModel("Internal request error", 503, "Translate service unavailable")
        raise HTTPException(status_code=503, detail="Translate service unavailable")

    if r.status_code == 200:
        #Store usage
        await register_usage(token, SERVICE_ID, usage_load)

        response = r.json()
        print(response)
        if batch_request:
            service_response = BatchResponse(translation=response['translation'], usage=usage_load)
        else:
            service_response = SentenceResponse(translation=response['translation'], usage=usage_load)
        return service_response
    else:
        #return ErrorResponseModel("Translate service error", 500, r.json()['detail'])
        raise HTTPException(status_code=500, detail="Translate service error: %s"%r.json()['detail'])

