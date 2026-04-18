"""BabelFlow uygulama ayarları — Pydantic Settings ile env yönetimi."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Uygulama ayarları. Env variable veya .env dosyasından yüklenir."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Whisper ASR
    WHISPER_MODEL_SIZE: str = "large-v3"
    WHISPER_DEVICE: str = "cuda"

    # Azure Translator
    AZURE_TRANSLATOR_KEY: str = ""
    AZURE_TRANSLATOR_REGION: str = "southeastasia"

    # Azure Speech (TTS)
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "southeastasia"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Development
    USE_MOCKS: bool = True
    LOG_LEVEL: str = "INFO"

    # Glossary pipeline hooks (MVP: passthrough)
    GLOSSARY_MODE: str = "passthrough"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./babelflow.db"

    # Security
    JWT_SECRET: str = "your-secret-key-change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # Server
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins'i liste olarak döndür."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def validated_cors_origins(self, widget_origins: list[str] | None = None) -> list[str]:
        """Production için fail-closed CORS doğrulaması.

        Tarayıcı zaten `*` + `credentials=True` kombinasyonunu reddeder,
        ama startup'ta yanlış config'i erkenden yakalamak için burada da reject et.
        """
        extras = widget_origins or []
        combined = self.cors_origin_list + extras
        env = self.ENVIRONMENT.strip().lower()

        if any(o.strip() == "*" for o in combined):
            raise RuntimeError(
                "CORS_ORIGINS cannot contain '*' with allow_credentials=True; "
                "list explicit origins instead."
            )

        if env != "development" and not self.cors_origin_list:
            raise RuntimeError(
                f"CORS_ORIGINS is empty in ENVIRONMENT={env!r}; set explicit origins."
            )

        return combined


@lru_cache
def get_settings() -> Settings:
    """Cached Settings instance döndürür."""
    return Settings()
