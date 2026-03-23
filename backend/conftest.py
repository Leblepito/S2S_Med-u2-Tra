"""BabelFlow backend test fixtures."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import app


@pytest.fixture
def mock_config() -> Settings:
    """Test için mock Settings instance — tüm key'ler sahte."""
    return Settings(
        WHISPER_MODEL_SIZE="tiny",
        WHISPER_DEVICE="cpu",
        AZURE_TRANSLATOR_KEY="test-translator-key",
        AZURE_TRANSLATOR_REGION="westeurope",
        AZURE_SPEECH_KEY="test-speech-key",
        AZURE_SPEECH_REGION="westeurope",
        REDIS_URL="redis://localhost:6379",
        USE_MOCKS=True,
        LOG_LEVEL="DEBUG",
    )


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)
