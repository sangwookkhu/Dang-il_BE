from typing import Dict
import asyncio

# 사용자별 큐 담는 딕셔너리
class UserQueue:
    user_queues = None
    
    def __init__(self):
        if(UserQueue.user_queues is None):
            UserQueue.user_queues = {}
    
    def get_queue(self):
        return UserQueue.user_queues    
    
