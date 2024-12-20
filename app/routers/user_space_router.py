#libraries
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
# 미들웨어
from app.middleware.session.session_middleware import SessionMiddleware
# 의존성 
from app.services.user_space_service import UserSpaceService, get_user_space_service
# DTO 
from app.schemas.service_dto.user_space_dto import (
    GetUserSpaceInput, GetUserSpaceOutput,
    SaveInteriorDataInput, SaveInteriorDataOutput,
    DeleteInteriorDataInput,
    GetTodoInput, GetTodoOutput,
    SaveTodoInput,SaveTodoOutput,
    DeleteTodoInput,
    GetBoardInput, GetBoardOutput,
    PostBoardInput, PostBoardOutput,
    DeleteBoardInput, DeleteBoardOutput,
    CreateMemoInput, CreateMemoOutput,
    UpdateMemoInput, UpdateMemoOutput,
    DeleteMemoInput, DeleteMemoOutput,
    GetMemoInput, GetMemoOutput,
    ChangeStandInput, ChangeStandOutput,
)
from app.schemas.request_dto.user_space_request import (
    SpaceSaveRequest,
    PostTodoRequest,
    PostBoardRequest,
    CreateMemoReq,
    UpdateMemoReq,
    DeleteMemoReq,
    ChangeLightReq,
)
from app.schemas.response_dto.user_space_response import (
    GetSpaceResponse,
    SaveSpaceResponse,
    GetTodoResponse,
    PostTodoResponse,
    DeleteSpaceResponse,
    GetBoardResponse,
    PostBoardResponse,
    DeleteBoardResponse,
    CreateMemoRes, 
    UpdateMemoRes,
    DeleteMemoRes,
    GetMemoRes,
    ChangeLightRes,
)
# 기타 사용자 모듈
from app.api_spec.user_space_spec import UserSpaceSpec
from app.schemas.service_dto.etc.sse_dto import (
    InsertSSEQueueInput,
)
from app.services.etc.sse_connection_service import SSEConnectionService, get_sse_connection_service


router = APIRouter()

@router.post("/init")
async def init_space(request: Request,
                     response: Response,
                     user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    await user_space_service.initialize_space(user_id = user_data.get("_id"))

    response.status_code = 204
    return response

# 유저 공간 정보 불러오기 + 이때 할일 적은 것+게시판도 같은 컬렉션에 넣기/ 메인페이지에는 안 가도록 함
@router.get("/{path_user_id}", response_model=GetSpaceResponse, **(UserSpaceSpec.space()))
async def get_space(request: Request,
                    path_user_id: str,
                    user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")
    user_friend_list = user_data.get("friend_list")

    # 본인인 경우 or 친구인 경우
    if(path_user_id == user_id or path_user_id in user_friend_list):
        # 정보 받아오기
        get_user_space_input = GetUserSpaceInput(id=path_user_id, is_unknown=False)
    # 모르는 사람인 경우 or 없는 유저인 경우
    else:
        # 존재 여부 + accessibility 확인
        get_user_space_input = GetUserSpaceInput(id=path_user_id, is_unknown=True)

    user_space_data: GetUserSpaceOutput = await user_space_service.get_user_space_data(get_user_space_input)

    if(user_space_data.accessibility): # 접근 가능한 유저
        return GetSpaceResponse(
            message="data successfully transferred",
            data=user_space_data.model_dump()
        )
    else:
        return JSONResponse(status_code=204)

# 유저 공간 정보 저장하기
@router.post("/save", response_model=SaveSpaceResponse, **(UserSpaceSpec.space_save()))
async def post_space_save(request: Request,
                          post_input: SpaceSaveRequest,
                          user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")
    save_input = SaveInteriorDataInput(id = user_id, updated_location_data = post_input.interior_data)
    user_space_data: SaveInteriorDataOutput = await user_space_service.save_interior_data(save_input)

    return SaveSpaceResponse(
        message="space data successfully updated",
        updated_data=user_space_data
    )

# 유저 공간 정보 초기화
@router.delete("/delete", response_model=DeleteSpaceResponse, **(UserSpaceSpec.space_delete()))
async def delete_space(request:Request,
                       user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")

    delete_interior_input = DeleteInteriorDataInput(id=user_id)
    await user_space_service.delete_interior_data(delete_interior_input)
    return DeleteSpaceResponse(
        message="space data successfully deleted"
    )

# 게시판 확인하기 -> 세션 미들웨어 필요하지 X
@router.get("/board/{path_user_id}")#, **(UserSpaceSpec.space_board()))
async def get_space_board(path_user_id,
                          user_space_service: UserSpaceService = Depends(get_user_space_service)):
    get_board_input = GetBoardInput(path_user_id)
    board_data: GetBoardOutput = await user_space_service.get_board(get_board_input)

    return GetBoardResponse(
        board_data=board_data
    )

# 친구, 모르는 유저 공간 게시판에 방명록 남기기 -> 세션 필요, 
# path_user_id는 게시판 주인 유저
@router.post("/board/{path_user_id}")#, **(UserSpaceSpec.space_board_write()))
async def post_space_board(request: Request,
                           path_user_id,
                           post_input: PostBoardRequest,
                           user_space_service: UserSpaceService = Depends(get_user_space_service),
                           sse_connection_service: SSEConnectionService = Depends(get_sse_connection_service)):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")
    user_name = user_data.get("name")
    post_board_input = PostBoardInput(
                                        sender_id=user_id,
                                        sender_name=user_name,
                                        receiver_id=path_user_id,
                                        memo=post_input.memo.get("content")
                                    )
    post_board_output: PostBoardOutput = await user_space_service.post_board(post_board_input)

    # 친구 요청 큐에 값 삽입
    queue_message = {
        "source": request.url.path,
        "data": {
            "sender_id": user_id,
            "memo": post_input.memo.get("content")
        }
    }
    insert_queue_input = InsertSSEQueueInput(
        user_id=path_user_id, # 받는 사람
        insert_data=queue_message
    )
    await sse_connection_service.insert_sse_queue(insert_queue_input)
    

    return PostBoardResponse(board_data=post_board_output.memo_data)

@router.delete("/board")#, **(UserSpaceSpec.space_board_delete()))
async def delete_space_board(request: Request,
                             user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)
    delete_board_input: DeleteBoardInput = {"receiver_id":user_data.get("_id")}
    await user_space_service.delete_board(delete_board_input)

    return DeleteBoardResponse(message="board has been cleared")

# 메모 관련
# 메모 생성
@router.post("/memo/create",
             summary="메모(pc밑에 붙는거) 만들기",
             description="""
                메모에 적을 내용을 memo_content에 적어서 넣기 <br><br>
                변경된 memo_list를 응답 <br><br>
                position은 int 리스트 <br><br>
                검증 위한 세션 id 필수
            """)
async def create_space_board(request: Request,
                             input: CreateMemoReq,
                             user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    memo_content = input.memo_content

    memo_input = CreateMemoInput(
        user_id=user_id,
        memo_content=memo_content,
        position=input.position
    )
    memo_output: CreateMemoOutput = await user_space_service.create_memo(memo_input)

    return CreateMemoRes(memo_output.memo_list)

@router.put("/memo/update",
             summary="메모(pc밑에 붙는거) 수정",
             description="""
                수정할 메모의 idx(배열 인덱스)를 memo_idx에 넣기 <br><br>
                메모에 적을 내용을 memo_content에 적어서 넣기 <br><br>
                변경된 memo_list를 응답 <br><br>
                position은 int 리스트 <br><br>
                검증 위한 세션 id 필수
            """)
async def update_space_board(request: Request,
                             input: UpdateMemoReq,
                             user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    memo_idx = input.memo_idx
    memo_content = input.memo_content

    memo_input = UpdateMemoInput(
        user_id=user_id,
        memo_idx=memo_idx,
        memo_content=memo_content
    )

    memo_output: UpdateMemoOutput = await user_space_service.update_memo(memo_input)

    return UpdateMemoRes(
        memo_list=memo_output.memo_list
    )

@router.delete("/memo/delete",
             summary="메모(pc밑에 붙는거) 삭제",
             description="""
                삭제할 메모의 memo_idx(메모 list의 배열 인덱스) <br><br>
                변경된 memo_list를 응답 <br><br>
                검증 위한 세션 id 필수
            """)
async def delete_space_board(request: Request,
                             input: DeleteMemoReq,
                             user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    memo_idx = input.memo_idx

    memo_input = DeleteMemoInput(user_id=user_id, memo_idx=memo_idx)
    memo_output: DeleteMemoOutput = await user_space_service.delete_memo(memo_input)

    return DeleteMemoRes(
        memo_list=memo_output.memo_list
    )

@router.get("/memo",
             summary="메모(pc밑에 붙는거) 조회",
             description="""
                그냥 전체 공간 정보 호출하면 메모도 포함돼서 옴, 혹시 몰라 만듬 <br><br>
                memo_list를 응답 <br><br>
                검증 위한 세션 id 필수
            """)
async def get_space_memo(request: Request,
                         user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    
    memo_input = GetMemoInput(user_id=user_id)
    memo_output: GetMemoOutput = await user_space_service.get_memo(memo_input)

    return GetMemoRes(memo_list=memo_output.memo_list)

@router.post("/stand/change",
             summary="스탠드 색상 변경",
             description="""
                변경할 색상을 light_color 에 넣어서 요청 <br><br>
                light_color는 0,1,2,3 만 가능 <br><br>
                변경된 색상 light_color로 응답 <br><br>
                검증 위한 세션 id 필수
            """)
async def change_stand_color(request: Request,
                             input: ChangeLightReq,
                             user_space_service: UserSpaceService = Depends(get_user_space_service)):
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    light_color = input.light_color

    change_input = ChangeStandInput(user_id=user_id, stand_color=light_color)
    change_output: ChangeStandOutput = await user_space_service.change_stand_color(change_input)

    return ChangeLightRes(
        change_output.stand_color
    )
