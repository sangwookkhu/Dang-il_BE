from pydantic import BaseModel

class YouTubeRequest(BaseModel):
    video_id: str  

class UpdateYouTubeRequest(BaseModel):
    old_video_id: str
    new_video_id: str