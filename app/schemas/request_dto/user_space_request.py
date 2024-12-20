from pydantic import BaseModel, Field
from typing import Tuple, List, Optional, Literal
from app.schemas.database_dto.db_schemas import FurnitureArrange


class SpaceSaveRequest(BaseModel):
    interior_data: List[Optional[FurnitureArrange]]
    
class PostTodoRequest(BaseModel):
    todo_data: List[str] = Field(..., 
        description="Todo 데이터 리스트로 보내기",
        example=[
                "국어", "수학"
            ]
        )
class PostBoardRequest(BaseModel):
    memo: dict = Field(...,
        description="메모 데이터 딕셔너리로 보내기",
        example={
            "content": "게시판에 작성할 글입니다."
        }
    )

class CreateMemoReq(BaseModel):
    memo_content: str
    position: List[str]

class UpdateMemoReq(BaseModel):
    memo_idx: int
    memo_content: str
    position: List[str]

class DeleteMemoReq(BaseModel):
    memo_idx: int

class ChangeLightReq(BaseModel):
    light_color: Literal[0, 1, 2, 3]