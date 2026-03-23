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

    # Server
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins'i liste olarak döndür."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Cached Settings instance döndürür."""
    return Settings()
