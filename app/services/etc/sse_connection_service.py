# libralies
from fastapi import Request
from typing import Optional
from asyncio import create_task, gather, Queue
# dto
from app.schemas.service_dto.etc.sse_dto import (
    ConnectSSEInput,
    InsertSSEQueueInput,
)
# 기타 사용자 모듈
from app.services.abs_service import AbsService
from app.deps import get_user_queue
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class SSEConnectionService(AbsService):
    instance: Optional["SSEConnectionService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "SSEConnectionService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    # SSE 연결
    @staticmethod
    async def connect_sse(request: Request,
                          input: ConnectSSEInput,
                          user_queues=get_user_queue()):
        my_id = input.user_id
        # 큐 딕셔너리에 없으면 생성
        if(user_queues.get(my_id) is None):
            user_queues[my_id] = Queue()
        
        yield 'data: {"message": "sse connection is connected"}\n\n'
        while True:
            if(await request.is_disconnected()):
                print("테스트: 끊어요")
                break
            queue_data = await user_queues[my_id].get()
            print("큐데이터", queue_data)
            print("큐", user_queues)
            yield f'data: {queue_data}\n\n'
            
    @staticmethod
    async def insert_sse_queue(input: InsertSSEQueueInput,
                               user_queues=get_user_queue()):
        user_id = input.user_id
        
        if(user_queues.get(user_id) is None):
            user_queues[user_id] = Queue()
            
        await user_queues[user_id].put(input.insert_data)
            
        
def get_sse_connection_service():
    return SSEConnectionService.get_instance()
        
    
