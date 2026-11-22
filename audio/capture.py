"""
K1 — Gerçek Mikrofon Yakalama Modülü (`audio/capture.py`)
İzinli Sahip: Katılımcı 1 (K1)

Hafta 1-3 Görev Özeti:
- `sounddevice` ile 16 kHz mono PCM ses çerçeveleri (`AudioFrame`) üretmek.
- Sınırlı kuyruk (ring buffer) ile sessizlikte veri birikmesini önlemek.
- Cihaz yok, izin reddi ve cihaz kopması durumlarında standart `ErrorCode` üretmek.
- GİZLİLİK: Ham ses verisini asla diske (.wav / .pcm) yazmamak.
"""

from __future__ import annotations

import math
import struct
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from contracts.models import AudioConfig, AudioFrame, ErrorCode

try:
    import sounddevice as sd
except Exception:  # pragma: no cover - PortAudio / sounddevice kurulu olmayan ortamlar için
    sd = None  # type: ignore[assignment]


class MicrophoneAudioSource:
    """Gerçek mikrofon yakalama sınıfı (`AudioSourceProtocol` uyumlu)."""

    def __init__(
        self,
        config: Optional[AudioConfig] = None,
        silence_threshold: float = 0.01,
    ) -> None:
        self._config: AudioConfig = config or AudioConfig()
        self._silence_threshold: float = silence_threshold
        self._running: bool = False
        self._sequence_id: int = 0
        self._queue: Deque[AudioFrame] = deque(maxlen=self._config.queue_max_frames)
        self._condition: threading.Condition = threading.Condition()
        self._stream: Optional[Any] = None
        self._stream_error: Optional[ErrorCode] = None

    @property
    def is_running(self) -> bool:
        return self._running

    def list_devices(self) -> List[Dict[str, object]]:
        """Kullanılabilir ses giriş (mikrofon) cihazlarını listeler."""
        if sd is None:
            return []

        try:
            raw_devices = sd.query_devices()
        except Exception:
            return []

        if isinstance(raw_devices, dict):
            device_entries = [raw_devices]
        else:
            device_entries = list(raw_devices)

        input_devices: List[Dict[str, object]] = []
        for idx, dev in enumerate(device_entries):
            max_in = int(dev.get("max_input_channels", 0))
            if max_in > 0:
                device_index = int(dev.get("index", idx))
                input_devices.append(
                    {
                        "id": device_index,
                        "name": str(dev.get("name", f"Cihaz #{device_index}")),
                        "max_input_channels": max_in,
                        "default_samplerate": int(round(float(dev.get("default_samplerate", 16000)))),
                    }
                )
        return input_devices

    def start(self, config: Optional[AudioConfig] = None) -> None:
        """16 kHz mono PCM RawInputStream başlatır (idempotent)."""
        if self._running:
            return

        if config is not None:
            self._config = config
            with self._condition:
                self._queue = deque(maxlen=self._config.queue_max_frames)

        if sd is None:
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

        devices = self.list_devices()
        if not devices:
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

        target_device = self._resolve_device_id(self._config.device_id, devices)

        self._sequence_id = 0
        self._stream_error = None
        with self._condition:
            self._queue.clear()

        try:
            stream = sd.RawInputStream(
                samplerate=self._config.sample_rate,
                blocksize=self._config.frames_per_buffer,
                device=target_device,
                channels=self._config.channels,
                dtype="int16",
                callback=self._audio_callback,
                finished_callback=self._on_stream_finished,
            )
            stream.start()
        except PermissionError as exc:
            self._cleanup_stream()
            raise PermissionError(ErrorCode.MIC_PERMISSION_DENIED.value) from exc
        except Exception as exc:
            self._cleanup_stream()
            msg = str(exc).lower()
            if any(token in msg for token in ("permission", "access denied", "denied", "unauthorized")):
                raise PermissionError(ErrorCode.MIC_PERMISSION_DENIED.value) from exc
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value) from exc

        self._stream = stream
        self._running = True

    def stop(self) -> None:
        """Ses akışını güvenli biçimde durdurur ve bellekteki kuyruğu temizler."""
        self._running = False
        self._cleanup_stream()
        with self._condition:
            self._queue.clear()
            self._condition.notify_all()

    def read_frame(self, timeout_ms: int = 200) -> Optional[AudioFrame]:
        """Kuyruktan sıradaki `AudioFrame` nesnesini döndürür (yoksa `None`)."""
        if not self._running:
            return None

        deadline = time.monotonic() + max(0.0, timeout_ms / 1000.0)
        with self._condition:
            while not self._queue and self._running and self._stream_error is None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._condition.wait(timeout=remaining)

            if self._stream_error == ErrorCode.DEVICE_LOST or (
                self._running and self._stream is not None and not getattr(self._stream, "active", True)
            ):
                self._running = False
                self._cleanup_stream()
                self._queue.clear()
                raise RuntimeError(ErrorCode.DEVICE_LOST.value)

            if not self._running:
                return None

            if self._queue:
                return self._queue.popleft()

        return None

    def _resolve_device_id(
        self,
        requested_device: Optional[int | str],
        devices: List[Dict[str, object]],
    ) -> Optional[int | str]:
        """İstenen cihaz kimliğini veya adını doğrular; geçersizse `device_not_found` üretir."""
        if requested_device is None:
            return None

        if isinstance(requested_device, int):
            if any(d.get("id") == requested_device for d in devices):
                return requested_device
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

        if isinstance(requested_device, str):
            normalized_req = requested_device.strip().lower()
            if not normalized_req:
                return None
            for d in devices:
                dev_name = str(d.get("name", "")).lower()
                if normalized_req == dev_name or normalized_req in dev_name:
                    return int(d["id"])  # type: ignore[arg-type]
            raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

        raise RuntimeError(ErrorCode.DEVICE_NOT_FOUND.value)

    def _audio_callback(
        self,
        indata: Any,
        frames: int,
        time_info: Any,
        status: Any,
    ) -> None:
        """PortAudio arka plan iş parçacığından gelen ham PCM verisini bellekte `AudioFrame`'e dönüştürür."""
        del frames, time_info
        if not self._running:
            return

        if status:
            status_text = str(status).lower()
            if any(err_word in status_text for err_word in ("underflow", "aborted", "device", "disconnected")):
                with self._condition:
                    self._stream_error = ErrorCode.DEVICE_LOST
                    self._condition.notify_all()

        pcm_bytes = bytes(indata)
        rms_level = self._calculate_rms_int16(pcm_bytes)
        is_silence = rms_level < self._silence_threshold

        with self._condition:
            self._sequence_id += 1
            frame = AudioFrame(
                pcm_bytes=pcm_bytes,
                sample_rate=self._config.sample_rate,
                channels=self._config.channels,
                sequence_id=self._sequence_id,
                rms_level=rms_level,
                is_silence=is_silence,
            )
            # Sessizlikte kuyruk şişmesini önle (ardışık sessizlik çerçeveleri kuyruğu doldurmaz)
            if not (is_silence and len(self._queue) > 0 and self._queue[-1].is_silence):
                self._queue.append(frame)
                self._condition.notify_all()

    def _on_stream_finished(self) -> None:
        """Akış beklenmedik şekilde sonlandığında (örn. mikrofon çıkarıldığında) tetiklenir."""
        with self._condition:
            if self._running:
                self._stream_error = ErrorCode.DEVICE_LOST
            self._condition.notify_all()

    def _cleanup_stream(self) -> None:
        """PortAudio akış nesnesini güvenli biçimde kapatır ve serbest bırakır."""
        stream = self._stream
        self._stream = None
        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass

    @staticmethod
    def _calculate_rms_int16(pcm_bytes: bytes) -> float:
        """16-bit işaretli mono PCM bayt dizisinden normalize edilmiş [0.0, 1.0] RMS seviyesi hesaplar."""
        sample_count = len(pcm_bytes) // 2
        if sample_count <= 0:
            return 0.0

        samples = struct.unpack(f"<{sample_count}h", pcm_bytes[: sample_count * 2])
        sum_squares = sum(sample * sample for sample in samples)
        mean_square = sum_squares / sample_count
        rms = math.sqrt(mean_square) / 32768.0
        return round(min(1.0, max(0.0, rms)), 4)
