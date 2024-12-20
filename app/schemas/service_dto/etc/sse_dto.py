from pydantic import BaseModel
from typing import Dict

class ConnectSSEInput(BaseModel):
    user_id: str
    
class InsertSSEQueueInput(BaseModel):
    user_id: str
    insert_data: Dict
    
