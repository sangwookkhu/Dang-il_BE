import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import Request
from fastapi.exceptions import HTTPException
from typing import Optional
from asyncio import create_task, gather

from app.deps import get_user_coll, get_session_cache, get_session_coll

from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.utils.db_handlers.redis_handler import RedisHandler

class SessionMiddleware:
    instance: Optional["SessionMiddleware"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "SessionMiddleware":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    async def session_check(request: Request,
                            user_coll: MongoDBHandler = get_user_coll(),
                            session_coll: MongoDBHandler = get_session_coll(),
                            session_cache: RedisHandler = get_session_cache()):
        
        session_id = request.cookies.get("session_id", None)
        
        # 세션 id 없으면 에러
        if(session_id is None):
            raise HTTPException(status_code=400, detail="Session ID does not exist")
        
        # 세션 id로 유저id받기, 없으면 유효하지 않은 세션id(권한에러 401)
        # 캐시랑 db는 look aside로 처리
        session_cache_check_task = create_task(session_cache.select(session_id))
        session_db_check_task = create_task(session_coll.select({"_id": session_id}))
        
        session_check_result = await session_cache_check_task
        if(session_check_result == False):
            session_check_result = await session_db_check_task
            if(session_check_result == False):
                    raise HTTPException(status_code=401, detail="Invalid session")
        
        # 유저 id로 유저 정보 받고 이를 반환
        user_id = session_check_result.get("identifier")
        user_data = await user_coll.select({"_id": user_id})
        return user_data
        
def get_session_middleware():
    return SessionMiddleware.get_instance()