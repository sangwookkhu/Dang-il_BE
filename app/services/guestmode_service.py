# libralies
from typing import Optional
from asyncio import create_task, gather
# dto
from app.schemas.service_dto.guestmode_dto import (
    GuestmodeGetInitialPageOutput as GetInitialPageOutput,
)
# 기타 사용자 모듈
from app.services.abs_service import AbsService
from app.deps import get_user_coll, get_user_space_coll, get_user_tasking_time_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class GuestmodeService(AbsService):
    instance: Optional["GuestmodeService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "GuestmodeService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    @staticmethod
    async def guestmode_get_initial_page(user_coll: MongoDBHandler=get_user_coll(),
                                         user_space_coll: MongoDBHandler=get_user_space_coll(),
                                         user_tasking_time_coll: MongoDBHandler=get_user_tasking_time_coll())->GetInitialPageOutput:
        # 초기값 세팅
        unknown_user_data = []
        unknown_user_space_data = []
        unknown_tasking_time_data = []
        
        # 전체 반환할 값 개수 설정(전체 = 본인+친구+모르는사람)
        total_data_count = 18
        unknown_data_count = total_data_count -1 

        # 모르는 유저 무작위로 불러오기
        # 무작위로 불러오기
        pipeline_criteria = [{"$sample":{"size": unknown_data_count}}]
        collection = user_coll.get_collection_conn()
        unknown_user_cursor = collection.aggregate(pipeline_criteria)  
        unknown_user_data = await unknown_user_cursor.to_list(length=None)
        # 모르는 유저 id 모음
        unknown_user_list = [{"_id": elem.get("_id")} for elem in unknown_user_data]
        
        # 공간, 시간 정보 받기
        unknown_space_task_list = [create_task(user_space_coll.select(elem)) for elem in unknown_user_list]
        unknown_tasking_task_list = [create_task(user_tasking_time_coll.select(elem)) for elem in unknown_user_list]
        unknown_user_space_data = await gather(*unknown_space_task_list)
        unknown_tasking_time_data = await gather(*unknown_tasking_task_list)
        
        return GetInitialPageOutput(
            user_data={
                "unknown_user_data": unknown_user_data
            },
            user_space_data={
                "unknown_space_data": unknown_user_space_data
            },
            user_tasking_time_data={
                "unknown_tasking_time_data": unknown_tasking_time_data
            }
        )
        

def get_guestmode_service():
    return GuestmodeService.get_instance()