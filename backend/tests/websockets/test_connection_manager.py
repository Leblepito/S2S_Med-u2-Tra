"""ConnectionManager testleri."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas import ConfigMessage
from app.websockets.connection_manager import ConnectionManager


class TestConnectionManager:
    """ConnectionManager class testleri."""

    @pytest.fixture
    def manager(self) -> ConnectionManager:
        return ConnectionManager()

    @pytest.fixture
    def mock_ws(self) -> MagicMock:
        return MagicMock()

    @pytest.fixture
    def config(self) -> ConfigMessage:
        return ConfigMessage(target_langs=["en", "th"])

    def test_connect_increases_count(
        self, manager: ConnectionManager, mock_ws: MagicMock, config: ConfigMessage
    ) -> None:
        """Connect sonrası active_count artmalı."""
        assert manager.active_count == 0
        manager.connect(mock_ws, config)
        assert manager.active_count == 1

    def test_disconnect_decreases_count(
        self, manager: ConnectionManager, mock_ws: MagicMock, config: ConfigMessage
    ) -> None:
        """Disconnect sonrası active_count azalmalı."""
        manager.connect(mock_ws, config)
        manager.disconnect(mock_ws)
        assert manager.active_count == 0

    def test_get_config(
        self, manager: ConnectionManager, mock_ws: MagicMock, config: ConfigMessage
    ) -> None:
        """Connect edilen ws'nin config'i dönmeli."""
        manager.connect(mock_ws, config)
        retrieved = manager.get_config(mock_ws)
        assert retrieved.target_langs == ["en", "th"]

    def test_get_config_unknown_ws(
        self, manager: ConnectionManager, mock_ws: MagicMock
    ) -> None:
        """Bilinmeyen ws → KeyError."""
        with pytest.raises(KeyError):
            manager.get_config(mock_ws)

    def test_disconnect_unknown_ws(
        self, manager: ConnectionManager, mock_ws: MagicMock
    ) -> None:
        """Bilinmeyen ws disconnect → sessiz geç (KeyError fırlatma)."""
        manager.disconnect(mock_ws)  # hata fırlatmamalı
        assert manager.active_count == 0

    def test_multiple_connections(
        self, manager: ConnectionManager, config: ConfigMessage
    ) -> None:
        """Birden fazla bağlantı yönetilebilmeli."""
        ws1, ws2, ws3 = MagicMock(), MagicMock(), MagicMock()
        manager.connect(ws1, config)
        manager.connect(ws2, config)
        manager.connect(ws3, config)
        assert manager.active_count == 3

        manager.disconnect(ws2)
        assert manager.active_count == 2
