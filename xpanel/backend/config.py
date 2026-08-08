from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "XPanel"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    
    # Database Settings
    DATABASE_TYPE: str = "sqlite"  # sqlite or postgresql
    DATABASE_URL: Optional[str] = None
    SQLITE_DB_PATH: str = "/app/data/xpanel.db"
    
    # PostgreSQL Settings (if using PostgreSQL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "xpanel"
    POSTGRES_PASSWORD: str = "xpanel_password"
    POSTGRES_DB: str = "xpanel"
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Default Admin Credentials
    DEFAULT_ADMIN_USERNAME: str = "admin"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    
    # Xray Core Settings
    XRAY_CONFIG_PATH: str = "/app/config/xray_config.json"
    XRAY_EXECUTABLE: str = "/usr/local/bin/xray"
    
    # Subscription Settings
    SUBSCRIPTION_HOST: str = ""
    SUBSCRIPTION_PORT: int = 8080
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.DATABASE_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        else:
            return f"sqlite+aiosqlite:///{self.SQLITE_DB_PATH}"


settings = Settings()
