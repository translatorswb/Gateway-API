import motor.motor_asyncio
from bson import ObjectId
from decouple import config
from passlib.context import CryptContext
from fastapi import HTTPException
from datetime import datetime

from app.api.database.database_helper import client_helper, admin_helper, token_helper

MONGO_DETAILS = config('MONGO_DETAILS')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

hash_helper = CryptContext(schemes=["bcrypt"])

database = client.gamayunapi

client_collection = database.get_collection('clients')
admin_collection = database.get_collection('admins')
token_collection = database.get_collection('tokens')
usage_collection = database.get_collection('usage')

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

async def retrieve_admins():
    admins = []
    async for admin in admin_collection.find():
        admins.append(admin_helper(admin))
    return admins

async def update_admin_data(name: str, data: dict):
    admin = await admin_collection.find_one({"name": name})
    if admin and data:
        admin_collection.update_one({"name": name}, {"$set": data})
        if 'name' in data:
            updated_admin = await admin_collection.find_one({"name": data['name']})
        else:
            updated_admin = await admin_collection.find_one({"name": name})
        return admin_helper(updated_admin)
    else:
        return False

async def delete_admin(admin_name: str):
    admin = await admin_collection.find_one({"name": admin_name})
    if admin:
        no_admins = await admin_collection.count_documents({})
        print("No admins", no_admins)
        if no_admins == 1:
            return False, {'detail': 'Cannot delete only admin'}

        await admin_collection.delete_one({"name": admin_name})

        return True, {'detail': 'Success'} 
    else:
        return False, {'detail': 'Admin not found'}

#Client operations

async def retrieve_clients():
    clients = []
    async for client in client_collection.find():
        clients.append(client_helper(client))
    return clients


async def add_client(client_data: dict) -> dict:
    client = await client_collection.find_one({"name": client_data['name']})
    if not client:
        client_data['signup'] = datetime.now()
        client = await client_collection.insert_one(client_data)
        new_client = await client_collection.find_one({"_id": client.inserted_id})
        return client_helper(new_client)
    else:
        return False

async def delete_client(client_name: str):
    client = await client_collection.find_one({"name": client_name})
    # deactivated_token = None
    if client:
        await client_collection.delete_one({"name": client_name})

        async for token in token_collection.find({'client': client_name}):
            
            token, status = await deactivate_token(token['token'])
            if token:
                # deactivated_token = token['token']
                print("Deactivated a token")

        return True
    else:
        print("Client not found")
        return False


async def retrieve_client(name: str) -> dict:
    client = await client_collection.find_one({"name": name})
    if client:
        return client_helper(client)
    else:
        return False


async def update_client_data(name: str, data: dict):
    print(data)
    client = await client_collection.find_one({"name": name})
    if client and data:
        client_collection.update_one({"name": name}, {"$set": data})
        if 'name' in data:
            updated_client = await client_collection.find_one({"name": data['name']})
        else:
            updated_client = await client_collection.find_one({"name": name})
        return client_helper(updated_client)
    else:
        return False

#Token operations

async def retrieve_tokens(only_active=False):
    tokens = []
    async for token in token_collection.find():
        if only_active:
            if token['active']:
                tokens.append(token_helper(token))
        else:
            tokens.append(token_helper(token))
    return tokens

async def generate_token(token_data: dict) -> dict:
    client = await client_collection.find_one({"name": token_data['client']})
    if client:
        client_deactivation = await deactivate_client_token(token_data['client'])
        if client_deactivation:
            token, status = await deactivate_token(client['active_token'])
        
        #make new token
        token_data['active']=True
        token_data['creation_date'] = datetime.now()
        token_data['toss_date'] = None

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
            token_collection.update_one({"token": tokenstr}, {"$set": {"active":False, "toss_date":datetime.now()}})
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

# Usage operations

MODEL_TAG_SEPARATOR = "-"

def get_model_id(src, tgt, alt_id=None):
    model_id = src + MODEL_TAG_SEPARATOR + tgt
    if alt_id:
        model_id += MODEL_TAG_SEPARATOR + alt_id
    return model_id

async def register_usage(token:dict, service: str, model_info:dict, usage_load:dict) -> dict:
    usage_data = {'client':token['client'], 'token':token['token'], 'date':datetime.now(), 'service':service, 'load':usage_load, 'model':model_info}
    await usage_collection.insert_one(usage_data)

async def query_usage(service: str, client: str = None, year: int = None, month: int = None):
    data_fields = ['load', 'model', 'date', 'token']
    if not client and not year and not month:
        cursor = usage_collection.find({'service': service})
        data_fields = ['client'] + data_fields
    elif not year and not month:
        client_query = await client_collection.find_one({"name": client})
        if not client_query:
            return False, {'detail': "Client with that name doesn't exist"}

        cursor = usage_collection.find({'service': service, 'client':client})
    elif not month:
        try:
            start_limit = datetime(year, 1, 1)
            end_limit = datetime(year+1, 1, 1)
        except ValueError as e:
            return False, {'detail': str(e)}
        cursor = usage_collection.find({'service': service, 'client':client, 'date': {'$lt': end_limit, '$gt': start_limit}})
    else:
        try:
            start_limit = datetime(year, month, 1)
            end_limit = datetime(year, month+1, 1)
        except ValueError as e:
            return False, {'detail': str(e)}
        cursor = usage_collection.find({'service': service, 'client':client, 'date': {'$lt': end_limit, '$gt': start_limit}})

    total = 0
    totals = {}
    usage_list = []
    async for document in cursor:
        total += document['load']
        if 'model' in document:
            model_id = get_model_id(document['model']['src'], document['model']['tgt'])
            if not model_id in totals:
                totals[model_id] = 0
            totals[model_id] += document['load']
        usage_list.append({d:document[d] for d in data_fields if d in document})

    result = {'Total': total, 'Models': totals, 'Details': usage_list}

    return result, {'detail': 'Success'}

    
    