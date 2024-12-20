#libraries
from fastapi import APIRouter, Depends, Request
# 미들웨어
from app.middleware.session.session_middleware import SessionMiddleware
# 의존성 
from app.services.mainpage_service import MainpageService, get_mainpage_service
# DTO 
from app.schemas.service_dto.mainpage_dto import (
    MainpageGetInitialPageInput as GetInitialPageInput,
    MainpageGetInitialPageOutput as GetInitialPageOutput,
)
from app.schemas.response_dto.mainpage_response import (
    MainpageResponse
)
from app.api_spec.mainpage_spec import MainpageSpec

router = APIRouter()

@router.get("/", response_model = MainpageResponse, **(MainpageSpec.mainpage()))
async def get_mainpage(request: Request,
                       mainpage_service: MainpageService = Depends(get_mainpage_service)):
    
    user_data = await SessionMiddleware.session_check(request)
    initial_page_input = GetInitialPageInput(user_data=user_data)
    initial_page_data: GetInitialPageOutput = await mainpage_service.get_initial_page(initial_page_input)
    
    return MainpageResponse(
        message="The response was successfully transmitted",
        data=initial_page_data.model_dump()
    )
    
    
    
    