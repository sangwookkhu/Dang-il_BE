from app.deps import get_user_tasking_time_coll
from app.schemas.response_dto.task_timer_response import TaskTimerResponse
from motor.motor_asyncio import AsyncIOMotorCollection
from fastapi import Depends

class TaskTimerService:
    def __init__(self, task_timer_coll: AsyncIOMotorCollection = Depends(get_user_tasking_time_coll)):
        self.task_timer_coll = task_timer_coll

    # 타이머 시간 저장
    async def save_task_timer(self, user_data: dict, time_in_seconds: int) -> TaskTimerResponse:
        await self.task_timer_coll.update_one(
            {"user_id": user_data['user_id']},
            {"$set": {"time_in_seconds": time_in_seconds}},
            upsert=True
        )
        return TaskTimerResponse(message="타이머 시간 저장 성공", time_in_seconds=time_in_seconds)

    # 타이머 시간 불러오기
    async def get_task_timer(self, user_data: dict) -> TaskTimerResponse:
        user_timer = await self.task_timer_coll.find_one({"user_id": user_data['user_id']})
        if user_timer:
            return TaskTimerResponse(message="타이머 시간 불러오기 성공", time_in_seconds=user_timer.get("time_in_seconds", 0))
        else:
            return TaskTimerResponse(message="타이머 기록이 없습니다.", time_in_seconds=0)

    # 타이머 리셋
    async def reset_task_timer(self, user_data: dict) -> TaskTimerResponse:
        await self.task_timer_coll.update_one(
            {"user_id": user_data['user_id']},
            {"$set": {"time_in_seconds": 0}},
            upsert=True
        )
        return TaskTimerResponse(message="타이머 리셋", time_in_seconds=0)
