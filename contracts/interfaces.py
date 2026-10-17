"""
BİLKOD Proje 3 — Modül Arayüz Protokolleri (Interfaces)
Sahip: Proje Lideri

Her gerçek sağlayıcının (mikrofon, Vosk tanıyıcı, komut eşleyici/yürütücü)
yanında aynı protokolü uygulayan bir sahte (fake) sağlayıcı bulunur.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Protocol

from contracts.models import (
    AudioConfig,
    AudioFrame,
    CommandId,
    CommandIntent,
    CommandResult,
    NormalizedText,
    RecognitionResult,
)


class AudioSourceProtocol(Protocol):
    """K1 ses kaynağı arayüzü (Gerçek mikrofon ve Sahte mikrofon bu arayüzü uygular)."""

    def list_devices(self) -> List[Dict[str, object]]:
        """Kullanılabilir ses giriş cihazlarını listeler."""
        ...

    def start(self, config: Optional[AudioConfig] = None) -> None:
        """Ses çerçevesi akışını başlatır."""
        ...

    def stop(self) -> None:
        """Ses akışını güvenli biçimde durdurur ve kaynakları serbest bırakır."""
        ...

    def read_frame(self, timeout_ms: int = 200) -> Optional[AudioFrame]:
        """Kuyruktan sıradaki ses çerçevesini döndürür (yoksa None)."""
        ...

    @property
    def is_running(self) -> bool:
        """Akışın aktif olup olmadığını döndürür."""
        ...


class SpeechRecognizerProtocol(Protocol):
    """K2 çevrimdışı konuşma tanıma arayüzü."""

    def load_model(self, model_path: str) -> bool:
        """Vosk Türkçe modelini yükler ve doğrular."""
        ...

    def accept_frame(self, frame: AudioFrame) -> Optional[RecognitionResult]:
        """Canlı ses çerçevesini işler; kısmi veya nihai RecognitionResult döndürür."""
        ...

    def transcribe_wav_file(self, wav_path: str) -> RecognitionResult:
        """Fixture WAV dosyasını çevrimdışı olarak metne çevirir."""
        ...

    def normalize_turkish(self, text: str) -> NormalizedText:
        """Türkçe İ/ı dönüşümü, küçük harf ve noktalama temizliği yapar."""
        ...

    def reset(self) -> None:
        """Tanıyıcı durumunu sıfırlar."""
        ...


class CommandMatcherProtocol(Protocol):
    """K3 güvenli komut eşleme (allowlist) arayüzü."""

    def match(
        self,
        normalized: NormalizedText,
        command_mode_enabled: bool = True,
        confidence: Optional[float] = None,
    ) -> CommandIntent:
        """Normalize edilmiş metni yalnızca 4 izinli komutla karşılaştırır."""
        ...


class CommandExecutorProtocol(Protocol):
    """K3 güvenli uygulama içi komut yürütme arayüzü (shell/subprocess YASAKTIR)."""

    def register_action(self, command_id: CommandId, callback: Callable[[], str]) -> None:
        """İzinli bir CommandId için uygulama içi güvenli Python fonksiyonu kaydeder."""
        ...

    def execute(self, intent: CommandIntent, confirmed: bool = False) -> CommandResult:
        """Eşleşmiş ve (gerekiyorsa) onaylanmış komutu çalıştırır."""
        ...
