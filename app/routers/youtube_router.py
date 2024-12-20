from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.youtube_service import YouTubeService, get_youtube_service
from app.schemas.request_dto.youtube_request import YouTubeRequest, UpdateYouTubeRequest
from app.schemas.response_dto.youtube_response import YouTubeResponse, UpdateYouTubeResponse
from app.middleware.session.session_middleware import SessionMiddleware

router = APIRouter()

@router.post("/video/save", response_model=YouTubeResponse)
async def save_video_id(request: Request, input: YouTubeRequest, service: YouTubeService = Depends(get_youtube_service)):
    try:
        user_data = await SessionMiddleware.session_check(request) 
        user_id = user_data.get("_id")
        
        result = await service.save_video_id(user_id=user_id, video_id=input.video_id)
        return YouTubeResponse(message="Video saved successfully", video_id=input.video_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/video/delete/{video_id}", response_model=YouTubeResponse)
async def delete_video_id(request: Request, video_id: str, service: YouTubeService = Depends(get_youtube_service)):
    try:
        user_data = await SessionMiddleware.session_check(request)  
        user_id = user_data.get("_id")
        
        result = await service.delete_video_id(user_id=user_id, video_id=video_id)
        return YouTubeResponse(message="Video deleted successfully", video_id=video_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/video/update", response_model=UpdateYouTubeResponse)
async def update_video_id(request: Request, input: UpdateYouTubeRequest, service: YouTubeService = Depends(get_youtube_service)):
    try:
        user_data = await SessionMiddleware.session_check(request)  
        user_id = user_data.get("_id")
        
        result = await service.update_video_id(user_id=user_id, old_video_id=input.old_video_id, new_video_id=input.new_video_id)
        return UpdateYouTubeResponse(
            message="Video updated successfully",
            old_video_id=input.old_video_id,
            new_video_id=input.new_video_id
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))