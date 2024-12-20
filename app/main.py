import os, sys, dotenv
dotenv.load_dotenv(encoding="utf-8")
sys.path.append(os.getenv("BACKEND_PATH"))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 기존 라우터, 서브앱
from routers.auth_router import router as auth_router
from routers.mainpage_router import router as mainpage_router
from routers.guestmode_router import router as guestmode_router
from routers.etc.sse_connection_router import router as sse_router
from routers.friend_router import router as friend_router
from routers.user_space_router import router as space_router
from app.routers.youtube_router import router as youtube_router
from routers.tasking_note_router import router as book_router
from routers.user_updatename_routers import router as user_router
from routers.task_timer_router import router as task_router

app = FastAPI(
    title="예술적인 소프트웨어 dangil api 문서",
    description="예술적인 소프트웨어 api 엔드포인트 설명입니다.",
    contact={"name": "강상욱, 채지성"},
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "https://localhost:3000", "https://localhost:8000"],  # 모든 출처를 허용합니다.
    allow_credentials=True,  # 쿠키를 포함한 요청을 허용합니다.
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다. 예: GET, POST, PUT, DELETE, PATCH 등
    allow_headers=["*"],  # 모든 헤더를 허용합니다.
)

# 기존 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(auth_router, prefix="/auth", tags=["login"])
app.include_router(mainpage_router, prefix="/mainpage", tags=["mainpage"])
app.include_router(guestmode_router, prefix="/guestmode", tags=["guestmode"])
app.include_router(sse_router, prefix="/sse", tags=["sse"])
app.include_router(friend_router, prefix="/friend", tags=["friend"])
app.include_router(space_router, prefix="/space", tags=["space"])
app.include_router(book_router, prefix="/book", tags=["book"])
app.include_router(youtube_router, prefix="/youtube", tags=["YouTube"])
app.include_router(user_router, prefix="/users", tags=["user"])
app.include_router(task_router, prefix="/task", tags=["task"])

@app.get("/")
async def index():
    return {"message": "index page"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)