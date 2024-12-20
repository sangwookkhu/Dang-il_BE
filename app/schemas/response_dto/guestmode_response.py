from pydantic import BaseModel
from typing import Optional

class GuestmodeMainpageResponse(BaseModel):
    message: str
    data: dict