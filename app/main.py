from fastapi import FastAPI
from app.api.AdminGatewayAPI import gateway_admin
from app.api.MTGatewayAPI import gateway_mt

app = FastAPI(openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs")

# @app.on_event("startup")
# async def startup():
#     await database.connect()

# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()

app.include_router(gateway_admin, prefix='/api/v1/admin')
app.include_router(gateway_mt, prefix='/api/v1/translate')

