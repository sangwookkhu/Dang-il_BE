from pydantic import BaseModel, Field

class AuthCallbackRequest(BaseModel):
    code:str = Field(..., description="로그인 인증 코드", example="구글 or 카카오 로그인 인증 코드" )