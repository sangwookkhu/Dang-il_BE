from pydantic import BaseModel
from typing import Dict, Union
from datetime import datetime

class TaskTimerStartInput(BaseModel):
    user_id: str
    task_name: str 
    start_time: Union[datetime, str]

class TaskTimerPauseInput(BaseModel):
    user_id: str
    end_time: Union[datetime, str]

class TaskTimerResetInput(BaseModel):
    user_id: str
    reset_time: Union[datetime, str] 

class TaskTimerOutput(BaseModel):
    message: str  
    total_time: int  
    task_specific_time: Dict[str, int]
