"""
K2 — Sahte Konuşma Tanıyıcı (`recognition/fake_recognizer.py`)
Vosk model dosyası olmadan arayüz, sözleşme ve entegrasyon testlerini
çalıştırmak için kullanılan sahte sağlayıcı.
"""

from __future__ import annotations

import os
import re
from typing import Dict, Optional

from contracts.models import AudioFrame, ErrorCode, NormalizedText, RecognitionResult


_TURKISH_CHAR_MAP = str.maketrans(
    {
        "İ": "i",
        "I": "ı",
        "Ğ": "ğ",
        "Ü": "ü",
        "Ş": "ş",
        "Ö": "ö",
        "Ç": "ç",
    }
)


def normalize_turkish_text(raw_text: str) -> NormalizedText:
    """
    Türkçe büyük-küçük harf kurallarına (İ->i, I->ı) uygun olarak
    metni küçük harfe çevirir, noktalama işaretlerini ve fazla boşlukları temizler.
    """
    lowered = raw_text.translate(_TURKISH_CHAR_MAP).lower()
    # Yalnızca harf, rakam ve boşluk bırak
    cleaned = re.sub(r"[^\w\s]", " ", lowered, flags=re.UNICODE)
    collapsed = " ".join(cleaned.split())
    return NormalizedText(raw_text=raw_text, normalized_text=collapsed, language="tr")


class FakeSpeechRecognizer:
    """SpeechRecognizerProtocol sözleşmesini uygulayan sahte konuşma tanıyıcı."""

    DEFAULT_FIXTURE_MAP: Dict[str, str] = {
        "cmd_dinlemeyi_durdur.wav": "Dinlemeyi durdur.",
        "cmd_metni_kaydet.wav": "Metni kaydet",
        "unknown_bilgisayari_kapat.wav": "Bilgisayarı kapat",
    }

    def __init__(
        self,
        min_confidence: float = 0.65,
        simulate_missing_model: bool = False,
    ) -> None:
        self._min_confidence = min_confidence
        self._simulate_missing_model = simulate_missing_model
        self._model_loaded = not simulate_missing_model
        self._next_simulated_text: str = "dinlemeyi durdur"
        self._next_confidence: float = 0.92

    def load_model(self, model_path: str) -> bool:
        if self._simulate_missing_model or not model_path:
            self._model_loaded = False
            return False
        self._model_loaded = True
        return True

    def set_next_simulated_phrase(self, phrase: str, confidence: float = 0.92) -> None:
        """Test veya sahte modda bir sonraki tanıma sonucunu belirler."""
        self._next_simulated_text = phrase
        self._next_confidence = confidence

    def normalize_turkish(self, text: str) -> NormalizedText:
        return normalize_turkish_text(text)

    def accept_frame(self, frame: AudioFrame) -> Optional[RecognitionResult]:
        if not self._model_loaded:
            return RecognitionResult(
                text="",
                is_final=True,
                error_code=ErrorCode.MODEL_MISSING,
                error_message="Vosk Türkçe dil modeli bulunamadı. Lütfen README adımlarını izleyin.",
            )
        if frame.is_silence:
            return None

        norm = self.normalize_turkish(self._next_simulated_text)
        err = (
            ErrorCode.LOW_CONFIDENCE
            if self._next_confidence < self._min_confidence
            else None
        )
        return RecognitionResult(
            text=self._next_simulated_text,
            is_final=True,
            confidence=self._next_confidence,
            normalized=norm,
            error_code=err,
            error_message="Ses yeterince net anlaşılamadı." if err else None,
        )

    def transcribe_wav_file(self, wav_path: str) -> RecognitionResult:
        if not self._model_loaded:
            return RecognitionResult(
                text="",
                is_final=True,
                error_code=ErrorCode.MODEL_MISSING,
                error_message="Vosk Türkçe dil modeli bulunamadı.",
            )
        if not os.path.exists(wav_path):
            return RecognitionResult(
                text="",
                is_final=True,
                error_code=ErrorCode.MODEL_MISSING,
                error_message=f"Fixture WAV dosyası bulunamadı: {wav_path}",
            )

        basename = os.path.basename(wav_path)
        text = self.DEFAULT_FIXTURE_MAP.get(basename, self._next_simulated_text)
        norm = self.normalize_turkish(text)
        return RecognitionResult(
            text=text,
            is_final=True,
            confidence=0.95,
            normalized=norm,
        )

    def reset(self) -> None:
        pass
