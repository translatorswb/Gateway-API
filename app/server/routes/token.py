from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.server.database.database import *
from app.server.models.models import TokenModel, GenerateTokenWithExpiryModel, RevokeTokenModel, ResponseModel, ErrorResponseModel

import secrets

router = APIRouter()

@router.get("/", response_description="Tokens retrieved")
async def see_tokens():
    tokens = await retrieve_tokens(only_active=False)
    return ResponseModel(tokens, "Token list retrieved successfully") \
        if len(tokens) > 0 \
        else ResponseModel(tokens, "Empty list returned")

@router.get("/active", response_description="Tokens retrieved")
async def see_active_tokens():
    tokens = await retrieve_tokens(only_active=True)
    return ResponseModel(tokens, "Token list retrieved successfully") \
        if len(tokens) > 0 \
        else ResponseModel(tokens, "Empty list returned")

@router.post("/{client_name}", response_description="Token generated")
async def new_token(client_name: str):
    token_dict = {"client":client_name, "token":secrets.token_urlsafe(), "expiry":None}

    token_data = await generate_token(token_dict)
    if token_data:
        return ResponseModel(token_data, "Token added successfully.")
    else:
        return ErrorResponseModel("Token not generated", 404,"Client doesn't exist: %s"%client_name)

@router.post("/{client_name}", response_description="Token generated with expiration")
async def new_token_with_expiry(token_request: GenerateTokenWithExpiryModel = Body(...)):
    #TODO: Parse expiry

    token_dict = {"client":client_name, "token":secrets.token_urlsafe(), "expiry":token_request.expiry}

    token_data = await generate_token(token_dict)
    if token_data:
        return ResponseModel(token_data, "Token added successfully.")
    else:
        return ErrorResponseModel("Token not generated", 404,"Client doesn't exist: %s"%client_name)

@router.delete("/{client_name}", response_description="Token revoked")
async def revoke_client_token(client_name:str):
    revoked_token, status = await revoke_token(client_name)
    if revoked_token:
        return ResponseModel(revoked_token, "Token revoked successfully.")
    else:
        return ErrorResponseModel("Token not revoked", 404, status['detail'])