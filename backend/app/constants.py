"""BabelFlow sabitleri — audio format, desteklenen diller."""

# Desteklenen diller (7 dil)
SUPPORTED_LANGS: frozenset[str] = frozenset(
    {"tr", "ru", "en", "th", "vi", "zh", "id"}
)

# Input audio format: PCM16 Little-Endian, 16kHz, Mono
SAMPLE_RATE: int = 16000
CHANNELS: int = 1
CHUNK_SAMPLES: int = 480  # 30ms @ 16kHz
CHUNK_BYTES: int = CHUNK_SAMPLES * 2  # PCM16 = 2 byte/sample → 960

# TTS output audio format: PCM16 Little-Endian, 24kHz, Mono
TTS_SAMPLE_RATE: int = 24000
