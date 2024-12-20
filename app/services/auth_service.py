# libraries
import datetime
from httpx import AsyncClient
from fastapi.exceptions import HTTPException
from secrets import token_hex
from asyncio import create_task, gather
from typing import Optional

# DTO import
from app.schemas.service_dto.auth_dto import (
    AuthCallbackInput,
    AuthCallbackOutput,
    AuthLoginInput,
    AuthLoginOutput,
    AuthRegisterInput,
    AuthRegisterOutput,
)
from app.schemas.database_dto.db_schemas import UserColl, SessionColl
# 기타 사용자 모듈
from app.configs.config import settings
from app.services.abs_service import AbsService
from app.deps import get_user_coll, get_session_coll, get_session_cache, get_user_space_coll, get_user_tasking_time_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.utils.db_handlers.redis_handler import RedisHandler

class AuthService(AbsService):
    instance: Optional["AuthService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "AuthService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    # 구글 로그인 처리(callback)
    @staticmethod
    async def google_callback(input: AuthCallbackInput) -> AuthCallbackOutput:
        print("구글컬백1")
        async with AsyncClient() as client:
            post_data = {
                "grant_type": "authorization_code",
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "code": input.code,
            }
            print("구글컬백2")
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data=post_data,
            )
            print("구글컬백3")
            token_data = token_response.json()
            print("googlecallback: ", token_data)
            print("tokendataatata, ", token_data.get("access_token"))

            if "error" in token_data:
                raise HTTPException(status_code=400, detail=token_data["error_description"])
            print("구글컬백4")
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
        print("구글컬백5")
        user_data = user_response.json()
        user_data["_id"] = user_data.pop("id")
        user_data["profile_image_url"] = user_data.get("picture") 
        print("구글컬백6user_Data", user_data)
        print("access_tolenㅇ ", token_data.get("access_token"))
        print(type(token_data.get("access_token")))
        return AuthCallbackOutput(**user_data, access_token=token_data.get("access_token"))
    
    # 카카오 로그인 처리(callback)
    @staticmethod
    async def kakao_callback(input: AuthCallbackInput) -> AuthCallbackOutput:
        async with AsyncClient() as client:
            post_data = {
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": input.code,
            }
            token_response = await client.post(
                "https://kauth.kakao.com/oauth/token",
                data=post_data,
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            if "error" in token_data:
                raise HTTPException(status_code=400, detail=token_data["error_description"])

            user_response = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )

        user_response.raise_for_status()
        user_json = user_response.json()
        print("jsoncheck: ", user_json)
        user_data = {
            "_id": str(user_json.get("id")),
            "name": str(user_json.get("properties").get("nickname")),
            "email": str(user_json.get("kakao_account").get("email")),
            "profile_image_url": user_json.get("properties").get("profile_image")
        }
        print("checking: ", user_data)

        return AuthCallbackOutput(**user_data, access_token=token_data.get("access_token"))

    # 사용자 등록 처리
    @staticmethod
    async def register(input: AuthRegisterInput,
                           user_coll: MongoDBHandler=get_user_coll(),
                           user_space_coll: MongoDBHandler = get_user_space_coll(),
                           user_taskingtime_coll: MongoDBHandler = get_user_tasking_time_coll(),
                           session_coll: MongoDBHandler=get_session_coll(),
                           session_cache: RedisHandler=get_session_cache())->AuthRegisterOutput:
        # 사용자 태그 선택
        user_coll_conn = user_coll.get_collection_conn()
        user_tag = (str(await user_coll_conn.count_documents({})).zfill(5))[::-1]

        # user_coll, session_coll, session_cache에 insert
        user_document = UserColl(
            _id = input.id,
            name = input.name,
            email = input.email,
            tag = user_tag,
            profile_image_url = input.profile_image_url 
        )
        session_document = SessionColl(
            _id = token_hex(16),
            identifier = input.id,
            created_at = datetime.datetime.now(datetime.timezone.utc),
            access_token=input.access_token
        )
        session_cache_document = SessionColl(
            _id = session_document.id,
            identifier = input.id,
            created_at = str(session_document.created_at),
            access_token=input.access_token
        )

        user_document_dict = user_document.model_dump(by_alias=True, exclude_none=True)
        session_document_dict = session_document.model_dump(by_alias=True, exclude_none=True)
        session_cache_document_dict = session_cache_document.model_dump(by_alias=True, exclude_none=True)

        user_coll_task = create_task(user_coll.insert(user_document_dict))
        session_coll_task = create_task(session_coll.insert(session_document_dict))
        session_cache_task = create_task(session_cache.insert(session_cache_document_dict))
        await gather(session_coll_task, session_cache_task)
        
        user_id = await user_coll_task

        task1 = create_task(user_space_coll.insert(
            {
                "_id": user_id,
                "interior_data": []
                }
            ))
        task2 = create_task(user_taskingtime_coll.insert(
            {
                "_id": user_id,
                "today_tasking_time": 0
                }
            ))

        await gather(task1, task2)
        
        # 레디스 ttl 만료 설정
        session_cache_id = session_document.id
        ttl = int(datetime.timedelta(days=3).total_seconds())
        session_cache_conn = await session_cache.get_redis_conn()
        await session_cache_conn.expire(session_cache_id, ttl)

        return AuthRegisterOutput(
            session_id = session_document.id,
            expires = (session_document.created_at + datetime.timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            profile_image_url=input.profile_image_url
        )   
    
    # 로그인 처리
    @staticmethod
    async def login(
        input: AuthLoginInput,
        session_coll: MongoDBHandler = get_session_coll(),
        session_cache: RedisHandler = get_session_cache()) -> AuthLoginOutput:
        print("로그인처리1")
        if input.session_id is not None:
            session_delete_task = create_task(session_coll.delete({"_id": input.session_id}))
            session_cache_delete_task = create_task(session_cache.delete(input.session_id))
            await gather(session_delete_task, session_cache_delete_task)
        print("로그인처리2")

        session_exist_check = create_task(session_coll.select({"identifier": input.id}))
        session_cache_exist_check = create_task(session_cache.select({"identifier": input.id}))
        if await session_exist_check != False or await session_cache_exist_check != False:
            session_delete_task = create_task(session_coll.delete({"identifier": input.id}))
            session_cache_delete_task = create_task(session_cache.delete(input.id))
            await gather(session_delete_task, session_cache_delete_task)
        print("로그인처리3")
        session_document = SessionColl(
            _id = token_hex(16),
            identifier = input.id,
            created_at = datetime.datetime.now(datetime.timezone.utc),
            access_token=input.access_token
        )
        session_cache_document = SessionColl(
            _id = session_document.id,
            identifier = input.id,
            created_at = str(session_document.created_at),
            access_token=input.access_token
        )

        session_document_dict = session_document.model_dump(by_alias=True)
        session_cache_document_dict = session_cache_document.model_dump(by_alias=True)

        session_coll_task = create_task(session_coll.insert(session_document_dict))
        session_cache_task = create_task(session_cache.insert(session_cache_document_dict))
        await gather(session_coll_task, session_cache_task)
        print("로그인처리4")
        session_cache_id = session_document.id
        ttl = int(datetime.timedelta(days=3).total_seconds())
        session_cache_conn = await session_cache.get_redis_conn()
        await session_cache_conn.expire(session_cache_id, ttl)
        print("로그인처리5")
        return AuthLoginOutput(
            session_id = session_document.id,
            expires = (session_document.created_at + datetime.timedelta(days=3)).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            profile_image_url=input.profile_image_url
        )

# 의존성 반환
def get_auth_service() -> AuthService:
    return AuthService.get_instance()
