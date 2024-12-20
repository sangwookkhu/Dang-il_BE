from pymongo import MongoClient

from app.configs.config import settings, Settings

def set_mongodb_ttl(idx, expire_time, db_settings:dict, mongodb_settings:Settings=settings):
    host = mongodb_settings.MONGODB_HOST
    port = mongodb_settings.MONGODB_PORT
    user = mongodb_settings.MONGODB_USER
    password = mongodb_settings.MONGODB_PASSWORD
    
    if(user is None or password is None):
        url = f'mongodb://{host}:{port}'
    else:
        url = f'mongodb://{user}:{password}@{host}:{port}'
    client = MongoClient(url)
    collection = client[db_settings.get("db_name")][db_settings.get("coll_name")]
    collection.create_index(idx, expireAfterSeconds = expire_time)
