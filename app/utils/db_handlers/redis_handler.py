# redis_handler.py
import redis.asyncio as redis
from typing import Optional, Union, Dict, List
from bson import ObjectId
import time

from app.configs.config import Settings, settings

class RedisHandler:
    instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if (cls.instance is None):
            cls.instance = super(RedisHandler, cls).__new__(cls)
        return cls.instance

    def __init__(self, redis_settings: Settings = settings, db_setting: Optional[Dict[str, str]] = None) -> None:
        host = redis_settings.REDIS_HOST
        port = redis_settings.REDIS_PORT
        password = redis_settings.REDIS_PASSWORD

        if (password is None):
            url = f"redis://{host}:{port}"
        else:
            url = f"redis://:{password}@{host}:{port}"

        if (db_setting is None):
            url += "/0"
        else:
            db_name = db_setting.get("db_name")
            url += f"/{db_name}"

        try:
            self.db_conn = redis.from_url(url, decode_responses=True)
        except Exception as e:
            print(f"RedisHandler Error: {e}")
            return False

        if (db_setting is None):
            self.db_schema = None
        else:
            self.db_schema = db_setting.get("db_schema", None)

    def close(self):
        if (self.db_conn is not None):
            self.db_conn.close()

    def get_redis_conn(self):
        return self.db_conn

    # 친구 활동중 표시
    async def update_friend_activity(self, user_id: str, friend_id: str, ttl_seconds: int):
        try:
            key = f"user_activity:{user_id}"
            score = time.time() + ttl_seconds
            await self.db_conn.zadd(key, {friend_id: score})
        except Exception as e:
            print(f"RedisHandler Update Friend Activity Error: {e}")
            return False

    # 활동 중인 친구 목록 불러오기
    async def get_active_friends(self, user_id: str) -> Union[List[str], bool]:
        try:
            key = f"user_activity:{user_id}"
            current_time = time.time()
            active_friends = await self.db_conn.zrangebyscore(key, min=current_time, max='+inf')
            return active_friends
        except Exception as e:
            print(f"RedisHandler Get Active Friends Error: {e}")
            return False

    # 활동중이지 않은 친구 처리
    async def logout_inactive_friends(self, user_id: str) -> bool:
        try:
            key = f"user_activity:{user_id}"
            current_time = time.time()
            await self.db_conn.zremrangebyscore(key, min='-inf', max=current_time)
            return True
        except Exception as e:
            print(f"RedisHandler Logout Inactive Friends Error: {e}")
            return False

    # Create => insert
    async def insert(self,
                     documents: Union[Dict[Union[str, ObjectId], str], list[Dict[Union[str, ObjectId], int]]]) -> bool:
        try:
            if (type(documents) is dict):
                if (self.db_schema is not None):
                    temp_data = self.db_schema(**documents)
                    data = temp_data.dict(by_alias=True)
                else:
                    data = documents

                key = data.get("_id")
                value: dict = data

                if (await self.db_conn.exists(key)):
                    raise ValueError("Already Existing Value")

                result = await self.db_conn.hmset(key, value)

                if (result == 1):
                    return True
                else:
                    raise ValueError("Already Existing Value")

            elif (type(documents) is list):
                if (self.db_schema is not None):
                    data_list = []
                    for elem in documents:
                        temp_data = self.db_schema(**elem)
                        data = temp_data.dict(by_alias=True)
                        data_list.append(data)
                else:
                    data_list = documents

                pipeline = self.db_conn.pipeline()
                for elem in data_list:
                    key = elem.get("_id")
                    pipeline.exists(key)
                result = await pipeline.execute()

                check = True
                for elem in result:
                    check = check and elem
                if (not check):
                    raise ValueError("Already Existing Value")

                for elem in data_list:
                    key = elem.get("_id")
                    value: dict = elem
                    pipeline.hmset(key, mapping=value)

                result = await pipeline.execute()

                result_status = True
                for elem in result:
                    result_status = result_status and elem

                if (result_status):
                    return True
                else:
                    raise ValueError("Already Existing Value")

        except Exception as e:
            print(f"RedisHandler Insert Error: {e}")
            return False

    # Read => select
    async def select(self,
                     keys: Union[Union[str, ObjectId], List[str]],
                     projection: Optional[Dict[str, int]] = None) -> Union[Dict, List[Dict], bool]:
        try:
            if (type(keys) is str or type(keys) is ObjectId):
                if (projection is None):
                    result = await self.db_conn.hgetall(keys)

                    if (result is None):
                        raise ValueError("Cannot find data from collection")
                    return result
                else:
                    projection_list = list(projection.keys())
                    result = await self.db_conn.hmget(keys, *projection_list)
                    if (result is None):
                        raise ValueError("Cannot find data from collection")

                    result_dict = {'_id': keys}
                    for i in range(projection_list):
                        result_dict[projection_list[i]] = result[i]
                    return result_dict

            elif (type(keys) is list):
                pipeline = self.db_conn.pipeline()
                if (projection is None):
                    for key in keys:
                        pipeline.hgetall(key)

                    result = await pipeline.execute()
                    return result
                else:
                    projection_list = list(projection.keys())
                    for key in keys:
                        pipeline.hmget(key, *projection_list)
                    result = await pipeline.execute()
                    result_list = []
                    for idx1 in range(result):
                        result_dict = {'_id', keys[idx1]}
                        for idx2 in range(projection_list):
                            result_dict[projection_list[idx2]] = result[idx1][idx2]
                        result_list.append(result_dict)

                    return result_list

        except Exception as e:
            print(f"MongoDBHandler Select Error: {e}")
            return False

    # update => update
    async def update(self,
                     keys: Union[Union[str, ObjectId], List[str]],
                     update: Dict = None) -> bool:
        try:
            if (type(keys) is str or type(keys) is ObjectId):
                if (await self.db_conn.exists(keys)):
                    result = await self.db_conn.hmset(name=keys, mapping=update)
                    if (result == 0):
                        return True
                    else:
                        raise ValueError("Cannot find data from collection")
                else:
                    raise ValueError("Cannot find data from collection")
            elif (type(keys) is list):
                pipeline = self.db_conn.pipeline()
                for key in keys:
                    pipeline.exists(key)
                check_result = await pipeline.execute()
                check = True
                for elem in check_result:
                    check = check and elem
                if (not check):
                    raise ValueError("Already Existing Value")

                for key in keys:
                    pipeline.hmset(name=key, mapping=update)
                result = await pipeline.execute()

                check = False
                for elem in result:
                    check = check or bool(elem)

                if (check):
                    raise ValueError("Already Existing Value")
                else:
                    return True

        except Exception as e:
            print(f"RedisHandler Update Error: {e}")
            return False

    # Delete => delete
    async def delete(self, keys: Union[Union[str, ObjectId], List[str]]) -> Union[int, bool]:
        try:
            if (type(keys) is str or type(keys) is ObjectId):
                result = await self.db_conn.delete(keys)
                return result
            else:
                pipeline = self.db_conn.pipeline()
                for key in keys:
                    pipeline.delete(key)
                result_list = await pipeline.execute()

                result = 0
                for elem in result_list:
                    result += elem
                return result

        except Exception as e:
            print(f"RedisHandler Delete Error: {e}")
            return False

    # 로그아웃시 사용자 세션 삭제
    async def delete_session(self, session_id: str) -> bool:
        try:
            result = await self.db_conn.delete(session_id)
            if result == 0:
                raise ValueError(f"Session with ID {session_id} not found.")
            return True
        except Exception as e:
            print(f"RedisHandler Delete Session Error: {e}")
            return False
