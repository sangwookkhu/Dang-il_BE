from pydantic import BaseModel
from typing import Optional

class AuthCallbackResponse(BaseModel):
    message: str
    action_type: str
    name: str
    profile_image_url: str
    

class AuthLogoutResponse(BaseModel):
    message:str