from pydantic import BaseModel
from typing import Union, Tuple, List, Optional, Dict, Literal
from app.schemas.database_dto.db_schemas import FurnitureArrange

class GetUserSpaceInput(BaseModel):
    id: str
    is_unknown: bool

class GetUserSpaceOutput(BaseModel):
    accessibility: bool = True
    user_space_data: Optional[Union[dict, bool]] = None
    user_tasking_time_data: Optional[Union[dict, bool]] = None

class SaveInteriorDataInput(BaseModel):
    id: str
    updated_location_data: List[Optional[FurnitureArrange]]

class SaveInteriorDataOutput(BaseModel):
    user_space_data: List[dict]

class DeleteInteriorDataInput(BaseModel):
    id: str

class GetTodoInput(BaseModel):
    id: str

class GetTodoOutput(BaseModel):
    todo_list: List[str]

class SaveTodoInput(BaseModel):
    id: str
    todo_list: List[str]

class SaveTodoOutput(BaseModel):
    todo_list: List[str]

class DeleteTodoInput(BaseModel):
    id: str

class GetBoardInput(BaseModel):
    id: str

class GetBoardOutput(BaseModel):
    board_data: list

class PostBoardInput(BaseModel):
    sender_id: str
    sender_name: str
    receiver_id: str
    memo: str

class Memo(BaseModel):
    sender_id: str
    sender_name: str
    content: str

class PostBoardOutput(BaseModel):
    memo_data: List[Memo]

class DeleteBoardInput(BaseModel):
    receiver_id: str

class DeleteBoardOutput(BaseModel):
    pass

# 메모
class CreateMemoInput(BaseModel):
    user_id: str
    memo_content: str
    position: List[str]

class CreateMemoOutput(BaseModel):
    memo_list : List[str]
    position: List[str]

class UpdateMemoInput(BaseModel):
    user_id: str
    memo_idx: int
    memo_content: str
    position: List[str]

class UpdateMemoOutput(BaseModel):
    memo_list: List[str]

class DeleteMemoInput(BaseModel):
    user_id: str
    memo_idx: int

class DeleteMemoOutput(BaseModel):
    memo_list: List[str]

class GetMemoInput(BaseModel):
    user_id: str

class GetMemoOutput(BaseModel):
    memo_list: List[str]

# 스탠드 색깔 바꾸기
class ChangeStandInput(BaseModel):
    user_id: str
    stand_color: Literal[0, 1, 2, 3]

class ChangeStandOutput(BaseModel):
    stand_color: Literal[0, 1, 2, 3]