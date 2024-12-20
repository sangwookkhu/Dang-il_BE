#libraries
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
# DTO 
from app.schemas.service_dto.friend_dto import (
    FriendApplyInput,
    FriendApplyOutput,
    FriendApplyResInput,
    FriendApplyResOutput,
    FriendSearchInput,
    FriendSearchOutput,
    FriendFriendSearchInput,
)
from app.schemas.request_dto.friend_request import (
    FriendApplyRequest,
    FriendApplyResRequest,
    FriendSearchRequest
)
from app.schemas.response_dto.friend_response import (
    FriendApplyResponse,
    FriendApplyResResponse,
    FriendSearchResponse,
)
from app.schemas.service_dto.etc.sse_dto import (
    InsertSSEQueueInput,
)
# 기타 사용자 모듈
from app.middleware.session.session_middleware import SessionMiddleware
from app.services.friend_service import FriendService, get_friend_service
from app.services.etc.sse_connection_service import SSEConnectionService, get_sse_connection_service
from app.api_spec.friend_spec import FriendSpec

router = APIRouter()

@router.post(path="/apply", response_model=FriendApplyResponse, **(FriendSpec.friend_apply()))
async def post_friend_apply(request: Request,
                            post_input: FriendApplyRequest,
                            friend_service: FriendService = Depends(get_friend_service),
                            sse_connection_service: SSEConnectionService = Depends(get_sse_connection_service)):
    user_data = await SessionMiddleware.session_check(request)

    sender_id = post_input.sender_id
    receiver_id = post_input.receiver_id
    user_name = user_data.get("name")

    # 검증 -> 쿠키의 id와 입력 sender_id가 다르면 기각
    if(sender_id != user_data.get("_id")):
        return JSONResponse(content={}, status_code=400)
    
    friend_apply_input = FriendApplyInput(
        sender_id=sender_id,
        receiver_id=receiver_id,
        sender_friend_list=user_data.get("friend_list")
    )
    friend_apply_result: FriendApplyOutput = await friend_service.friend_apply(friend_apply_input)
    
    if(friend_apply_result.status == "already_friend"):
        response_content = {
            "message": "This friend is already added."
        }
        return JSONResponse(content=response_content, status_code=204)
    if(friend_apply_result.status == "already_send"):
        response_content = {
            "message": "The request was sent within 3 days"
        }
        return JSONResponse(content=response_content, status_code=204)
    
    # 친구 요청 큐에 값 삽입
    queue_message = {
        "source": request.url.path,
        "data": {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "sender_name": user_name
        }
    }
    insert_queue_input = InsertSSEQueueInput(
        user_id=receiver_id,
        insert_data=queue_message
    )
    await sse_connection_service.insert_sse_queue(insert_queue_input)
    
    return FriendApplyResponse(
        message="Request has been successfully sent",
        data={
            "sender_id": sender_id,
            "receiver_id": receiver_id
        }
    )

@router.post(path="/apply/response", response_model=FriendApplyResResponse, **(FriendSpec.friend_apply_response()))
async def post_friend_apply_response(request: Request,
                                    post_input: FriendApplyResRequest,
                                    friend_service: FriendService = Depends(get_friend_service),
                                    sse_connection_service: SSEConnectionService = Depends(get_sse_connection_service)):
    user_data = await SessionMiddleware.session_check(request)
    
    sender_id = post_input.sender_id
    receiver_id = user_data.get("_id")
    receiver_name = user_data.get("name")
    consent_status = post_input.consent_status
    
    friend_apply_res_input = FriendApplyResInput(
        consent_status=consent_status,
        sender_id=sender_id,
        receiver_id=receiver_id
    )
    
    friend_apply_response: FriendApplyResOutput = await friend_service.friend_apply_response(friend_apply_res_input)
    
    if(consent_status):
        # 친구 요청 승낙 여부 큐에 삽입
        queue_message = {
            "source": request.url.path,
            "data": {
                "consent_status": consent_status,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "receiver_name": receiver_name
            }
        }
        insert_queue_input = InsertSSEQueueInput(
            user_id=sender_id,
            insert_data=queue_message
        )
        await sse_connection_service.insert_sse_queue(insert_queue_input)
        
        response_message = "Friend request accepted successfully"
    else:
        response_message = "Friend request denied successfully"
        
    return FriendApplyResResponse(
        message=response_message,
        data={
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "reciever_friendlist": friend_apply_response.receiver_friendlist
        }
    )

@router.post(path="/search", **(FriendSpec.friend_search()))
async def post_friend_search(post_input: FriendSearchRequest,
                             friend_service: FriendService = Depends(get_friend_service)):
    search_word = post_input.search_word
    
    friend_search_input = FriendSearchInput(search_word=search_word)
    friend_search_data: FriendSearchOutput = await friend_service.friend_search(friend_search_input)
    
    if(not friend_search_data.exist_status):
        return JSONResponse(
            content={"message": "The search data does not exist"},
            status_code=204
        )
    else:
        return FriendSearchResponse(
            message="search data successfully transported",
            user_data_list=friend_search_data.user_data_list
        )
    
@router.post(path="/friendsearch",
             summary="친구만 검색하는 api",
             description="세션 필요, 친구만 검색(/friend/search는 친구 아니어도 검색) api")
async def post_friend_search(request: Request,
                             post_input: FriendSearchRequest,
                             friend_service: FriendService = Depends(get_friend_service)):
    user_data = await SessionMiddleware.session_check(request)

    friend_list = user_data.get("friend_list")
    search_word = post_input.search_word
    
    friend_search_input = FriendFriendSearchInput(
        friend_list = friend_list,
        search_word= search_word
    )
    friend_search_data: FriendSearchOutput = await friend_service.friend_friendsearch(friend_search_input)
    
    if(not friend_search_data.exist_status):
        return JSONResponse(
            content={"message": "The search data does not exist"},
            status_code=204
        )
    else:
        return FriendSearchResponse(
            message="search data successfully transported",
            user_data_list=friend_search_data.user_data_list
        )