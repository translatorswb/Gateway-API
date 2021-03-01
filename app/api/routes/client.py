from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.api.database.database import retrieve_clients, add_client, retrieve_client, delete_client, update_client_data
from app.api.models.models import ClientModel, UpdateClientModel, ResponseModel, ErrorResponseModel

router = APIRouter()

@router.post("/")
async def add_client_data(client: ClientModel = Body(...)):
    new_client = await add_client(jsonable_encoder(client))
    if new_client:
        return ResponseModel(new_client, "Client added successfully.")
    else:
        return ErrorResponseModel("Request error", 404, "Client with name already exists: %s"%client.name)

@router.get("/", response_description="Clients retrieved")
async def get_clients():
    clients = await retrieve_clients()
    return ResponseModel(clients, "Clients data retrieved successfully") \
        if len(clients) > 0 \
        else ResponseModel(clients, "Empty list returned")

@router.get("/{client_name}", response_description="Client data retrieved")
async def get_client_data(client_name:str):
    client = await retrieve_client(client_name)
    return ResponseModel(client, "Client data retrieved successfully") \
        if client \
        else ErrorResponseModel("An error occured.", 404, "Client with name %s doesn't exist"%client_name)

@router.delete("/{client_name}", response_description="Client data deleted from the database")
async def delete_client_data(client_name: str):
    deleted_client = await delete_client(client_name)
    return ResponseModel("Client with name: %s removed"%client_name, "Client deleted successfully") \
        if deleted_client \
        else ErrorResponseModel("An error occured", 404, "Client with name %s doesn't exist"%client_name)

@router.put("/{client_name}")
async def update_client(client_name: str, req: UpdateClientModel = Body(...)):
    updatedict = {a:req.dict()[a] for a in req.dict() if req.dict()[a]}
    updated_client = await update_client_data(client_name, updatedict)
    if updated_client:
        return ResponseModel(updated_client, "Client updated successfully.")
    else:
        return ErrorResponseModel("An error occurred", 404, "There was an error updating the client.")
    
