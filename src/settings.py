from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_NAME: str
    YANDEX_TOKEN: str
    LOG_FILE_PATH: str = "log_file"
    class Config:
        env_file = '../app/.env'

config = Settings()