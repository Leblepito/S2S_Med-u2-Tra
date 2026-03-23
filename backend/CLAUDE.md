# Backend — FastAPI + WebSocket Audio Pipeline

## Kurallar
- Tüm endpoint'ler async def
- Pydantic V2 model kullan (BaseModel)
- WebSocket handler max 50 satır, business logic service'te
- Audio format: PCM16, 16kHz, mono
- Her module'ün __init__.py'si olmalı
- Type hints zorunlu (mypy strict)
- Exception handling: custom exception class'lar app/exceptions.py'de

## Test Komutları
```bash
pytest tests/ -v
pytest tests/ -v --cov=app --cov-report=term-missing
```

## Env Variables (backend/.env)
```
AZURE_TRANSLATOR_KEY=
AZURE_TRANSLATOR_REGION=southeastasia
AZURE_SPEECH_KEY=
AZURE_SPEECH_REGION=southeastasia
WHISPER_MODEL_SIZE=large-v3
WHISPER_DEVICE=cuda  # veya cpu
```
