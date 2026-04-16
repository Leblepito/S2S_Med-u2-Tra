"""BabelFlow custom exception hiyerarşisi."""


class BabelFlowError(Exception):
    """Tüm BabelFlow hatalarının base class'ı."""


class AudioFormatError(BabelFlowError):
    """Audio format uyumsuzluğu (sample rate, channels, chunk size)."""


class TranscriptionError(BabelFlowError):
    """ASR/Whisper transcription hatası."""


class TranslationError(BabelFlowError):
    """Azure Translator API hatası."""


class TTSError(BabelFlowError):
    """Azure TTS sentez hatası."""


class WebSocketError(BabelFlowError):
    """WebSocket bağlantı/protokol hatası."""
