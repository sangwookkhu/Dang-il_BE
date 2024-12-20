from pydantic import BaseModel
from typing import Dict, List, Union

class FriendApplyResponse(BaseModel):
    message: str
    data: Dict[str, Union[str, list]]

class FriendApplyResResponse(FriendApplyResponse):
    pass

class FriendSearchData(BaseModel):
    id: str
    name: str
    tag: str

class FriendSearchResponse(BaseModel):
    message: str
    user_data_list: list