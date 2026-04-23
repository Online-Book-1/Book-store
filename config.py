from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_HOST: str
    DB_PORT: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_DRIVER: str
    DB_DIALECT: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    KAFKA_BOOTSTRAP_SERVERS: str
    REDIS_SERVERS: str
    REDIS_PORT: str
    REFRESH_TOKEN_SECRET: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    def get_db_url(self):
        return f"{self.DB_DIALECT}+{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()