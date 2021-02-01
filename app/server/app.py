from fastapi import FastAPI, Depends
from passlib.context import CryptContext

from .auth.jwt_bearer import JWTBearer
from .routes.client import router as ClientRouter
from .routes.admin import router as AdminRouter
from .routes.token import router as TokenRouter
from .routes.translate import router as TranslateRouter

from .database.database import add_admin, check_superadmin

app = FastAPI()

token_listener = JWTBearer()
hash_helper = CryptContext(schemes=["bcrypt"])

init_admin = {"name": "superadmin", "password": "test123"}

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


app.include_router(AdminRouter, tags=["Administrator"], prefix="/api/v1/admin")
app.include_router(ClientRouter, tags=["Clients"], prefix="/api/v1/client", dependencies=[Depends(token_listener)])
app.include_router(TokenRouter, tags=["Tokens"], prefix="/api/v1/token", dependencies=[Depends(token_listener)])
app.include_router(TranslateRouter, tags=["Translate"], prefix="/api/v1/translate")
