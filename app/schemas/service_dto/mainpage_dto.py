from pydantic import BaseModel
from typing import Dict

class MainpageGetInitialPageInput(BaseModel):
    user_data: Dict

class MainpageGetInitialPageOutput(BaseModel): # 이건 스키마 좀 애매하긴 함
    user_data: Dict
    user_space_data: Dict
    user_tasking_time_data: Dict