export MT_API_HOST_URL='http://127.0.0.1:8001/api/v1'
export secret="jwt_secret"
export PYTHONPATH=$PWD
export  MONGO_DETAILS="mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
