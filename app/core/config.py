from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MODEL_PATH: str
    MODEL_TEMPORAL_PATH: str
    TOKENIZER_PATH: str
    TEMPORAL_SCALER_PATH: str
    DATABASE_URL: str
    ADMIN_FULL_NAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()
