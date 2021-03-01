from fastapi import Body, APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from app.api.auth.admin import validate_login
from app.api.auth.jwt_handler import signJWT
from app.api.database.database import add_admin, check_superadmin, change_admin_password, retrieve_admins, update_admin_data, delete_admin
from app.api.models.models import AdminModel, UpdateAdminPasswordModel, ResponseModel, ErrorResponseModel, UpdateAdminModel
from app.api.auth.jwt_bearer import JWTBearer

router = APIRouter()
token_listener = JWTBearer()

hash_helper = CryptContext(schemes=["bcrypt"])

@router.post("/login")
async def admin_login(admin: AdminModel):
    login_ok = await validate_login(admin)
    if login_ok:
        return {
            "name": admin.name,
            "access_token": signJWT(admin.name)["access_token"] #TODO timeout
        }
    #return "Invalid Login Details!" #TODO proper error message
    return ErrorResponseModel("Authentication error", 404, "Invalid Login Details!")


@router.post("/password", dependencies=[Depends(token_listener)])
async def change_admin_pass(admin: UpdateAdminPasswordModel):
    login_ok = await validate_login(admin)
    if login_ok:
        pass_change = await change_admin_password(admin.name, admin.new_password)
        print(pass_change)
        return ResponseModel(data={"name":admin.name}, message="Changed password")
    else:
        return ErrorResponseModel("Authentication error", 404, "Admin with that name/pass cannot be found")

@router.post("/new", dependencies=[Depends(token_listener)])
async def add_new_admin(admin: AdminModel = Body(...)):
    #admin = jsonable_encoder(admin)
    new_admin = await add_admin(jsonable_encoder(admin))
    if new_admin:
        return ResponseModel(new_admin, "Admin added successfully.")
    else:
        #raise HTTPException(status_code=401, detail="Duplicate name: %s"%admin['name'])
        return ErrorResponseModel("Request error", 404, "Duplicate name: %s"%admin.name)

    
@router.get("/", response_description="Admins retrieved")
async def get_admins():
    admins = await retrieve_admins()
    return ResponseModel(admins, "Admins data retrieved successfully") \
        if len(admins) > 0 \
        else ResponseModel(admins, "Empty list returned")

@router.put("/{admin_name}")
async def update_admin(admin_name: str, req: UpdateAdminModel = Body(...)):
    updatedict = {a:req.dict()[a] for a in req.dict() if req.dict()[a]}
    updated_admin = await update_admin_data(admin_name, updatedict)
    if updated_admin:
        return ResponseModel(updated_admin, "Admin updated successfully.")
    else:
        return ErrorResponseModel("An error occurred", 404, "There was an error updating the admin.")
    
@router.delete("/{admin_name}", response_description="Admin data deleted from the database")
async def delete_admin_data(admin_name: str):
    deleted_admin, status = await delete_admin(admin_name)
    return ResponseModel("Admin with name %s removed"%admin_name, "Admin deleted successfully from database") \
        if deleted_admin \
        else ErrorResponseModel("An error occured", 404, status)


