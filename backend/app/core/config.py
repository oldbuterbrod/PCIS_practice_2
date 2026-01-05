"""
Простая конфигурация для начала
"""
import os
from typing import List

class Settings:
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://vaultdoc_user:vaultdoc_pass@localhost:5433/vaultdoc_db"
    )
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "vaultdoc-secret-key-dev-2024")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # App
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

settings = Settings()
