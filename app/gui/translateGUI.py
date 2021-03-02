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

INIT_MESSAGE = ""
INIT_SRC = "fr"
INIT_TGT = "en"

def get_language_info():
    translate_url = mt_service_url + "/translate/languages"

    try:
        r = httpx.get(translate_url)
    except httpx.HTTPError as exc:
        print(f"Error while requesting {exc.request.url!r}.")
        print(exc)

    if r.status_code == 200:
        response = r.json()

        api_languages = response['languages']
        api_models = response['models']
 
    else:
        print("Error retrieving language list")
        print(response['detail'])
        api_languages = {}
        api_models = {}

    return api_languages, api_models


@app.get("/")
def form_get(request: Request):
    api_languages, api_models = get_language_info()

    return templates.TemplateResponse('translate.html', context={'request': request, 'api_languages':api_languages, 'api_models':api_models, 'src':INIT_SRC, 'tgt':INIT_TGT, 'source': INIT_MESSAGE, 'text1': '', 'text2': ''})


@app.post("/")
async def form_post(request: Request):
    form = await request.form()
    message = form['message']
    src = form['src']
    tgt = form['tgt']

    api_languages, api_models = get_language_info()

    if message and tgt in api_models[src]:
        translate_service_url = mt_service_url + "/translate"
        
        json_data = {'src':src, 
                     'tgt':tgt,
                     'text':message}

        print(json_data)

        try:
            r = httpx.post(translate_service_url, json=json_data)

            if r.status_code == 200:
                usage_load = len(message.split())
                await register_usage(FAKE_GUI_TOKEN, SERVICE_ID, usage_load)  #TODO: register this in a separate table (register_gui_usage)

                response = r.json()
                result = response['translation']
            else:
                result = r.json()['detail']
        except httpx.HTTPError as exc:
            print(f"Error while requesting {exc.request.url!r}.")
            print(exc)
            result = 'Translate service not available.'
    else:
        result = ''

    
    return templates.TemplateResponse('translate.html', context={'request': request, 'api_languages':api_languages, 'api_models':api_models, 'src':src, 'tgt':tgt, 'source': message, 'text1': result, 'text2': ''})
