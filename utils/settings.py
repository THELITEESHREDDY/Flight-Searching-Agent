from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env',extra='ignore')
    SQL_DATABASE:str
    SERP_API:str
    AI_KEY:str
    SQLLITE:str
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:str

settings = Settings()
