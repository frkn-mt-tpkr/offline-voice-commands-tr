"""
K1 — Sahte Mikrofon Sağlayıcısı (`audio/fake_source.py`)
Gerçek mikrofon donanımı olmadan `AudioFrame` akışını ve cihaz hatalarını
test etmek için kullanılan sahte sağlayıcı.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Optional

from contracts.models import AudioConfig, AudioFrame, ErrorCode


class FakeAudioSource:
    """AudioSourceProtocol sözleşmesini uygulayan sahte mikrofon kaynağı."""

    def __init__(
        self,
        config: Optional[AudioConfig] = None,
        simulated_error: Optional[ErrorCode] = None,
    ) -> None:
        self._config = config or AudioConfig()
        self._simulated_error = simulated_error
        self._running = False
        self._sequence_id = 0
        self._queue: Deque[AudioFrame] = deque(maxlen=self._config.queue_max_frames)

    @property
    def is_running(self) -> bool:
        return self._running

    def list_devices(self) -> List[Dict[str, object]]:
        if self._simulated_error == ErrorCode.DEVICE_NOT_FOUND:
            return []
        return [
            {
                "id": 0,
                "name": "Sahte Mikrofon (16 kHz Mono Test Kaynağı)",
                "max_input_channels": 1,
                "default_samplerate": 16000,
            }
        ]

    def start(self, config: Optional[AudioConfig] = None) -> None:
        if config is not None:
            self._config = config
            self._queue = deque(maxlen=self._config.queue_max_frames)

        if self._simulated_error == ErrorCode.MIC_PERMISSION_DENIED:
            raise PermissionError(ErrorCode.MIC_PERMISSION_DENIED.value)
        if self._simulated_error == ErrorCode.DEVICE_NOT_FOUND:
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

        # İki kez start çağrıldığında ikinci akış açılmaz (idempotent)
        if self._running:
            return

        self._running = True
        self._sequence_id = 0
        self._enqueue_sample_frame(is_silence=False, rms_level=0.25)

    def stop(self) -> None:
        self._running = False
        self._queue.clear()

    def push_fake_frame(self, pcm_bytes: Optional[bytes] = None, is_silence: bool = False) -> AudioFrame:
        """Test amacıyla kuyruğa tek bir sahte AudioFrame ekler."""
        return self._enqueue_sample_frame(
            pcm_bytes=pcm_bytes,
            is_silence=is_silence,
            rms_level=0.0 if is_silence else 0.3,
        )

    def read_frame(self, timeout_ms: int = 200) -> Optional[AudioFrame]:
        if not self._running:
            return None
        if self._simulated_error == ErrorCode.DEVICE_LOST:
            self.stop()
            raise RuntimeError(ErrorCode.DEVICE_LOST.value)
        if not self._queue:
            return self._enqueue_sample_frame(is_silence=True, rms_level=0.01)
        return self._queue.popleft()

    def _enqueue_sample_frame(
        self,
        pcm_bytes: Optional[bytes] = None,
        is_silence: bool = False,
        rms_level: float = 0.0,
    ) -> AudioFrame:
        self._sequence_id += 1
        byte_count = self._config.frames_per_buffer * 2  # 16-bit mono = 2 byte/sample
        raw = pcm_bytes if pcm_bytes is not None else (b"\x00" * byte_count)
        frame = AudioFrame(
            pcm_bytes=raw,
            sample_rate=self._config.sample_rate,
            channels=self._config.channels,
            sequence_id=self._sequence_id,
            rms_level=rms_level,
            is_silence=is_silence,
        )
        # Sessizlikte kuyruk şişmesini önle (Hafta 2 K1 kuralı)
        if not (is_silence and len(self._queue) > 0 and self._queue[-1].is_silence):
            self._queue.append(frame)
        return frame
