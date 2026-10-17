"""
K3 — Güvenli Uygulama İçi Komut Yürütücü (`commands/executor.py`)
İzinli Sahip: Katılımcı 3 (K3)

GÜVENLİK KURALI:
Bu modül işletim sistemi komutu çalıştırmaz. Yalnızca uygulama içi
kayıtlı Python fonksiyonlarını (callback) çağırır.
"""

from __future__ import annotations

from typing import Callable, Dict

from contracts.models import CommandId, CommandIntent, CommandResult, ErrorCode


class SafeCommandExecutor:
    """Yalnızca `CommandId` enum değerlerine bağlı güvenli Python fonksiyonlarını çalıştırır."""

    def __init__(self) -> None:
        self._actions: Dict[CommandId, Callable[[], str]] = {}

    def register_action(self, command_id: CommandId, callback: Callable[[], str]) -> None:
        if not isinstance(command_id, CommandId):
            raise ValueError("Yalnızca CommandId enum değerleri kaydedilebilir.")
        self._actions[command_id] = callback

    def execute(self, intent: CommandIntent, confirmed: bool = False) -> CommandResult:
        if not intent.matched or intent.command_id is None:
            return CommandResult(
                command_id=None,
                executed=False,
                error_code=intent.error_code or ErrorCode.UNKNOWN_COMMAND,
                message=intent.reason or "Bilinmeyen veya eşleşmeyen komut çalıştırılamaz.",
            )

        if intent.requires_confirmation and not confirmed:
            return CommandResult(
                command_id=intent.command_id,
                executed=False,
                cancelled=True,
                message=f"'{intent.normalized_text}' komutu onay verilmediği için çalıştırılmadı.",
            )

        callback = self._actions.get(intent.command_id)
        if callback is None:
            return CommandResult(
                command_id=intent.command_id,
                executed=False,
                message=f"'{intent.command_id.value}' için tanımlı uygulama içi eylem bulunamadı.",
            )

        feedback = callback()
        return CommandResult(
            command_id=intent.command_id,
            executed=True,
            message=feedback,
        )
