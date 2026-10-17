"""
Lider — Uygulama Koordinatörü / Glue Code (`core/controller.py`)
Sahip: Proje Lideri

`audio/` (K1), `recognition/` (K2), `commands/` (K3) ve `ui/` (K3)
modüllerini ortak sözleşmeler (`contracts/`) üzerinden birbirine bağlar.
"""

from __future__ import annotations

from typing import List, Optional

from audio.fake_source import FakeAudioSource
from commands.executor import SafeCommandExecutor
from commands.matcher import AllowlistCommandMatcher
from contracts.interfaces import (
    AudioSourceProtocol,
    CommandExecutorProtocol,
    CommandMatcherProtocol,
    SpeechRecognizerProtocol,
)
from contracts.models import (
    AppEvent,
    CommandId,
    CommandIntent,
    CommandResult,
    ListeningState,
)
from core.config import AppSettings
from recognition.fake_recognizer import FakeSpeechRecognizer


class AppController:
    """Modüller arası veri akışını ve güvenli komut yürütmesini koordine eder."""

    def __init__(
        self,
        settings: AppSettings,
        audio_source: Optional[AudioSourceProtocol] = None,
        recognizer: Optional[SpeechRecognizerProtocol] = None,
        matcher: Optional[CommandMatcherProtocol] = None,
        executor: Optional[CommandExecutorProtocol] = None,
    ) -> None:
        self.settings = settings
        self.audio_source: AudioSourceProtocol = audio_source or FakeAudioSource(
            settings.to_audio_config()
        )
        self.recognizer: SpeechRecognizerProtocol = recognizer or FakeSpeechRecognizer(
            min_confidence=settings.min_confidence
        )
        self.matcher: CommandMatcherProtocol = matcher or AllowlistCommandMatcher(
            min_confidence=settings.min_confidence
        )
        self.executor: CommandExecutorProtocol = executor or SafeCommandExecutor()

        self.state = ListeningState.IDLE
        self.event_log: List[AppEvent] = []
        self._register_default_safe_actions()

    def _register_default_safe_actions(self) -> None:
        """4 izinli komut için varsayılan güvenli uygulama içi callback'leri bağlar."""
        self.executor.register_action(
            CommandId.STOP_LISTENING,
            lambda: self._action_stop_listening(),
        )
        self.executor.register_action(
            CommandId.DELETE_LAST_SENTENCE,
            lambda: "Son nihai cümle metin alanından kaldırıldı.",
        )
        self.executor.register_action(
            CommandId.CLEAR_TEXT,
            lambda: "Metin alanının tamamı güvenli biçimde temizlendi.",
        )
        self.executor.register_action(
            CommandId.SAVE_TEXT,
            lambda: "Metin kullanıcının seçtiği konuma .txt olarak kaydedildi.",
        )

    def _action_stop_listening(self) -> str:
        self.stop_listening()
        return "Dinleme durduruldu ve mikrofon kapatıldı."

    def list_device_names(self) -> List[str]:
        devices = self.audio_source.list_devices()
        if not devices:
            return ["Mikrofon bulunamadı"]
        return [str(d.get("name", f"Cihaz #{d.get('id', 0)}")) for d in devices]

    def start_listening(self) -> None:
        self.audio_source.start(self.settings.to_audio_config())
        self.state = ListeningState.LISTENING
        self.event_log.append(
            AppEvent(event_type="listening_started", source="controller")
        )

    def stop_listening(self) -> None:
        self.audio_source.stop()
        self.state = ListeningState.IDLE
        self.event_log.append(
            AppEvent(event_type="listening_stopped", source="controller")
        )

    def evaluate_text(
        self,
        raw_text: str,
        command_mode_enabled: bool = True,
        confidence: Optional[float] = 0.95,
    ) -> CommandIntent:
        """Gelen metni K2 normalizasyonundan geçirip K3 allowlist eşleyicisine iletir."""
        norm = self.recognizer.normalize_turkish(raw_text)
        intent = self.matcher.match(
            normalized=norm,
            command_mode_enabled=command_mode_enabled,
            confidence=confidence,
        )
        self.event_log.append(
            AppEvent(event_type="intent_evaluated", source="controller", payload=intent)
        )
        return intent

    def execute_intent(self, intent: CommandIntent, confirmed: bool = False) -> CommandResult:
        """Eşleşmiş niyeti güvenli yürütücü üzerinden çalıştırır."""
        result = self.executor.execute(intent, confirmed=confirmed)
        self.event_log.append(
            AppEvent(event_type="command_executed", source="controller", payload=result)
        )
        return result
