#libraries
from fastapi import APIRouter, Depends, Request
# 의존성 
from app.services.guestmode_service import GuestmodeService, get_guestmode_service
# DTO 
from app.schemas.service_dto.guestmode_dto import (
    GuestmodeGetInitialPageOutput as GetInitialPageOutput,
)
from app.schemas.response_dto.guestmode_response import (
    GuestmodeMainpageResponse
)
from app.api_spec.guestmode_spec import GuestmodeSpec

router = APIRouter()

@router.get("/mainpage", response_model=GuestmodeMainpageResponse, **(GuestmodeSpec.guestmode_mainpage()))
async def get_guestmode_mainpage(guestmode_service: GuestmodeService = Depends(get_guestmode_service)):
    initial_page_data: GetInitialPageOutput = await guestmode_service.guestmode_get_initial_page()

    return GuestmodeMainpageResponse(
        message="The response was successfully transmitted",
        data=initial_page_data.model_dump()
    )
