from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from app.server.database.database import *
from app.server.models.models import ClientModel, ResponseModel, ErrorResponseModel

router = APIRouter()


@router.get("/", response_description="Clients retrieved")
async def get_clients():
    clients = await retrieve_clients()
    return ResponseModel(clients, "Clients data retrieved successfully") \
        if len(clients) > 0 \
        else ResponseModel(clients, "Empty list returned")


# @router.get("/{id}", response_description="Student data retrieved")
# async def get_student_data(id):
#     student = await retrieve_student(id)
#     return ResponseModel(student, "Student data retrieved successfully") \
#         if student \
#         else ErrorResponseModel("An error occured.", 404, "Student doesn'exist.")


@router.post("/")
async def add_client_data(client: ClientModel = Body(...)):
    new_client = await add_client(jsonable_encoder(client))
    if new_client:
        return ResponseModel(new_client, "Client added successfully.")
    else:
        return ErrorResponseModel("Request error", 404, "Client with name already exists: %s"%client.name)


# @router.delete("/{id}", response_description="Student data deleted from the database")
# async def delete_student_data(id: str):
#     deleted_student = await delete_student(id)
#     return ResponseModel("Student with ID: {} removed".format(id), "Student deleted successfully") \
#         if deleted_student \
#         else ErrorResponseModel("An error occured", 404, "Student with id {0} doesn't exist".format(id))


# @router.put("{id}")
# async def update_student(id: str, req: UpdateStudentModel = Body(...)):
#     updated_student = await update_student_data(id, req.dict())
#     return ResponseModel("Student with ID: {} name update is successful".format(id),
#                          "Student name updated successfully") \
#         if updated_student \
#         else ErrorResponseModel("An error occurred", 404, "There was an error updating the student.".format(id))
