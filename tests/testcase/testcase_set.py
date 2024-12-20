import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from app.deps import get_user_coll, get_session_coll, get_session_cache, get_user_tasking_time_coll, get_user_space_coll
from app.schemas.database_dto.db_schemas import UserColl
from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.utils.db_handlers.redis_handler import RedisHandler
import asyncio
from datetime import datetime, timezone
from typing import Optional
import httpx

class SetTestCase:
    instance: Optional["SetTestCase"] = None
    url: str = "http://localhost:8000"
    user_list = ["test1", "test2", "test3"] + [f"SetUser{i}" for i in range(1,16)] + [f"UnsetUser{i}" for i in range(16, 31)]
    user_coll: MongoDBHandler = get_user_coll()
    session_coll: MongoDBHandler = get_session_coll()
    session_cache: RedisHandler = get_session_cache()
    user_taskingtime_coll: MongoDBHandler = get_user_tasking_time_coll()
    user_space_coll: MongoDBHandler = get_user_space_coll()

    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "SetTestCase":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance

    @classmethod
    async def initialize_users(cls):
        # 유저 세팅
        
        # 유저 삽입 태스크
        user_insert_task = [
            asyncio.create_task(
                cls.user_coll.insert(
                    {
                        "_id": i,
                        "name": i,
                        "email": f"{i}@gmail.com",
                        "tag": i
                    }
                )
            ) 
        for i in cls.user_list]
        # 세션 db 삽입 테스크
        session_coll_task = [
            asyncio.create_task(
                cls.session_coll.insert(
                    {
                        "_id": i,
                        "identifier": i,
                        "created_at": "제한시간 없음"
                    }
                )
            )
        for i in cls.user_list]
        # 세션 캐시 삽입 테스크
        session_cache_task = [
            asyncio.create_task(
                cls.session_cache.insert(
                    {
                        "_id": i,
                        "identifier": i,
                        "created_at": "제한시간 없음"
                    }
                )
            )
        for i in cls.user_list]
        # 유저 공간 초기화 테스크
        user_space_task = [
            asyncio.create_task(
                cls.user_space_coll.insert({"_id": i})
            )
        for i in cls.user_list]
        user_taskingtime_task = [
            asyncio.create_task(
                cls.user_taskingtime_coll.insert({"_id": i})
            )
        for i in cls.user_list]

        await asyncio.gather(*user_insert_task, *session_cache_task, *session_coll_task, *user_space_task, *user_taskingtime_task)

        print("초기화(initialize) 완료")

    @classmethod
    async def set_user_space(cls):
        async with httpx.AsyncClient() as client:
            request_body = {
                    "interior_data": [
                        {"decor_id": "desk1", "location": (1.0, 2.0, 3.0)},
                        {"decor_id": "desk2", "location": (1.0, 2.0, 3.0)}
                    ] 
                }
            user_space_tasks = [
                asyncio.create_task(client.post(f"{cls.url}/space/save", json=request_body, cookies={"session_id": i})) 
                for i in cls.user_list[0:18]
            ]

            await asyncio.gather(*user_space_tasks)

            await client.post(f"{cls.url}/space/save", json=request_body, cookies={"session_id": "test1"})

    @classmethod
    async def set_board(cls):
        async with httpx.AsyncClient() as client:
            request_body = {
                    "memo": {
                        "content": "test입니다",
                        "sender_id": "UnsetUser1",
                        "sender_name": "UnsetUser1"
                    }
                }
            user_space_tasks = [
                asyncio.create_task(client.post(f"{cls.url}/space/board/{i}", json=request_body, cookies={"session_id": "UnsetUser1"})) 
                for i in cls.user_list[0:18]
            ]

            await asyncio.gather(*user_space_tasks)

            await client.post(f"{cls.url}/space/save", json=request_body, cookies={"session_id": "test1"})


if(__name__ == "__main__"):
    test = SetTestCase.get_instance()

    asyncio.run(test.initialize_users())
    asyncio.run(test.set_user_space())
    asyncio.run(test.set_board())
