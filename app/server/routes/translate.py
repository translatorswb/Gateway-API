from typing import List, Optional, Dict
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

@router.get ("/")
async def languages():
    translate_url = mt_service_url + "/translate/languages"
    try:
        r = httpx.get(translate_url)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        return ErrorResponseModel("Internal request error", 503, "Translate service unavailable")

    if r.status_code == 200:
        response = r.json()
        languages_response = LanguagesResponse(languages=response['languages'])
        return languages_response
    else:
        return ErrorResponseModel("Translate service error", 500, r.json()['detail'])


@router.post('/', status_code=200)
async def translate(request: ServiceRequest):
    #Authenticate
    token = await check_token(request.token)
    if not token:
        return ErrorResponseModel("Not authorized", 401, "Bad token")

    #Check if token has service permission
    if not SERVICE_ID in token['services']:
        return ErrorResponseModel("Not authorized", 403, "Token not authorized to service: %s"%SERVICE_ID)

    print("Request from %s"%token['client'])

    batch_request = False
    if request.text:
        translate_service_url = mt_service_url + "/translate"

        if request.alt:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'text':request.text}
        else:
            json_data = {'src':request.src, 'tgt':request.tgt, 'text':request.text}
        
        usage = len(request.text.split())

    elif request.batch:
        batch_request = True
        translate_service_url = mt_service_url + "/translate/batch"

        if request.alt:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'texts':request.batch}
        else:
            json_data = {'src':request.src, 'tgt':request.tgt, 'alt':request.alt, 'texts':request.batch}

        usage = sum([len(text.split()) for text in request.batch])
    else:
        return ErrorResponseModel("Request error", 400, "Need input in batch or text")

    try:
        r = httpx.post(translate_service_url, json=json_data)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        return ErrorResponseModel("Internal request error", 503, "Translate service unavailable")

    if r.status_code == 200:
        response = r.json()
        print(response)
        if batch_request:
            service_response = BatchResponse(translation=response['translation'], usage=usage)
        else:
            service_response = SentenceResponse(translation=response['translation'], usage=usage)
        return service_response
    else:
        return ErrorResponseModel("Translate service error", 500, r.json()['detail'])
