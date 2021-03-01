from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.database.database import retrieve_tokens, generate_token, revoke_token
from app.api.models.models import TokenModel, GenerateTokenModel, RevokeTokenModel, ResponseModel, ErrorResponseModel

import secrets

router = APIRouter()

SERVICES_LIST = ['translate', 'diarization']

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
async def new_token_with_info(client_name: str, token_request: GenerateTokenModel = Body(...)):
    #TODO: Parse expiry date

    #Parse services list
    not_implemented = [s for s in token_request.services if s not in SERVICES_LIST]
    if not_implemented:
        return ErrorResponseModel("Token not generated", 404,"Services not implemented: %s"%not_implemented)

    token_dict = {"client":client_name, "token":secrets.token_urlsafe(), "expiry":token_request.expiry, "services":token_request.services}

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