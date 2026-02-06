from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # S3
    s3_endpoint: str | None = None
    s3_region: str = "ap-northeast-1"
    s3_bucket: str = "bi-datasets"
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    # Auth
    basic_auth_username: str = "admin"
    basic_auth_password: str = "changeme"


settings = Settings()
