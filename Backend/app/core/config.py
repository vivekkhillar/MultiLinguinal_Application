from pydantic_settings import BaseSettings, SettingsConfigDict
from .base_dir import BaseDir

env_path = BaseDir().get_base_directory() / ".env"

class config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = env_path,
        env_file_encoding="utf-8",
        extra = "ignore"
    )

    redis_port : int
    redis_host : str
    redis_timeout : int
    redis_password : str
    db_url:str
    JWT_SECRET_KEY:str
    JWT_ALGORITHM:str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    SESSION_TOKEN_EXPIRE_DAYS: int = 7