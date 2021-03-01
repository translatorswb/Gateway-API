from fastapi import APIRouter, Body, HTTPException
from app.api.database.database import query_usage
from app.api.models.models import ErrorResponseModel, ResponseModel

router = APIRouter()

SERVICES_LIST = ['translate']  #TODO: read from environment

@router.get("/{service_name}", response_description="Usage retrieved")
async def see_usage_for_service_client(service_name: str):
    if service_name in SERVICES_LIST:
        usage_query, status = await query_usage(service_name)
        return ResponseModel(usage_query, "Usage data retrieved successfully") \
            if usage_query \
            else ErrorResponseModel("Usage not retrieved", 404, status['detail'])
    else:
        return ErrorResponseModel("Usage not retrieved", 404, "Service does not exist: %s"%service_name)

@router.get("/{service_name}/{client_name}", response_description="Usage retrieved")
async def see_usage_for_service_client(service_name: str, client_name: str):
    if service_name in SERVICES_LIST:
        usage_query, status = await query_usage(service_name, client_name)
        return ResponseModel(usage_query, "Usage data retrieved successfully") \
            if usage_query \
            else ErrorResponseModel("Usage not retrieved", 404, status['detail'])
    else:
        return ErrorResponseModel("Usage not retrieved", 404, "Service does not exist: %s"%service_name)

@router.get("/{service_name}/{client_name}/{year}", response_description="Usage retrieved")
async def see_usage_for_service_client_year(service_name: str, client_name: str, year: int):
    if service_name in SERVICES_LIST:
        usage_query, status = await query_usage(service_name, client_name, year)
        return ResponseModel(usage_query, "Usage data retrieved successfully") \
            if usage_query \
            else ErrorResponseModel("Usage not retrieved", 404, status['detail'])
    else:
        return ErrorResponseModel("Usage not retrieved", 404, "Service does not exist: %s"%service_name)

@router.get("/{service_name}/{client_name}/{year}/{month}", response_description="Usage retrieved")
async def see_usage_for_service_client_year(service_name: str, client_name: str, year: int, month: int):
    if service_name in SERVICES_LIST:
        usage_query, status = await query_usage(service_name, client_name, year, month)
        return ResponseModel(usage_query, "Usage data retrieved successfully") \
            if usage_query \
            else ErrorResponseModel("Usage not retrieved", 404, status['detail'])
    else:
        return ErrorResponseModel("Usage not retrieved", 404, "Service does not exist: %s"%service_name)
