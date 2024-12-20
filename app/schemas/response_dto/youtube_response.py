from pydantic import BaseModel

class YouTubeResponse(BaseModel):
    message: str  
    video_id: str

class UpdateYouTubeResponse(BaseModel):
    message: str
    old_video_id: str
    new_video_id: str
    