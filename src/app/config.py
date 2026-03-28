from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_DAYS: int = 7

    SECRET_KEY: str


    REDIS_HOST:str="localhost"
    REDIS_PORT:int=6379


    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_PORT:int
    MAIL_SERVER:str
    MAIL_TO:str
    MAIL_STARTTLS:bool = False
    MAIL_SSL_TLS:bool = True
    USE_CREDENTIALS:bool = True
    VALIDATE_CERTS:bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = Settings()
