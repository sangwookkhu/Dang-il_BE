from pydantic import BaseModel

class TaskTimerResponse(BaseModel):
    message: str
    time_in_seconds: int
