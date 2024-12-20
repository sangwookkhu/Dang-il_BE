# app/utils/db_handlers/mongodb_handler.py

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Union, Dict, List
from bson import ObjectId

from app.configs.config import Settings, settings

class MongoDBHandler:
    # 싱글톤 객체로 운용되는 db 연결 -> 포트, 
    instance = None
    db_conn = None

    # 컬렉션 연결용 init
    def __init__(self, mongodb_settings:Settings=settings, db_settings:Optional[Dict[str,str]]=None)->None:
        self.db_coll = None
        self.db_schema = None

        if(MongoDBHandler.db_conn is None):    
            host = mongodb_settings.MONGODB_HOST
            port = mongodb_settings.MONGODB_PORT
            user = mongodb_settings.MONGODB_USER
            password = mongodb_settings.MONGODB_PASSWORD

            if(user is None or password is None):
                url = f'mongodb://{host}:{port}'
            else:
                url = f'mongodb://{user}:{password}@{host}:{port}/?authSource=admin'

            MongoDBHandler.db_conn = AsyncIOMotorClient(url)

        if(db_settings is not None):
            db_name = db_settings.get("db_name", None)
            coll_name = db_settings.get("coll_name", None)
            db_schema = db_settings.get("db_schema", None)

            if(db_name is None or coll_name is None):
                raise

            try:
                db = MongoDBHandler.db_conn[db_name]
                self.db_coll = db[coll_name]
                self.db_schema = db_schema
            except Exception as e:
                print(f"MongoDBHandler Error: {e}")

    # 연결 해제         
    def close(self):
        if(MongoDBHandler.db_conn is not None):
            MongoDBHandler.db_conn.close()

    # collection 연결 가져오기
    def get_collection_conn(self):
        return self.db_coll

    # Create => insert
    async def insert(self, documents:Union[Dict[str, str], list[Dict[str, str]]])->Union[ObjectId, List[ObjectId], bool]:
        try:
            # 하나의 객체만 삽입 -> ObjectId 반환
            if(type(documents) is dict):
                # 유효성 검사, 안되면 오류
                if(self.db_schema is not None):
                    temp_data = self.db_schema(**documents)
                    data = temp_data.dict(by_alias=True, exclude_none=True)
                else:
                    data = documents

                result = await self.db_coll.insert_one(data)
                return result.inserted_id
            # 여러 객체 삽입 -> ObjectId 배열 반환
            elif(type(documents) is list):
                # 유효성 검사, 안되면 오류
                if(self.db_schema is not None):
                    data_list = []
                    for elem in documents:
                        temp_data = self.db_schema(**elem)
                        data = temp_data.dict(by_alias=True, exclude_none=True)
                        data_list.append(data)
                else:
                    data_list = documents

                result = await self.db_coll.insert_many(data_list)
                result_list = list(result.inserted_ids)
                return result_list
        # 오류는 False 반환
        except Exception as e:
            print(f"MongoDBHandler Insert Error: {e}")
            return False

    # Read => select
    async def select(self, 
                     filter:Dict={},
                     projection:Optional[Dict[str, int]]=None)->Union[Dict, List[Dict], bool]:
        try:
            # _id 기준으로 검색 시 1개 반환, dict
            if(filter.get("_id", None) is not None):
                result = await self.db_coll.find_one(filter, projection)
                # 없으면 오류 반환
                if(result is None):
                    raise ValueError("Cannot find data from collection")
                return result
            # 여러개 반환, dict 배열
            else:
                cursor = self.db_coll.find(filter, projection)

                result_list = []
                async for document in cursor:
                    result_list.append(document)
                    
                # 없으면 오류 반환
                if(result_list == []):
                    raise ValueError("Cannot find data from collection")

                return result_list

        # 오류는 False 반환
        except Exception as e:
            print(f"MongoDBHandler Select Error: {e}")
            return False

    # Update => update
    async def update(self, 
                     filter:Dict={},
                     update:Dict=None)->Union[int, bool]:
        try:
            # 기존 update 메소드는 주로 필드 업데이트에 사용됩니다.
            # 여기서는 기존 _id를 새 _id로 변경하는 로직을 추가합니다.

            if "_id" in filter and "_id" in update:
                old_id = filter["_id"]
                new_id = update["_id"]
                
                # 새 문서 생성
                existing_document = await self.db_coll.find_one({"_id": old_id})
                if existing_document is None:
                    raise ValueError("Cannot find data from collection")
                
                existing_document["_id"] = new_id
                await self.db_coll.insert_one(existing_document)
                
                # 기존 문서 삭제
                result = await self.db_coll.delete_one({"_id": old_id})
                return result.deleted_count

            # _id 기준으로 검색 시 1개 수정, dict
            if(filter.get("_id", None) is not None):
                result = await self.db_coll.update_one(filter, update)
            # 여러 개 수정
            else:
                result = await self.db_coll.update_many(filter, update)

            updated_count = result.modified_count
            if(updated_count == 0):
                raise ValueError("Cannot find data from collection")
            return updated_count    

        # 오류는 False 반환
        except Exception as e:
            print(f"MongoDBHandler Update Error: {e}")
            return False

    # Delete => delete
    async def delete(self, filter:Dict={}) -> Union[int, bool]:
        try:
            # _id 기준으로 검색 시 1개 삭제, dict
            if(filter.get("_id", None) is not None):
                result = await self.db_coll.delete_one(filter)
            else:
                result = await self.db_coll.delete_many(filter)

            deleted_count = result.deleted_count
            if(deleted_count == 0):
                raise ValueError("Cannot find data from collection")
            return deleted_count

        # 오류는 False 반환
        except Exception as e:
            print(f"MongoDBHandler Delete Error: {e}")
            return False

    # 로그아웃시 사용자 session 삭제
    async def delete_user_session(self, user_id: str) -> Union[int, bool]:
        try:
            result = await self.db_coll.delete_one({"user_id": user_id})
            deleted_count = result.deleted_count
            if deleted_count == 0:
                raise ValueError("no user_id by given session_id")
            return deleted_count

        except Exception as e:
            print(f"MongoDBHandler Delete User Session Error: {e}")
            return False
