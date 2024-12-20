from pydantic import BaseModel, Field

class FriendApplyRequest(BaseModel):
    sender_id: str = Field(
        ..., 
        description="친구 요청 보내는 사람(본인) id", 
        examples=["test1"])
    receiver_id: str = Field(..., description="친구 요청 받는 사람 id", examples=["test2"])
    
class FriendApplyResRequest(BaseModel):
    consent_status: bool = Field(
        ..., 
        description="친구 수락 또는 거절 여부(수락은 True, 거절은 False)", 
        examples=[True, False]
        )
    sender_id: str = Field(
        ..., 
        description="친구 요청 보내는 사람(현재는 받은 사람 시점이므로 본인X) id", 
        examples=['test1']
        )
    
class FriendSearchRequest(BaseModel):
    search_word: str = Field(..., description="검색어(친구 이름 등)", examples=["test1"])

