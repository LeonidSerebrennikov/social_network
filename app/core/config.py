from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # ========== Project Settings ==========
    PROJECT_NAME: str = "Social Network API"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    API_V1_PREFIX: str = "/api/v1"
    COMPONENTS_PATH: str = "cmp"
    
    # ========== Database Settings ==========
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="social_network")
    POSTGRES_PORT: str = Field(default="5432")
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ========== Database Pool Settings ==========
    DB_ECHO: bool = Field(default=False, description="Log SQL queries")
    DB_POOL_SIZE: int = Field(default=10, ge=1, le=100)
    DB_MAX_OVERFLOW: int = Field(default=20, ge=0)
    DB_POOL_TIMEOUT: int = Field(default=30, ge=1)
    DB_POOL_RECYCLE: int = Field(default=3600, ge=1)
    
    # ========== Redis Settings ==========
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ========== Security ==========
    SECRET_KEY: str = Field(
        default="_example_secret__example_secret_",
        min_length=32,
        description="Secret key for JWT and security"
    )
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    
    # ========== CORS ==========
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="List of allowed CORS origins"
    )
    
    # ========== Rate Limiting ==========
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Time window in seconds")
    
    # ========== Pagination ==========
    DEFAULT_PAGE_SIZE: int = Field(default=20, ge=1, le=100)
    MAX_PAGE_SIZE: int = Field(default=100, ge=1)
    
    # ========== Logging ==========
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ========== File Upload ==========
    MAX_UPLOAD_SIZE: int = Field(
        default=5 * 1024 * 1024,  # 5 MB
        description="Maximum upload size in bytes"
    )
    ALLOWED_IMAGE_TYPES: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"]
    )
    
    # ========== Cache Settings ==========
    CACHE_DEFAULT_TTL: int = Field(default=300, description="Default cache TTL in seconds")
    CACHE_USER_TTL: int = Field(default=600, description="User cache TTL in seconds")
    CACHE_POST_TTL: int = Field(default=60, description="Post cache TTL in seconds")
    
    # ========== Feature Flags ==========
    ENABLE_SWAGGER: bool = Field(default=True, description="Enable Swagger UI")
    ENABLE_METRICS: bool = Field(default=False, description="Enable Prometheus metrics")
    ENABLE_SENTRY: bool = Field(default=False, description="Enable Sentry error tracking")
    
    # ========== Sentry ==========
    SENTRY_DSN: Optional[str] = Field(default=None)
    
    # ========== Admin Settings ==========
    FIRST_SUPERUSER_EMAIL: str = Field(default="admin@example.com")
    FIRST_SUPERUSER_PASSWORD: str = Field(default="admin123")
    FIRST_SUPERUSER_USERNAME: str = Field(default="admin")


settings = Settings()