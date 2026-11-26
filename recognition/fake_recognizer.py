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
    Türkçe büyük-küçük harf kurallarına (İ->i, I->ı, Ş->ş, Ğ->ğ, Ü->ü, Ö->ö, Ç->ç)
    uygun olarak metni küçük harfe çevirir, noktalama işaretlerini ve fazla boşlukları temizler.
    """
    if not raw_text:
        return NormalizedText(raw_text="", normalized_text="", language="tr")

    # Standart lower() öncesi Türkçe büyük harfleri dönüştür ve birleşik üst noktayı (\u0307) temizle
    translated = raw_text.translate(_TURKISH_CHAR_MAP).replace("\u0307", "")
    lowered = translated.lower().replace("\u0307", "")
    # Yalnızca harf, rakam ve boşluk bırak (noktalama ve alt çizgiyi boşluğa çevir)
    cleaned = re.sub(r"[^\w\s]|_", " ", lowered, flags=re.UNICODE)
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
        self._next_is_final: bool = True
        self._last_partial_text: str = ""

    def load_model(self, model_path: str) -> bool:
        if self._simulate_missing_model or not model_path:
            self._model_loaded = False
            return False
        self._model_loaded = True
        self._last_partial_text = ""
        return True

    def set_next_simulated_phrase(
        self,
        phrase: str,
        confidence: float = 0.92,
        is_final: bool = True,
    ) -> None:
        """Test veya sahte modda bir sonraki tanıma sonucunu belirler."""
        self._next_simulated_text = phrase
        self._next_confidence = confidence
        self._next_is_final = is_final

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
        if frame.is_silence or not frame.pcm_bytes:
            return None

        cleaned_text = self._next_simulated_text.strip()
        norm = self.normalize_turkish(cleaned_text)
        if not cleaned_text or not norm.normalized_text:
            return None

        if not self._next_is_final:
            if cleaned_text == self._last_partial_text:
                return None
            self._last_partial_text = cleaned_text
            return RecognitionResult(
                text=cleaned_text,
                is_final=False,
                confidence=None,
                normalized=norm,
                error_code=None,
                error_message=None,
            )

        self._last_partial_text = ""
        err = (
            ErrorCode.LOW_CONFIDENCE
            if self._next_confidence < self._min_confidence
            else None
        )
        return RecognitionResult(
            text=cleaned_text,
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
        text = self.DEFAULT_FIXTURE_MAP.get(basename, self._next_simulated_text).strip()
        norm = self.normalize_turkish(text)
        conf = 0.95
        err = ErrorCode.LOW_CONFIDENCE if conf < self._min_confidence else None
        return RecognitionResult(
            text=text,
            is_final=True,
            confidence=conf,
            normalized=norm,
            error_code=err,
            error_message="Ses yeterince net anlaşılamadı." if err else None,
        )

    def reset(self) -> None:
        self._last_partial_text = ""
        self._next_is_final = True
