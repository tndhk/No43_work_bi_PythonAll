from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # S3
    s3_endpoint: Optional[str] = None
    s3_region: str = "ap-northeast-1"
    s3_bucket: str = "bi-datasets"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None

    # Auth
    basic_auth_username: str = "admin"
    basic_auth_password: str = "changeme"
    
    # Flask session secret key
    secret_key: str = secrets.token_urlsafe(32)
    
    # Auth provider type (future: "form" | "saml")
    auth_provider_type: str = "form"
    
    # DOMO API
    domo_client_id: Optional[str] = None
    domo_client_secret: Optional[str] = None

    # Gemini LLM
    gemini_api_key: Optional[str] = None
    gemini_model_name: str = "gemini-3-flash-preview"


settings = Settings()
