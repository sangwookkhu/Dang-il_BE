from pydantic import BaseModel
from typing import Optional

class MainpageResponse(BaseModel):
    message: str
    data: dict