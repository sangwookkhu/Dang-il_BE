from pydantic import BaseModel
from typing import Union, Optional, Dict, List, IO, Any, Literal
from bson.binary import Binary

class CreateBookRes(BaseModel):
    user_id: str
    note_title: str
    note_description: Optional[str]=None
    note_color: Optional[Literal[0,1,2,3]]=None

class UpdateBookRes(BaseModel):
    user_id: str
    note_title: str
    note_description: str
    note_color: Optional[Literal[0,1,2,3]]=None

class OpenBookRes(BaseModel):
    user_id: str
    note_title: str
    note_description: str
    page_count: int
    page_text: str

class WritePageRes(BaseModel):
    user_id: str
    note_title: str
    note_page: int

class GetPageTextRes(BaseModel):
    note_title: str
    note_page: int
    page_text: str

class GetPageImageRes(BaseModel):
    note_title: str
    note_page: int
    page_image: Optional[Dict[str, Any]]

class GetPageFileRes(BaseModel):
    note_title: str
    note_page: int
    page_image: Optional[Dict[str, Any]]

class GetBookListRes(BaseModel):
    book_list: List[str]