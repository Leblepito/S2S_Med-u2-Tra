"""WebSocket bağlantı yönetimi."""

import logging
from typing import Any

from app.schemas import ConfigMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Aktif WebSocket bağlantılarını ve config'lerini yönetir."""

    def __init__(self) -> None:
        self._connections: dict[Any, ConfigMessage] = {}

    @property
    def active_count(self) -> int:
        """Aktif bağlantı sayısı."""
        return len(self._connections)

    def connect(self, ws: Any, config: ConfigMessage) -> None:
        """Yeni bağlantı kaydet.

        Args:
            ws: WebSocket instance.
            config: İstemci konfigürasyonu.
        """
        self._connections[ws] = config
        logger.info(f"[WS_CONNECT] active={self.active_count}")

    def disconnect(self, ws: Any) -> None:
        """Bağlantıyı kaldır. Bilinmiyorsa sessiz geç.

        Args:
            ws: WebSocket instance.
        """
        self._connections.pop(ws, None)
        logger.info(f"[WS_DISCONNECT] active={self.active_count}")

    def get_config(self, ws: Any) -> ConfigMessage:
        """Bağlantının config'ini döndür.

        Args:
            ws: WebSocket instance.

        Returns:
            ConfigMessage.

        Raises:
            KeyError: Bilinmeyen bağlantı.
        """
        return self._connections[ws]
