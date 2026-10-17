"""
K2 — Çevrimdışı Vosk Konuşma Tanıma İskeleti (`recognition/vosk_recognizer.py`)
İzinli Sahip: Katılımcı 2 (K2)

Hafta 1-3 Görev Özeti:
- Vosk Türkçe modelini (`models/vosk-model-small-tr-0.3`) yapılandırma üzerinden yüklemek.
- Model klasörü yoksa çökmeden `ErrorCode.MODEL_MISSING` döndürmek.
- 3 fixture WAV dosyasını ve canlı `AudioFrame` akışını kısmi/nihai metne çevirmek.
- Türkçe normalizasyon (`İ->i`, `I->ı`) ve düşük güven (`low_confidence`) kontrolü yapmak.
"""

from __future__ import annotations

from typing import Optional

from contracts.models import AudioFrame, NormalizedText, RecognitionResult
from recognition.fake_recognizer import normalize_turkish_text


class VoskSpeechRecognizer:
    """Gerçek Vosk çevrimdışı konuşma tanıyıcı (K2 tarafından Hafta 1'de tamamlanacaktır)."""

    def __init__(self, model_path: str, sample_rate: int = 16000) -> None:
        self._model_path = model_path
        self._sample_rate = sample_rate
        self._loaded = False

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """TODO (K2 - Hafta 1): Vosk Model ve KaldiRecognizer nesnelerini başlat."""
        raise NotImplementedError("K2 Hafta 1 görevinde uygulanacaktır.")

    def accept_frame(self, frame: AudioFrame) -> Optional[RecognitionResult]:
        """TODO (K2 - Hafta 2): Canlı AudioFrame'i modele besle ve kısmi/nihai sonuç üret."""
        raise NotImplementedError("K2 Hafta 2 görevinde uygulanacaktır.")

    def transcribe_wav_file(self, wav_path: str) -> RecognitionResult:
        """TODO (K2 - Hafta 1): Fixture WAV dosyasını çevrimdışı olarak metne çevir."""
        raise NotImplementedError("K2 Hafta 1 görevinde uygulanacaktır.")

    def normalize_turkish(self, text: str) -> NormalizedText:
        return normalize_turkish_text(text)

    def reset(self) -> None:
        pass
