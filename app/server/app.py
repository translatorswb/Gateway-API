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

app = FastAPI(root_path=ROOT_PATH, redoc_url="/v1/redoc", openapi_url="/v1/openapi.json", docs_url="/v1/docs")

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


app.include_router(AdminRouter, tags=["Administrator"], prefix="/v1/admin")
app.include_router(ClientRouter, tags=["Clients"], prefix="/v1/client", dependencies=[Depends(token_listener)])
app.include_router(TokenRouter, tags=["Tokens"], prefix="/v1/token", dependencies=[Depends(token_listener)])
app.include_router(TranslateRouter, tags=["Translate"], prefix="/v1/translate")
