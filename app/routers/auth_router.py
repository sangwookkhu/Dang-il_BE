# 라이브러리 및 모듈 임포트
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException

# 의존성
from app.deps import get_user_coll
from app.services.auth_service import get_auth_service, AuthService
# 로그아웃 서비스 추가
from app.services.logout_service import LogoutService #,get_logout_service

# 미들웨어
from app.middleware.session.session_middleware import SessionMiddleware
# DTO
from app.schemas.service_dto.auth_dto import (
    AuthCallbackInput,
    AuthCallbackOutput,
    AuthLoginInput,
    AuthLoginOutput,
    AuthRegisterInput,
    AuthRegisterOutput,
)
from app.schemas.request_dto.auth_request import (
    AuthCallbackRequest
)
from app.schemas.response_dto.auth_response import (
    AuthCallbackResponse,
    # AuthLogoutResponse
)
# 기타 사용자 모듈
from app.configs.config import settings
from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.api_spec.auth_spec import AuthSpec

router = APIRouter()

# 구글 로그인
@router.get("/google/login", **(AuthSpec.auth_google_login()))
async def auth_google_login():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)

# 구글 콜백
@router.post("/google/callback", response_model=AuthCallbackResponse, **(AuthSpec.auth_google_callback()))
async def auth_google_callback(post_input: AuthCallbackRequest,
                               request: Request,
                               response: Response,
                               auth_service: AuthService = Depends(get_auth_service),
                               user_coll: MongoDBHandler = Depends(get_user_coll)):
    # 쿼리 파라미터에서 인증코드 받기, 없으면 400에러
    code = post_input.code
    print("라우터1")
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")
    print("라우터2")
    # 인증 코드 기반으로 google에 엑세스 토큰 요청해 사용자 정보 받기
    google_callback_input = AuthCallbackInput(
        code=code
    )
    print("라우터3")
    user_data: AuthCallbackOutput = await auth_service.google_callback(google_callback_input)
    print("라우터4")
    # 기존에 존재하는 유저이면 로그인, 아니면 회원가입
    existing_user = await user_coll.select({"_id": user_data.id})
    if existing_user == False:
        register_login_result: AuthRegisterOutput = await auth_service.register(user_data)
        response_message = "register process is complete"
        response_action_type = "register"
    else:
        print("라우터5")
        if existing_user.get("profile_image_url") != user_data.profile_image_url:
            print("라우터6")
            await user_coll.update(
                {"_id": user_data.id},
                {"$set": {"profile_image_url": user_data.profile_image_url}}
            )
            print("라우터6.5")
        print("라우터7")
        login_input = AuthLoginInput(
            _id=user_data.id,
            name=user_data.name,
            email=user_data.email,
            profile_image_url= user_data.profile_image_url,
            session_id=request.cookies.get("session_id"),
            access_token=user_data.access_token
        )
        print("라우터8")
        register_login_result: AuthLoginOutput = await auth_service.login(login_input)
        print("라우터9")
        response_message = "login process is complete"
        response_action_type = "login"

    # 반환된 정보로 세션id 쿠키 삽입, 응답 생성
    session_cookie = {
        "key": "session_id",
        "value": register_login_result.session_id,
        "expires": register_login_result.expires,
        "httponly": False,
        "secure": True,
        "samesite": 'None',
    }
    response.set_cookie(**session_cookie)

    return AuthCallbackResponse(
        message=response_message,
        action_type=response_action_type,
        name=user_data.name,
        profile_image_url=user_data.profile_image_url
    )

# 카카오 로그인
@router.get("/kakao/login", **(AuthSpec.auth_kakao_login()))
async def auth_kakao_login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)

# 카카오 콜백
@router.post("/kakao/callback", response_model=AuthCallbackResponse, **(AuthSpec.auth_kakao_callback()))
async def auth_kakao_callback(post_input: AuthCallbackRequest,
                              request: Request,
                              response: Response,
                              auth_service: AuthService = Depends(get_auth_service),
                              user_coll: MongoDBHandler = Depends(get_user_coll)):
    # 쿼리 파라미터에서 인증코드 받기, 없으면 400에러
    code = post_input.code
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    # 인증 코드 기반으로 google에 엑세스 토큰 요청해 사용자 정보 받기
    kakao_callback_input = AuthCallbackInput(
        code=code
    )
    user_data: AuthCallbackOutput = await auth_service.kakao_callback(kakao_callback_input)

    # 기존에 존재하는 유저이면 로그인, 아니면 회원가입
    existing_user = await user_coll.select({"_id": user_data.id})
    if existing_user == False:
        register_login_result: AuthRegisterOutput = await auth_service.register(user_data)
        response_message = "register process is complete"
        response_action_type = "register"
    else:
        if existing_user.get("profile_image_url") != user_data.profile_image_url:
            await user_coll.update(
                {"_id": user_data.id},
                {"$set": {"profile_image_url": user_data.profile_image_url}}
            )
        login_input = AuthLoginInput(
            _id=user_data.id,
            name=user_data.name,
            email=user_data.email,
            profile_image_url=user_data.profile_image_url,
            session_id=request.cookies.get("session_id"),
            access_token=user_data.access_token
        )
        register_login_result: AuthLoginOutput = await auth_service.login(login_input)
        response_message = "login process is complete"
        response_action_type = "login"

    # 반환된 정보로 세션id 쿠키 삽입, 응답 생성
    session_cookie = {
        "key": "session_id",
        "value": register_login_result.session_id,
        "expires": register_login_result.expires,
        "httponly": False,
        "secure": True,
        "samesite": 'None',
    }

    response.set_cookie(**session_cookie)

    return AuthCallbackResponse(
        message=response_message,
        action_type=response_action_type,
        name=user_data.name,
        profile_image_url=user_data.profile_image_url
    )

# 로그아웃
@router.post("/logout", **(AuthSpec.auth_logout()))
async def logout(request: Request, response:Response):
    logout_service = LogoutService()
    return await logout_service.logout(request, response)