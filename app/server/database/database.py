import motor.motor_asyncio
from bson import ObjectId
from decouple import config
from passlib.context import CryptContext
from fastapi import HTTPException

from app.server.database.database_helper import client_helper, admin_helper, token_helper

MONGO_DETAILS = config('MONGO_DETAILS')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

hash_helper = CryptContext(schemes=["bcrypt"])

database = client.gamayunapi

client_collection = database.get_collection('clients')
admin_collection = database.get_collection('admins')
token_collection = database.get_collection('tokens')

#Admin operations
async def check_superadmin():
    admin = await admin_collection.find_one({'name': 'superadmin'})
    if admin:
        return True
    return False

async def change_admin_password(name: str, new_password: str):
    admin = await admin_collection.find_one({"name": name})
    if admin:
        new_password_hash = hash_helper.encrypt(new_password)
        admin_collection.update_one({"name": name}, {'$set': {'password':new_password_hash}})
        return True
    return False

async def add_admin(admin_data: dict) -> dict:
    admin = await admin_collection.find_one({"name": admin_data['name']})
    if not admin:
        admin_data['password'] = hash_helper.encrypt(admin_data['password'])
        admin = await admin_collection.insert_one(admin_data)
        new_admin = await admin_collection.find_one({"_id": admin.inserted_id})
        return admin_helper(new_admin)
    return False

#Client operations

async def retrieve_clients():
    clients = []
    async for client in client_collection.find():
        clients.append(client_helper(client))
    return clients


async def add_client(client_data: dict) -> dict:
    client = await client_collection.find_one({"name": client_data['name']})
    if not client:
        client = await client_collection.insert_one(client_data)
        new_client = await client_collection.find_one({"_id": client.inserted_id})
        return client_helper(new_client)
    else:
        return False


# async def retrieve_client(id: str) -> dict:
#     client = await client_collection.find_one({"_id": ObjectId(id)})
#     if client:
#         return client_helper(client)
#     else:
#         return False


# async def delete_client(id: str):
#     client = await client_collection.find_one({"_id": ObjectId(id)})
#     if client:
#         await client_collection.delete_one({"_id": ObjectId(id)})
#         return True


# async def update_client_data(id: str, data: dict):
#     client = await client_collection.find_one({"_id": ObjectId(id)})
#     if client:
#         client_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
#         return True

#Token operations

async def retrieve_tokens():
    tokens = []
    async for token in token_collection.find():
        tokens.append(token_helper(token))
    return tokens

async def generate_token(token_data: dict) -> dict:
    client = await client_collection.find_one({"name": token_data['client']})
    if client:
        client_deactivation = await deactivate_client_token(token_data['client'])
        if client_deactivation:
            existing_token = await token_collection.find_one({"token": client['active_token']})
            token_collection.update_one({"token": existing_token['token']}, {"$set": {"active":False}})
        
        #make new token with expiry date
        token_data['active']=True
        token = await token_collection.insert_one(token_data)
        new_token = await token_collection.find_one({"_id": token.inserted_id})

        #add token reference as active token to user
        client_collection.update_one({"name": token_data['client']}, {"$set": {"active_token":token_data["token"]}})
        return token_helper(new_token)
    else:
        return False

async def check_token(tokenstr:str):
    #check if token exists and return user
    token = await token_collection.find_one({"token": tokenstr})
    if token:
        if token['active']:
            print("active token")
            return token_helper(token)
        else:
            print("token not active")
    else:
        #Token not found. 
        print("token not found")
        return 0

async def deactivate_token(tokenstr:str):
    token = await token_collection.find_one({"token": tokenstr})
    if token:
        if token['active']:
            token_collection.update_one({"token": tokenstr}, {"$set": {"active":False}})
            token = await token_collection.find_one({"token": tokenstr})
            return token_helper(token), {'detail': 'Success'}
        else:
            return False, {'detail': 'Token already deactivated'}
    else:
        #Token not found. 
        return False, {'detail': 'Token not found'}

#Deactivate client token. 
async def deactivate_client_token(clientname:str):
    print("deactivate_client_token %s"%clientname)
    client = await client_collection.find_one({"name": clientname})
    #print(client['active_token'])
    if client and client['active_token']:
        dump_token = client['active_token']
        print(dump_token)
        client_collection.update_one({"name": client['name']}, {"$set": {"active_token": None, "token_history":client['token_history'] + [dump_token]}})
        print(dump_token)
        return dump_token
    else:
        return False


async def revoke_token(clientname:str):
    client = await client_collection.find_one({"name": clientname})
    if client:
        if client['active_token']:
            dump_token = await deactivate_client_token(clientname)
            if dump_token:
                revoked_token, status = await deactivate_token(dump_token)
                if revoked_token:
                    return revoked_token, {'detail': 'Success'}
                else:
                    return False, {'detail': status['detail']}
            else:
                return False, {'detail': "Database error"}
        else:
            return False, {'detail': 'Client has no active token'}
    else:
        return False, {'detail': "Client with that name doesn't exist"}
    