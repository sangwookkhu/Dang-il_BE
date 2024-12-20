# libraries
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
# 미들웨어
from app.middleware.session.session_middleware import SessionMiddleware
# dto
from app.schemas.service_dto.etc.sse_dto import ConnectSSEInput
# 기타 사용자 모듈
from app.services.etc.sse_connection_service import SSEConnectionService, get_sse_connection_service
from app.api_spec.sse_connection_spec import SSEConnectSpec

router = APIRouter()

@router.get("/connect", **(SSEConnectSpec.sse_connect()))
async def connect_sse(request: Request,
                      sse_service: SSEConnectionService = Depends(get_sse_connection_service)):
    user_data = await SessionMiddleware.session_check(request)
    connect_sse_input = ConnectSSEInput(user_id=user_data.get("_id"))
    
    return StreamingResponse(sse_service.connect_sse(request=request, input=connect_sse_input), media_type="text/event-stream")

