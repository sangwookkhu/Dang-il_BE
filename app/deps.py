# db 스키마
from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.utils.db_handlers.redis_handler import RedisHandler
from app.utils.etc.server_sent_event import UserQueue
from app.utils.db_handlers.set_mongodb_ttl import set_mongodb_ttl
from app.schemas.database_dto.db_schemas import UserColl, SessionColl, UserSpaceColl, UserTaskingTimeColl, FriendWaitColl, DecorColl, TaskingNoteColl
from fastapi import Request, HTTPException, Depends, status

## 로그아웃 관련
redis_handler = RedisHandler()
mongodb_handler = MongoDBHandler()
def get_current_user(request: Request):
    # 쿠키에서 세션 ID를 가져옴
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session_id")

    # Redis에서 세션 정보를 조회
    user_data = redis_handler.client.get(session_id)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unvalid session")

    # 사용자 데이터를 반환
    user = mongodb_handler.db["sessions"].find_one({"session_id": session_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can't find user")

    return {
        "user_id": user["user_id"],
        "session_id": session_id,
        "auth_provider": user.get("auth_provider"),
        "access_token": user.get("access_token")
    }


# session_coll은 ttl설정
def get_session_coll() -> MongoDBHandler:
    db_settings = {
        "db_name": "artisticsw_db",
        "coll_name": "session_coll",
        "db_schema": SessionColl
    }
    mongodb_instance = MongoDBHandler(db_settings=db_settings)
    
    set_mongodb_ttl([("created_at", 1)], 86400*3, db_settings=db_settings)
    
    return mongodb_instance

def get_user_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "user_coll",
        "db_schema": UserColl
    })

def get_session_cache() -> RedisHandler:
    return RedisHandler(db_setting={
        "db_name": "0",
        "db_schema": SessionColl
    })

def get_user_space_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "user_space_coll",
        "db_schema": UserSpaceColl
    })
    
def get_user_tasking_time_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "user_tasking_time_coll",
        "db_schema": UserTaskingTimeColl
    })

def get_friend_wait_coll() -> MongoDBHandler:
    db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "friend_wait_coll",
        "db_schema": FriendWaitColl
    }
    mongodb_instance = MongoDBHandler(db_settings=db_settings)
    set_mongodb_ttl([("request_date", 1)], 86400*3, db_settings=db_settings)
    
    return mongodb_instance

def get_decor_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "decor_coll",
        "db_schema": DecorColl
    })
    
def get_user_queue():
    user_q = UserQueue()
    return user_q.get_queue()


def get_video_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "video_db",
        "coll_name": "video_coll",
    })

def get_taskingnote_coll() -> MongoDBHandler:
    return MongoDBHandler(db_settings={
        "db_name": "artisticsw_db",
        "coll_name": "tasking_note_coll",
        "db_schema": TaskingNoteColl
    })

# def get_decor_coll() -> MongoDBHandler:
#     return MongoDBHandler(coll_config={"coll_name": "decor_coll"})

# def get_decor_category()->list:
#     return ['desk', 'lamp', 'monitor', 'vase', 'bookshelf', 'frame'] # 현재는 이정도