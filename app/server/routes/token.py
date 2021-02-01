from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.server.database.database import *
from app.server.models.models import TokenModel, GenerateTokenModel, RevokeTokenModel, ResponseModel, ErrorResponseModel

import secrets

router = APIRouter()

@router.get("/", response_description="Tokens retrieved")
async def see_tokens():
    tokens = await retrieve_tokens()
    return ResponseModel(tokens, "Token list retrieved successfully") \
        if len(tokens) > 0 \
        else ResponseModel(tokens, "Empty list returned")

@router.post("/", response_description="Token generated")
async def new_token(token_request: GenerateTokenModel = Body(...)):
    token_dict = {"client":token_request.client, "token":secrets.token_urlsafe(), "expiry":token_request.expiry}

    token_data = await generate_token(token_dict)
    if token_data:
        return ResponseModel(token_data, "Token added successfully.")
    else:
        return ErrorResponseModel("Token not generated", 404,"Client doesn't exist: %s"%token_request.client)

@router.delete("/", response_description="Token revoked")
async def revoke_client_token(revoke_token_request: RevokeTokenModel = Body(...)):
    revoked_token, status = await revoke_token(revoke_token_request.client)
    if revoked_token:
        return ResponseModel(revoked_token, "Token revoked successfully.")
    else:
        return ErrorResponseModel("Token not revoked", 404, status['detail'])