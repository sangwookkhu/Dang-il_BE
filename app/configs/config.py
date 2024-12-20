from pydantic_settings import BaseSettings # type: ignore
from typing import Optional

class Settings(BaseSettings):
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    SECRET_KEY: str
    
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB_NUMBER: Optional[int] = None
    
    URL_ADDRESS: str
    BACKEND_PATH: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()