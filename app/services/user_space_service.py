# libralies
from typing import Optional
from asyncio import create_task, gather
from fastapi.exceptions import HTTPException
from datetime import datetime, timezone, timedelta
# dto
from app.schemas.service_dto.user_space_dto import (
    GetUserSpaceInput, GetUserSpaceOutput,
    SaveInteriorDataInput, SaveInteriorDataOutput,
    DeleteInteriorDataInput,
    GetTodoInput, GetTodoOutput,
    SaveTodoInput, SaveTodoOutput,
    DeleteTodoInput,
    GetBoardInput, GetBoardOutput,
    PostBoardInput, PostBoardOutput,
    DeleteBoardInput, DeleteBoardOutput,
    CreateMemoInput, CreateMemoOutput,
    UpdateMemoInput, UpdateMemoOutput,
    DeleteMemoInput, DeleteMemoOutput,
    GetMemoInput,GetMemoOutput,
    ChangeStandInput, ChangeStandOutput,
)
# 기타 사용자 모듈
from app.services.abs_service import AbsService
from app.deps import get_user_space_coll, get_user_tasking_time_coll, get_user_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class UserSpaceService(AbsService):
    instance: Optional["UserSpaceService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "UserSpaceService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    @staticmethod
    async def initialize_space(user_id: str,
                               user_space_coll: MongoDBHandler = get_user_space_coll(),
                               user_tasking_time_coll: MongoDBHandler = get_user_tasking_time_coll()):
        task1 = create_task(user_space_coll.insert(
            {
                "_id": user_id,
                "interior_data": []
                }
            ))
        task2 = create_task(user_tasking_time_coll.insert(
            {
                "_id": user_id,
                "today_tasking_time": 0
                }
            ))

        await gather(task1, task2)

    @staticmethod
    async def get_user_space_data(input: GetUserSpaceInput,
                                  user_coll: MongoDBHandler = get_user_coll(),
                                  user_space_coll: MongoDBHandler = get_user_space_coll(),
                                  user_tasking_time_coll: MongoDBHandler = get_user_tasking_time_coll())->GetUserSpaceOutput:
        user_id = input.id
        is_unknown= input.is_unknown
        
        # 본인+친구
        if(not is_unknown):
            user_space_task = create_task(user_space_coll.select({"_id": user_id}))
            user_tasking_time_task = create_task(user_tasking_time_coll.select({"_id": user_id}))
        else: # 모르는 사람 or 존재 X
            user_accessibility_data = await user_coll.select({"_id": user_id}, {"_id": 1, "accessibility": 1})
            if(not user_accessibility_data): # 존재하지 않는 유저
                raise HTTPException(404, "User does not exist")
            elif(not user_accessibility_data.get("accessibility")): # 공개 여부 false
                return GetUserSpaceOutput(accessibility=False)
            else: # 존재+공개 True
                user_space_task = create_task(user_space_coll.select({"_id": user_id}))
                user_tasking_time_task = create_task(user_tasking_time_coll.select({"_id": user_id}))
            
        return GetUserSpaceOutput(
            user_space_data=await user_space_task,
            user_tasking_time_data=await user_tasking_time_task
        )
        
    @staticmethod
    async def save_interior_data(input: SaveInteriorDataInput,
                                 user_space_coll: MongoDBHandler = get_user_space_coll()) -> SaveInteriorDataOutput:
        user_id = input.id
        updated_data = input.updated_location_data
        for idx in range(len(updated_data)):
            updated_data[idx] = updated_data[idx].model_dump(by_alias=True, exclude_none=True)
        update_result = await user_space_coll.update({"_id": str(user_id)}, {'$set': {"interior_data": updated_data}})
        

        if(update_result == False):
            raise HTTPException(status_code=400)
        
        return SaveInteriorDataOutput(
            user_space_data=updated_data
        )
    
    @staticmethod
    async def delete_interior_data(input: DeleteInteriorDataInput,
                                   user_space_coll: MongoDBHandler = get_user_space_coll())->None:
        user_id = input.id

        delete_result = await user_space_coll.delete({"_id": user_id})

        if(delete_result == False):
            raise HTTPException(status_code=400)
    
    @staticmethod
    async def get_todo(input: GetTodoInput,
                       user_space_coll: MongoDBHandler = get_user_space_coll()) -> GetTodoOutput:
        user_id = input.id
        
        user_todo_data = await user_space_coll.select({"_id": user_id}, {"todo_list": 1})

        if(user_todo_data == False or user_todo_data == []):
            return GetTodoOutput(todo_list=[])
        else:
            return GetTodoOutput(todo_list=user_todo_data)

    @staticmethod
    async def save_todo(input: SaveTodoInput,
                        user_space_coll: MongoDBHandler = get_user_space_coll()) -> SaveTodoOutput:
        user_id = input.id
        todo_list = input.todo_list

        update_result = await user_space_coll.update(filter={"_id": user_id}, update={"$set": {"todo_list": todo_list}})

        if(update_result == False):
            HTTPException(status_code=400)
        else:
            return SaveTodoOutput(todo_list)

    @staticmethod
    async def delete_todo(input: DeleteTodoInput,
                          user_space_coll: MongoDBHandler = get_user_space_coll()) -> None:
        user_id = input.id
        delete_result = await user_space_coll.delete({"_id": user_id})

        if(delete_result == False):
            raise HTTPException(status_code=400)
        
    @staticmethod
    async def get_board(input: GetBoardInput,
                        user_space_coll: MongoDBHandler = get_user_space_coll()) -> GetBoardOutput:
        user_id = input.id
        board_data = await user_space_coll.select({"_id": user_id}, {"board": 1})
        return GetBoardOutput(board_data=board_data)

    @staticmethod # 작업중
    async def post_board(input: PostBoardInput,
                         user_space_coll: MongoDBHandler = get_user_space_coll()) -> PostBoardOutput:
        receiver_id = input.receiver_id
        sender_name = input.sender_name
        sender_id = input.sender_id
        memo_data = input.memo

        memo = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "content": memo_data,
            "date" : datetime.now(timezone.utc)
        }

        await user_space_coll.update(
            {"_id": receiver_id},
            {"$push": {"board": memo}}
        )

        memo_data = (await user_space_coll.select(
            {"_id": receiver_id},
            {"board":1}
        )).get("board")

        return PostBoardOutput(memo_data = memo_data)
    
    @staticmethod
    async def delete_board(input: DeleteBoardInput,
                           user_space_coll: MongoDBHandler = get_user_space_coll())->DeleteBoardOutput:
        receiver_id = input.receiver_id
        await user_space_coll.delete(
            {"_id": receiver_id},  
            {"$set": {"board": []}}
        )

    # 메모 관련
    # 메모 생성
    @staticmethod 
    async def create_memo(input: CreateMemoInput,
                          user_space_coll: MongoDBHandler = get_user_space_coll())->CreateMemoOutput:
        user_id = input.user_id
        memo_list_elem = [input.memo_content, input.position]

        await user_space_coll.update(
            {"_id": user_id},
            {"$push": {"memo_list": memo_list_elem}}
        )

        memo_list = (await user_space_coll.select({"_id": user_id}, {"memo_list": 1})).get("memo_list")
        if(memo_list is None):
            memo_list = []
        return CreateMemoOutput(
            memo_list=memo_list
        )
    
    # 메모 수정
    @staticmethod
    async def update_memo(input: UpdateMemoInput,
                          user_space_coll: MongoDBHandler = get_user_space_coll()) -> UpdateMemoOutput: 
        user_id = input.user_id
        memo_idx = input.memo_idx
        memo_content = [input.memo_content, input.position]

        update_count = await user_space_coll.update(
            {"_id": user_id},
            {"$set": {
                f"memo_list.{memo_idx}": memo_content
            }}
        )

        if(update_count <= 0):
            return None

        memo_list = (await user_space_coll.select({"_id": user_id}, {"memo_list": 1})).get("memo_list")
        if(memo_list is None):
            memo_list = []
        return UpdateMemoOutput(
            memo_list=memo_list
        ) 

    @staticmethod
    async def delete_memo(input: DeleteMemoInput,
                          user_space_coll: MongoDBHandler = get_user_space_coll()) -> DeleteMemoOutput:
        user_id = input.user_id
        memo_idx = input.memo_idx

        memo_list = (await user_space_coll.select({"_id": user_id}, {"memo_list": 1})).get("memo_list")
        del memo_list[memo_idx]

        await user_space_coll.update(
            {"_id": user_id},
            {"$set": {"memo_list": memo_list}}
        )

        return DeleteMemoOutput(memo_list=memo_list)

    @staticmethod
    async def get_memo(input: GetMemoInput,
                       user_space_coll: MongoDBHandler = get_user_space_coll()) -> GetMemoOutput:
        user_id = input.user_id

        memo_list = (await user_space_coll.select({"_id": user_id}, {"memo_list": 1})).get("memo_list")
        if(memo_list == None):
            memo_list = []

        return GetMemoOutput(memo_list=memo_list)

    @staticmethod
    async def change_stand_color(input: ChangeStandInput,
                                 user_space_coll: MongoDBHandler = get_user_space_coll()) -> ChangeStandInput:
        user_id = input.user_id
        stand_color = input.stand_color

        await user_space_coll.update(
            {"_id": user_id},
            {"$set": {"light_color": stand_color}}
        )

        return ChangeStandOutput(stand_color=stand_color)


def get_user_space_service():
    return UserSpaceService.get_instance()