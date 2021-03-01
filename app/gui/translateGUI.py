from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
import httpx
import json
import os

from app.api.database.database import register_usage

app = APIRouter()

templates = Jinja2Templates(directory="templates/")

MT_API_HOST_URL = 'http://localhost:8001/api/v1'
mt_service_url = os.environ.get('MT_API_HOST_URL') or MT_API_HOST_URL

SERVICE_ID = 'translate'
FAKE_GUI_TOKEN = {'client':'GUI', 'token':None} #TODO: register this in a separate table

@app.get("/")
def form_post(request: Request):
    return templates.TemplateResponse('translate.html', context={'request': request, 'text1': '', 'text2': ''})


@app.post("/")
async def form_post(request: Request, message: str = Form(...)):

    translate_service_url = mt_service_url + "/translate"
    
    json_data = {'src':'xx', 
                 'tgt':'xx',
                 'text':message}

    try:
        r = httpx.post(translate_service_url, json=json_data)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)
        return ErrorResponseModel("Internal request error", 503, "Translate service unavailable")

    usage_load = len(message.split())
    await register_usage(FAKE_GUI_TOKEN, SERVICE_ID, usage_load)  #TODO: register this in a separate table (register_gui_usage)

    if r.status_code == 200:
        response = r.json()
        result = response['translation']
    else:
        result = r.json()['detail']

    return templates.TemplateResponse('translate.html', context={'request': request, 'text1': result, 'text2': ''})

