from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Awesome API"
    open_ai_key: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()