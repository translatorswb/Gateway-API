from fastapi import APIRouter, Request, File, Form, UploadFile
from fastapi.templating import Jinja2Templates
import httpx
import json
import os

app = APIRouter()

templates = Jinja2Templates(directory="templates/")

ASR_API_HOST_URL = 'http://localhost:8010'
asr_service_url = os.environ.get('ASR_API_HOST_URL') or ASR_API_HOST_URL

SERVICE_ID = 'transcribe'

INIT_LANG = "en"

@app.get("/")
def form_get(request: Request):
	return templates.TemplateResponse('transcribe.html', context={'request': request, 'text1':''})

# @app.post("/")
# async def form_post(request: Request):
# 	form = await request.form()
# 	some_file = form['audioFile']
# 	print(type(some_file))
# 	print(some_file)
# 	return templates.TemplateResponse('transcribe.html', context={'request': request, 'text1':some_file})

@app.post("/")
async def post_upload(imgdata: tuple, file: UploadFile = File(...)):
    print(imgdata)
    data_dict = eval(imgdata[0])
    winWidth, imgWidth, imgHeight = data_dict["winWidth"], data_dict["imgWidth"], data_dict["imgHeight"]

    data = {
        "imgWidth": imgWidth,
        "imgHeight": imgHeight
    }
    return data
