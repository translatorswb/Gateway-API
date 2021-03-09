from fastapi import FastAPI, Depends
from passlib.context import CryptContext
import os
from datetime import datetime

from app.api.auth.jwt_bearer import JWTBearer
from app.api.routes.client import router as ClientRouter
from app.api.routes.admin import router as AdminRouter
from app.api.routes.token import router as TokenRouter
from app.api.routes.usage import router as UsageRouter
from app.api.routes.translate import router as TranslateRouter
from app.gui.translateGUI import app as TranslateGUI

from app.api.database.database import add_admin, check_superadmin, add_client

ROOT_PATH = '/' + os.environ.get('PROXY_PREFIX') if os.environ.get('PROXY_PREFIX') else None

app = FastAPI(title="Gamayun API",
    		  description="API gateway for TWB's language technology services",
              version="0.9", 
              root_path=ROOT_PATH, 
              redoc_url="/redoc", openapi_url="/openapi.json", docs_url="/docs")

token_listener = JWTBearer()
hash_helper = CryptContext(schemes=["bcrypt"])

#Add initial superadmin
init_admin_name = os.environ.get('INIT_ADMIN_NAME') or "superadmin"
init_admin_pass = os.environ.get('INIT_ADMIN_PASS') or "test123"

init_admin = {"name": init_admin_name, "password": init_admin_pass, "email": None}
init_gui_client = {"name":"GUI", "email":None, "active_token":None, "token_history":[], "signup":datetime.now()}

@app.on_event("startup")
async def startup():
	init_superadmin = await add_admin(init_admin)
	if init_superadmin:
		print("Superadmin registered.")
	else:
		print("Superadmin already registered.")

	gui_client = await add_client(init_gui_client)
	if gui_client:
		print("GUI client registered.")
	else:
		print("GUI client already registered.")


# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(ClientRouter, tags=["Clients"], prefix="/client", dependencies=[Depends(token_listener)])
app.include_router(TokenRouter, tags=["Tokens"], prefix="/token", dependencies=[Depends(token_listener)])
app.include_router(UsageRouter, tags=["Usage"], prefix="/usage", dependencies=[Depends(token_listener)])
app.include_router(TranslateRouter, tags=["Translate"], prefix="/v1/translate")
app.include_router(TranslateGUI, tags=["Translate GUI"], prefix='/mt')
