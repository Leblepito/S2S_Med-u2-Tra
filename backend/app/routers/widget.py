"""Widget configuration API."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/widget", tags=["widget"])

SUPPORTED_LANGUAGES = [
    {"code": "tr", "name": "Türkçe", "flag": "\U0001f1f9\U0001f1f7"},
    {"code": "ru", "name": "Русский", "flag": "\U0001f1f7\U0001f1fa"},
    {"code": "en", "name": "English", "flag": "\U0001f1ec\U0001f1e7"},
    {"code": "th", "name": "ไทย", "flag": "\U0001f1f9\U0001f1ed"},
    {"code": "vi", "name": "Tiếng Việt", "flag": "\U0001f1fb\U0001f1f3"},
    {"code": "zh", "name": "中文", "flag": "\U0001f1e8\U0001f1f3"},
    {"code": "id", "name": "Indonesia", "flag": "\U0001f1ee\U0001f1e9"},
]


@router.get("/config")
async def widget_config() -> dict:
    """Return widget default configuration for embedding."""
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "default_language": "en",
        "version": "1.0.0",
        "features": {
            "voice_translation": True,
            "text_display": True,
            "audio_playback": True,
        },
    }
