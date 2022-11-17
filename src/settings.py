from pydantic import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    BOT_NAME: str
    YANDEX_TOKEN: str
    CHANNEL_CHAT_ID: str
    BOT_NOTIFICATOR_TOKEN: str
    LOG_FILE_PATH: str = "log_file"
    class Config:
        env_file = '../app/.env'

config = Settings()