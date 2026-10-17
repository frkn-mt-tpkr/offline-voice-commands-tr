"""
K3 — Sabit İzin Listesi (Allowlist) Komut Eşleyici (`commands/matcher.py`)
İzinli Sahip: Katılımcı 3 (K3)
"""

from __future__ import annotations

from typing import Optional

from contracts.models import (
    ALLOWED_COMMANDS,
    CommandIntent,
    ErrorCode,
    NormalizedText,
)


class AllowlistCommandMatcher:
    """
    Normalize edilmiş Türkçe metni yalnızca 4 izinli komutla (Allowlist) eşleştirir.
    Bilinmeyen veya düşük güvenli cümleler ASLA komuta dönüştürülmez.
    """

    def __init__(self, min_confidence: float = 0.65) -> None:
        self._min_confidence = min_confidence

    def match(
        self,
        normalized: NormalizedText,
        command_mode_enabled: bool = True,
        confidence: Optional[float] = None,
    ) -> CommandIntent:
        if not command_mode_enabled:
            return CommandIntent(
                matched=False,
                raw_text=normalized.raw_text,
                normalized_text=normalized.normalized_text,
                confidence=confidence,
                reason="Komut modu kapalı (yalnızca dikte modu aktif).",
            )

        if confidence is not None and confidence < self._min_confidence:
            return CommandIntent(
                matched=False,
                raw_text=normalized.raw_text,
                normalized_text=normalized.normalized_text,
                confidence=confidence,
                error_code=ErrorCode.LOW_CONFIDENCE,
                reason="Güven skoru eşik değerinin altında; komut çalıştırılmadı.",
            )

        candidate = normalized.normalized_text.strip()
        spec = ALLOWED_COMMANDS.get(candidate)
        if spec is None:
            return CommandIntent(
                matched=False,
                raw_text=normalized.raw_text,
                normalized_text=candidate,
                confidence=confidence,
                error_code=ErrorCode.UNKNOWN_COMMAND,
                reason="Anlaşılamadı: İfade izinli 4 komuttan biriyle eşleşmedi.",
            )

        return CommandIntent(
            matched=True,
            raw_text=normalized.raw_text,
            normalized_text=candidate,
            command_id=spec.command_id,
            requires_confirmation=spec.requires_confirmation,
            confidence=confidence,
            reason=f"İzinli komut eşleşti: {spec.phrase}",
        )
