from pydantic import BaseModel

class TaskTimerStartRequest(BaseModel):
    task_name: str
