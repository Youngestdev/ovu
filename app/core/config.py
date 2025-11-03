"""
Configuration management for Ovu Transport Aggregator
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Ovu Transport Aggregator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_VERSION: str = "v1"
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "ovu_transport"
    
    # Travu API
    TRAVU_API_KEY: str = ""
    TRAVU_API_URL: str = "https://api.travu.com"
    TRAVU_API_SECRET: str = ""
    
    # NRC API
    NRC_API_KEY: str = ""
    NRC_API_URL: str = "https://api.nrc.gov.ng"
    NRC_API_SECRET: str = ""
    
    # Paystack
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: str
    PAYSTACK_WEBHOOK_SECRET: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str
    SMTP_FROM_NAME: str = "Ovu Transport"
    
    # Resend
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str = "Ovu Transport <noreply@ovu.ng>"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Compliance
    PCI_DSS_MODE: str = "enabled"
    NDPA_COMPLIANCE: str = "enabled"
    DATA_ENCRYPTION_KEY: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
