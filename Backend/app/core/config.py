from pydantic_settings import BaseSettings, SettingsConfigDict
from core.base_dir import BaseDir


env_path = str(BaseDir().get_base_directory()) + "\\.env"
class config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = env_path,
        env_file_encoding="utf-8",
    )

    redis_port : int
    redis_host : str
    redis_timeout : int
    redis_password : str
