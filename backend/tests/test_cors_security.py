"""CORS güvenlik testleri — §1.3/S1 fail-closed doğrulama."""

import pytest

from app.config import Settings


def _make_settings(**overrides) -> Settings:
    data = {
        "CORS_ORIGINS": "http://localhost:3000",
        "ENVIRONMENT": "development",
    }
    data.update(overrides)
    return Settings(**data)


def test_wildcard_origin_rejected_even_in_development() -> None:
    settings = _make_settings(CORS_ORIGINS="*")
    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain"):
        settings.validated_cors_origins()


def test_wildcard_in_widget_extras_rejected() -> None:
    settings = _make_settings()
    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain"):
        settings.validated_cors_origins(widget_origins=["https://leblepito.com", "*"])


def test_empty_origins_rejected_in_production() -> None:
    settings = _make_settings(CORS_ORIGINS="", ENVIRONMENT="production")
    with pytest.raises(RuntimeError, match="CORS_ORIGINS is empty"):
        settings.validated_cors_origins()


def test_explicit_origins_accepted_in_production() -> None:
    settings = _make_settings(
        CORS_ORIGINS="https://babelflow.app,https://admin.babelflow.app",
        ENVIRONMENT="production",
    )
    origins = settings.validated_cors_origins(widget_origins=["https://leblepito.com"])
    assert "https://babelflow.app" in origins
    assert "https://leblepito.com" in origins
    assert "*" not in origins


def test_development_default_localhost_passes() -> None:
    settings = _make_settings()
    origins = settings.validated_cors_origins()
    assert origins == ["http://localhost:3000"]
