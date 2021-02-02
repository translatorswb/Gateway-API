export secret="jwt_secret"
export PYTHONPATH=$PWD
export  MONGO_DETAILS="mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb"
#uvicorn server.app:app --reload --host 0.0.0.0 --port 8000
python app/main.py