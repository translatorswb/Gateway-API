from fastapi import FastAPI, Depends
from passlib.context import CryptContext
import os

from .auth.jwt_bearer import JWTBearer
from .routes.client import router as ClientRouter
from .routes.admin import router as AdminRouter
from .routes.token import router as TokenRouter
from .routes.translate import router as TranslateRouter

from .database.database import add_admin, check_superadmin

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

init_admin = {"name": init_admin_name, "password": init_admin_pass}

@app.on_event("startup")
async def startup():
	init_superadmin = await add_admin(init_admin)
	if init_superadmin:
		print("Superadmin registered.")
	else:
		print("Superadmin already registered.")


# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


app.include_router(AdminRouter, tags=["Administrator"], prefix="/admin")
app.include_router(ClientRouter, tags=["Clients"], prefix="/client", dependencies=[Depends(token_listener)])
app.include_router(TokenRouter, tags=["Tokens"], prefix="/token", dependencies=[Depends(token_listener)])
app.include_router(TranslateRouter, tags=["Translate"], prefix="/v1/translate")
