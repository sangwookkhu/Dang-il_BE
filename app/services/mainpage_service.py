# libralies
from typing import Optional
from asyncio import create_task, gather
# dto
from app.schemas.service_dto.mainpage_dto import (
    MainpageGetInitialPageInput as GetInitialPageInput,
    MainpageGetInitialPageOutput as GetInitialPageOutput,
)
# 기타 사용자 모듈
from app.configs.config import settings
from app.services.abs_service import AbsService
from app.deps import get_user_coll, get_user_space_coll, get_user_tasking_time_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler


# 친구 id 파트에서 오류가 날 것 같음(확인 필요)
class MainpageService(AbsService):
    instance: Optional["MainpageService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "MainpageService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    # 이거 변수명 리팩토링해야함!
    @staticmethod
    async def get_initial_page(input: GetInitialPageInput,
                               user_coll: MongoDBHandler=get_user_coll(),
                               user_space_coll: MongoDBHandler=get_user_space_coll(),
                               user_taskingtime_coll: MongoDBHandler=get_user_tasking_time_coll())->GetInitialPageOutput:
        # 유저 데이터 받기
        user_data = input.user_data
        user_id = user_data.get("_id")
        # 친구, 모르는 사람 데이터 기본값 설정
        friend_data = []
        unknown_user_data = []
        
        # 전체 반환할 값 개수 설정(전체 = 본인+친구+모르는사람)
        total_data_count = 18
        friend_data_count = 0
        
        # friend_list에 친구 있는지 확인 후 있으면 친구 데이터 받기
        friend_list = user_data.get("friend_list")
        if(friend_list is not None and friend_list != []):
            friend_task_list = [create_task(user_coll.select({"_id": id})) for id in friend_list]
            friend_data_count += len(friend_list)
            print("친구데이터 카운트", len(friend_task_list))

        # 전체 - 본인(1)- 친구가 1 이상이면 모르는 사람 무작위로 불러옴
        unknown_data_count = total_data_count-1-friend_data_count
        if(unknown_data_count > 0):
            if(friend_list is not None and friend_list != []):
                pipeline_criteria = [
                    {"$match": {"_id": {"$nin": friend_list+[user_id]}}},
                    {"$sample":{"size": unknown_data_count}}
                ]
            else:
                pipeline_criteria = [
                    {"$match": {"_id": {"$nin": [user_id]}}},
                    {"$sample":{"size": unknown_data_count}}
                ]
            user_coll_conn = user_coll.get_collection_conn()
            unknown_user_cursor = user_coll_conn.aggregate(pipeline_criteria)
        
        # 내 id, 친구 id, 모르는 사람 id로 공간, 작업시간 데이터 받기
        user_space_data, user_tasking_time_data = None, None
        friend_space_data, unknown_user_space_data, friend_tasking_time_data, unknown_tasking_time_data = [], [], [], []
        if((friend_list is not None and friend_list != [])
           and unknown_data_count > 0): # 친구 O, 모르는 O
            friend_data = await gather(*friend_task_list)
            print("친구데이터", friend_data)
            unknown_user_data = await unknown_user_cursor.to_list(length=None)
            # 모두 id들어있는 리스트로 변환
            friend_id_list = [{"_id": elem} for elem in friend_list]
            unknown_user_list = [{"_id": elem.get("_id")} for elem in unknown_user_data]

            # 공간 정보 받아오기 작업
            user_space_task = create_task(user_space_coll.select({"_id": user_id}))
            friend_space_task_list = [create_task(user_space_coll.select(elem)) for elem in friend_id_list]
            unknown_space_task_list = [create_task(user_space_coll.select(elem)) for elem in unknown_user_list]
            print("친구아이디리스트", friend_id_list)
            print(len(friend_space_task_list))
            # 작업 시간 정보 받아오기 작업
            user_tasking_time_task = create_task(user_taskingtime_coll.select({"_id": user_id}))
            friend_tasking_time_task = [create_task(user_taskingtime_coll.select(elem)) for elem in friend_id_list]
            unknown_tasking_time_task = [create_task(user_taskingtime_coll.select(elem)) for elem in unknown_user_list]
            
            # 작업 결과 매핑    
            user_space_data = await user_space_task
            friend_space_data = await gather(*friend_space_task_list)
            unknown_user_space_data = await gather(*unknown_space_task_list)
            user_tasking_time_data = await user_tasking_time_task
            friend_tasking_time_data = await gather(*friend_tasking_time_task)
            unknown_tasking_time_data = await gather(*unknown_tasking_time_task)
        elif((friend_list is not None and friend_list != []) and 
             unknown_data_count <= 0): # 친구는 O, 모르는 사람 X
            friend_data = await gather(*friend_task_list)
            # 모두 id 들어있는 리스트로 변환
            friend_id_list = [{"_id": elem} for elem in friend_list]
            
            # 공간 정보 받아오기
            user_space_task = create_task(user_space_coll.select({"_id": user_id}))
            friend_space_task_list = [create_task(user_space_coll.select(elem)) for elem in friend_id_list]
        
            # 작업 시간 정보 받아오기
            user_tasking_time_task = create_task(user_taskingtime_coll.select({"_id": user_id}))
            friend_tasking_time_task = [create_task(user_taskingtime_coll.select(elem)) for elem in friend_id_list]

            # 작업 결과 매핑  
            user_space_data = await user_space_task
            friend_space_data = await gather(*friend_space_task_list)
            user_tasking_time_data = await user_taskingtime_task
            friend_tasking_time_data = await gather(*friend_tasking_time_task)
        else: # 친구 X, 모르는 사람 X
            unknown_user_data = await unknown_user_cursor.to_list(length=None)
            unknown_user_list = [{"_id": elem.get("_id")} for elem in unknown_user_data]
            
            # 공간 정보 받아오기
            user_space_task = create_task(user_space_coll.select({"_id": user_id}))
            unknown_space_task_list = [create_task(user_space_coll.select(elem)) for elem in unknown_user_list]
            # 작업 시간 정보 받아오기
            user_taskingtime_task = create_task(user_taskingtime_coll.select({"_id": user_id}))
            unknown_taskingtime_task = [create_task(user_taskingtime_coll.select(elem)) for elem in unknown_user_list]
            
            # 작업 결과 매핑
            user_space_data = await user_space_task
            unknown_user_space_data = await gather(*unknown_space_task_list)
            user_tasking_time_data = await user_taskingtime_task
            unknown_tasking_time_data = await gather(*unknown_taskingtime_task)
        
        return GetInitialPageOutput(
            user_data={
                "my_data": user_data,
                "friend_data": friend_data,
                "unknown_user_data": unknown_user_data
            },
            user_space_data={
                "my_space_data": user_space_data,
                "friend_space_data": friend_space_data,
                "unknown_space_data": unknown_user_space_data
            },
            user_tasking_time_data={
                "my_tasking_time_data": user_tasking_time_data,
                "friend_tasking_time" : friend_tasking_time_data,
                "unknown_tasking_time_data": unknown_tasking_time_data
            }
        )
            
def get_mainpage_service():
    return MainpageService.get_instance()