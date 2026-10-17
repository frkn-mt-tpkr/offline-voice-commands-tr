"""
BİLKOD Proje 3 — Ortak Veri Sözleşmeleri (Contracts)
Sahip: Proje Lideri

ÖNEMLİ KURAL:
Katılımcılar (K1, K2, K3) bu dosyayı doğrudan değiştiremez.
Sözleşmede değişiklik ihtiyacı doğarsa Issue üzerinden proje liderinden karar istenir.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


CONTRACT_VERSION = "1.0.0"


class ErrorCode(str, Enum):
    """Standart hata ve durum kodları."""

    MIC_PERMISSION_DENIED = "mic_permission_denied"
    DEVICE_NOT_FOUND = "device_not_found"
    DEVICE_LOST = "device_lost"
    MODEL_MISSING = "model_missing"
    LOW_CONFIDENCE = "low_confidence"
    UNKNOWN_COMMAND = "unknown_command"


class ListeningState(str, Enum):
    """Uygulamanın dinleme ve işlem durumu."""

    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    ERROR = "error"


class CommandId(str, Enum):
    """İzin verilen (Allowlist) 4 güvenli uygulama içi komut kimliği."""

    STOP_LISTENING = "stop_listening"
    DELETE_LAST_SENTENCE = "delete_last_sentence"
    CLEAR_TEXT = "clear_text"
    SAVE_TEXT = "save_text"


@dataclass(frozen=True)
class AllowedCommandSpec:
    """Allowlist içindeki tek bir güvenli komutun tanımı."""

    command_id: CommandId
    phrase: str
    description: str
    requires_confirmation: bool


# Değişmez 4 izinli komut kataloğu (Allowlist)
ALLOWED_COMMANDS: Dict[str, AllowedCommandSpec] = {
    "dinlemeyi durdur": AllowedCommandSpec(
        command_id=CommandId.STOP_LISTENING,
        phrase="dinlemeyi durdur",
        description="Mikrofonu kapatır ve dinlemeyi bitirir.",
        requires_confirmation=False,
    ),
    "son cümleyi sil": AllowedCommandSpec(
        command_id=CommandId.DELETE_LAST_SENTENCE,
        phrase="son cümleyi sil",
        description="Metin alanındaki son nihai cümleyi kaldırır.",
        requires_confirmation=False,
    ),
    "metni temizle": AllowedCommandSpec(
        command_id=CommandId.CLEAR_TEXT,
        phrase="metni temizle",
        description="Metin alanının tamamını temizler.",
        requires_confirmation=True,
    ),
    "metni kaydet": AllowedCommandSpec(
        command_id=CommandId.SAVE_TEXT,
        phrase="metni kaydet",
        description="Metni kullanıcının seçtiği konuma .txt olarak kaydeder.",
        requires_confirmation=True,
    ),
}


def now_ms() -> int:
    """Geçerli zaman damgasını milisaniye cinsinden döndürür."""
    return int(time.time() * 1000)


@dataclass(frozen=True)
class AudioConfig:
    """K1 ses yakalama modülü yapılandırma sözleşmesi."""

    sample_rate: int = 16000
    channels: int = 1
    frame_duration_ms: int = 100
    queue_max_frames: int = 50
    device_id: Optional[int | str] = None

    @property
    def frames_per_buffer(self) -> int:
        return int(self.sample_rate * (self.frame_duration_ms / 1000.0))


@dataclass(frozen=True)
class AudioFrame:
    """K1 tarafından üretilen ve K2 tarafından tüketilen 16 kHz mono PCM ses çerçevesi."""

    pcm_bytes: bytes
    sample_rate: int = 16000
    channels: int = 1
    sequence_id: int = 0
    rms_level: float = 0.0
    is_silence: bool = False
    timestamp_ms: int = field(default_factory=now_ms)


@dataclass(frozen=True)
class NormalizedText:
    """K2 tarafından Türkçe kurallarına göre normalize edilmiş metin sözleşmesi."""

    raw_text: str
    normalized_text: str
    language: str = "tr"


@dataclass(frozen=True)
class RecognitionResult:
    """K2 konuşma tanıma modülü çıktı sözleşmesi."""

    text: str
    is_final: bool = True
    confidence: Optional[float] = None
    normalized: Optional[NormalizedText] = None
    error_code: Optional[ErrorCode] = None
    error_message: Optional[str] = None
    timestamp_ms: int = field(default_factory=now_ms)

    @property
    def is_error(self) -> bool:
        return self.error_code is not None


@dataclass(frozen=True)
class CommandIntent:
    """K3 komut eşleme (matcher) modülü çıktı sözleşmesi."""

    matched: bool
    raw_text: str
    normalized_text: str
    command_id: Optional[CommandId] = None
    requires_confirmation: bool = False
    confidence: Optional[float] = None
    error_code: Optional[ErrorCode] = None
    reason: str = ""
    timestamp_ms: int = field(default_factory=now_ms)


@dataclass(frozen=True)
class ConfirmationRequest:
    """Riskli/kalıcı komutlar ('metni temizle', 'metni kaydet') için onay isteği."""

    request_id: str
    intent: CommandIntent
    prompt_message: str
    timestamp_ms: int = field(default_factory=now_ms)


@dataclass(frozen=True)
class CommandResult:
    """K3 güvenli komut yürütücü (executor) sonuç sözleşmesi."""

    command_id: Optional[CommandId]
    executed: bool
    cancelled: bool = False
    message: str = ""
    error_code: Optional[ErrorCode] = None
    timestamp_ms: int = field(default_factory=now_ms)


@dataclass(frozen=True)
class AppEvent:
    """Modüller arası ve UI güncellemeleri için ortak olay zarfı."""

    event_type: str
    source: str
    payload: Any = None
    error_code: Optional[ErrorCode] = None
    timestamp_ms: int = field(default_factory=now_ms)
