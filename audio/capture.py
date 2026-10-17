"""
K1 — Gerçek Mikrofon Yakalama İskeleti (`audio/capture.py`)
İzinli Sahip: Katılımcı 1 (K1)

Hafta 1-3 Görev Özeti:
- `sounddevice` ile 16 kHz mono PCM ses çerçeveleri (`AudioFrame`) üretmek.
- Sınırlı kuyruk (ring buffer) ile sessizlikte veri birikmesini önlemek.
- Cihaz yok, izin reddi ve cihaz kopması durumlarında standart `ErrorCode` üretmek.
- GİZLİLİK: Ham ses verisini asla diske (.wav / .pcm) yazmamak.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from contracts.models import AudioConfig, AudioFrame


class MicrophoneAudioSource:
    """Gerçek mikrofon yakalama sınıfı (K1 tarafından Hafta 1'de tamamlanacaktır)."""

    def __init__(self, config: Optional[AudioConfig] = None) -> None:
        self._config = config or AudioConfig()
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def list_devices(self) -> List[Dict[str, object]]:
        """TODO (K1 - Hafta 1): sounddevice.query_devices() ile giriş cihazlarını listele."""
        raise NotImplementedError("K1 Hafta 1 görevinde uygulanacaktır.")

    def start(self, config: Optional[AudioConfig] = None) -> None:
        """TODO (K1 - Hafta 1): 16 kHz mono RawInputStream başlat."""
        raise NotImplementedError("K1 Hafta 1 görevinde uygulanacaktır.")

    def stop(self) -> None:
        """TODO (K1 - Hafta 1/2): Akışı güvenli kapat ve kuyruğu temizle."""
        self._running = False

    def read_frame(self, timeout_ms: int = 200) -> Optional[AudioFrame]:
        """TODO (K1 - Hafta 1/2): Kuyruktan sıradaki AudioFrame nesnesini döndür."""
        return None
