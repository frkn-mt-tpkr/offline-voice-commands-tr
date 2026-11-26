"""
K2 — Çevrimdışı Vosk Konuşma Tanıma Sağlayıcısı (`recognition/vosk_recognizer.py`)
İzinli Sahip: Katılımcı 2 (K2)

Hafta 1-3 Görev Özeti:
- Vosk Türkçe modelini yapılandırma üzerinden yüklemek (sabit model yolu kullanılmaz).
- Model klasörü yoksa çökmeden `ErrorCode.MODEL_MISSING` döndürmek.
- 3 fixture WAV dosyasını ve canlı `AudioFrame` akışını kısmi/nihai metne çevirmek.
- Türkçe normalizasyon (`İ->i`, `I->ı`) ve düşük güven (`low_confidence`) kontrolü yapmak.
"""

from __future__ import annotations

import json
import os
import wave
from typing import Any, Dict, List, Optional

from contracts.models import (
    AudioFrame,
    ErrorCode,
    NormalizedText,
    RecognitionResult,
)
from recognition.fake_recognizer import normalize_turkish_text

try:
    from vosk import KaldiRecognizer, Model, SetLogLevel

    SetLogLevel(-1)
    _VOSK_AVAILABLE = True
except Exception:  # pragma: no cover
    KaldiRecognizer = None  # type: ignore[assignment]
    Model = None  # type: ignore[assignment]
    _VOSK_AVAILABLE = False

_DEFAULT_RELATIVE_MODEL_DIR = os.path.join("models", "vosk-model-small-tr-0.3")


class VoskSpeechRecognizer:
    """SpeechRecognizerProtocol sözleşmesini uygulayan gerçek Vosk çevrimdışı konuşma tanıyıcı."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        sample_rate: int = 16000,
        min_confidence: float = 0.65,
    ) -> None:
        self._model_path: str = (
            model_path
            if model_path is not None
            else os.environ.get("VOSK_MODEL_PATH", _DEFAULT_RELATIVE_MODEL_DIR)
        )
        self._sample_rate: int = sample_rate
        self._min_confidence: float = min_confidence
        self._model: Any = None
        self._recognizer: Any = None
        self._loaded: bool = False
        self._last_partial_text: str = ""

    @property
    def is_loaded(self) -> bool:
        """Modelin başarıyla yüklenip yüklenmediğini döndürür."""
        return self._loaded

    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Vosk Türkçe modelini verilen veya yapılandırılan yoldan yükler ve doğrular."""
        if model_path is not None:
            self._model_path = model_path

        target_path = (self._model_path or "").strip()
        if not target_path or not _VOSK_AVAILABLE:
            self._loaded = False
            self._model = None
            self._recognizer = None
            self._last_partial_text = ""
            return False

        if not os.path.isdir(target_path):
            self._loaded = False
            self._model = None
            self._recognizer = None
            self._last_partial_text = ""
            return False

        try:
            self._model = Model(target_path)
            self._recognizer = KaldiRecognizer(
                self._model, float(self._sample_rate)
            )
            if hasattr(self._recognizer, "SetWords"):
                self._recognizer.SetWords(True)
            self._loaded = True
            self._last_partial_text = ""
            return True
        except Exception:
            self._loaded = False
            self._model = None
            self._recognizer = None
            self._last_partial_text = ""
            return False

    def _ensure_model_loaded(self) -> bool:
        """Model yüklü değilse mevcut model yolu ile yüklemeyi dener."""
        if self._loaded and self._model is not None and self._recognizer is not None:
            return True
        if self._model_path:
            return self.load_model(self._model_path)
        return False

    def _missing_model_result(self, detail: Optional[str] = None) -> RecognitionResult:
        msg = (
            detail
            or "Vosk Türkçe dil modeli bulunamadı. Lütfen README adımlarını izleyin."
        )
        return RecognitionResult(
            text="",
            is_final=True,
            confidence=None,
            normalized=None,
            error_code=ErrorCode.MODEL_MISSING,
            error_message=msg,
        )

    @staticmethod
    def _extract_word_confidences(payload: Dict[str, Any]) -> List[float]:
        words = payload.get("result")
        if not isinstance(words, list):
            return []
        confidences: List[float] = []
        for item in words:
            if isinstance(item, dict) and "conf" in item:
                try:
                    confidences.append(float(item["conf"]))
                except (TypeError, ValueError):
                    continue
        return confidences

    def _build_recognition_result(
        self,
        raw_text: str,
        is_final: bool,
        confidences: Optional[List[float]] = None,
    ) -> RecognitionResult:
        cleaned_raw = raw_text.strip()
        norm = self.normalize_turkish(cleaned_raw)

        avg_conf: Optional[float] = None
        if confidences:
            avg_conf = round(sum(confidences) / len(confidences), 4)
        elif is_final and cleaned_raw:
            avg_conf = 1.0

        err_code: Optional[ErrorCode] = None
        err_msg: Optional[str] = None
        if (
            is_final
            and cleaned_raw
            and avg_conf is not None
            and avg_conf < self._min_confidence
        ):
            err_code = ErrorCode.LOW_CONFIDENCE
            err_msg = (
                f"Ses yeterince net anlaşılamadı "
                f"(güven={avg_conf:.2f} < eşik={self._min_confidence:.2f})."
            )

        return RecognitionResult(
            text=cleaned_raw,
            is_final=is_final,
            confidence=avg_conf,
            normalized=norm,
            error_code=err_code,
            error_message=err_msg,
        )

    def accept_frame(self, frame: AudioFrame) -> Optional[RecognitionResult]:
        """Canlı ses çerçevesini işler; kısmi veya nihai RecognitionResult döndürür."""
        if not self._ensure_model_loaded():
            return self._missing_model_result()

        if not frame.pcm_bytes:
            return None

        try:
            is_endpoint = bool(self._recognizer.AcceptWaveform(frame.pcm_bytes))
            if not is_endpoint and len(frame.pcm_bytes) < (self._sample_rate // 10) * 2:
                # Kısa son çerçeve (ör. WAV akışı sonu) sonrasında Kaldi endpoint algılaması için
                # sessizlik tamponu besle
                if self._recognizer.AcceptWaveform(b"\x00" * 16000):
                    is_endpoint = True
            if is_endpoint:
                self._last_partial_text = ""
                payload = json.loads(self._recognizer.Result() or "{}")
                text = str(payload.get("text", "")).strip()
                if not text:
                    return None
                norm_check = self.normalize_turkish(text)
                if not norm_check.normalized_text:
                    return None
                confs = self._extract_word_confidences(payload)
                return self._build_recognition_result(
                    raw_text=text,
                    is_final=True,
                    confidences=confs,
                )

            if frame.is_silence:
                return None

            partial_payload = json.loads(self._recognizer.PartialResult() or "{}")
            partial_text = str(partial_payload.get("partial", "")).strip()
            if not partial_text or partial_text == self._last_partial_text:
                return None

            norm_partial = self.normalize_turkish(partial_text)
            if not norm_partial.normalized_text:
                return None

            self._last_partial_text = partial_text
            return self._build_recognition_result(
                raw_text=partial_text,
                is_final=False,
                confidences=None,
            )
        except Exception as exc:
            self._last_partial_text = ""
            return RecognitionResult(
                text="",
                is_final=True,
                error_code=ErrorCode.LOW_CONFIDENCE,
                error_message=f"Ses çerçevesi işlenemedi: {exc}",
            )

    def transcribe_wav_file(self, wav_path: str) -> RecognitionResult:
        """Fixture WAV dosyasını çevrimdışı olarak metne çevirir."""
        if not self._ensure_model_loaded():
            return self._missing_model_result()

        if not wav_path or not os.path.isfile(wav_path):
            return self._missing_model_result(
                f"Fixture WAV dosyası bulunamadı: {wav_path}"
            )

        try:
            with wave.open(wav_path, "rb") as wf:
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                frame_rate = wf.getframerate()

                if channels != 1 or sample_width != 2:
                    return RecognitionResult(
                        text="",
                        is_final=True,
                        error_code=ErrorCode.LOW_CONFIDENCE,
                        error_message=(
                            f"Desteklenmeyen WAV formatı (kanal={channels}, "
                            f"örnek genişliği={sample_width} bayt). 16-bit mono PCM bekleniyor."
                        ),
                    )

                file_recognizer = KaldiRecognizer(self._model, float(frame_rate))
                if hasattr(file_recognizer, "SetWords"):
                    file_recognizer.SetWords(True)

                text_segments: List[str] = []
                all_confidences: List[float] = []

                while True:
                    pcm_chunk = wf.readframes(4000)
                    if not pcm_chunk:
                        break
                    if file_recognizer.AcceptWaveform(pcm_chunk):
                        part_payload = json.loads(file_recognizer.Result() or "{}")
                        part_text = str(part_payload.get("text", "")).strip()
                        if part_text:
                            text_segments.append(part_text)
                        all_confidences.extend(
                            self._extract_word_confidences(part_payload)
                        )

                final_payload = json.loads(file_recognizer.FinalResult() or "{}")
                final_text = str(final_payload.get("text", "")).strip()
                if final_text:
                    text_segments.append(final_text)
                all_confidences.extend(self._extract_word_confidences(final_payload))

                full_text = " ".join(text_segments).strip()
                return self._build_recognition_result(
                    raw_text=full_text,
                    is_final=True,
                    confidences=all_confidences,
                )
        except Exception as exc:
            return self._missing_model_result(
                f"WAV dosyası çözümlenirken hata oluştu: {exc}"
            )

    def normalize_turkish(self, text: str) -> NormalizedText:
        """Türkçe İ/ı dönüşümü, küçük harf ve noktalama temizliği yapar."""
        return normalize_turkish_text(text)

    def reset(self) -> None:
        """Tanıyıcı durumunu ve son kısmi metin tamponunu sıfırlar."""
        self._last_partial_text = ""
        if self._loaded and self._recognizer is not None:
            if hasattr(self._recognizer, "Reset"):
                self._recognizer.Reset()
            elif self._model is not None:
                self._recognizer = KaldiRecognizer(
                    self._model, float(self._sample_rate)
                )
                if hasattr(self._recognizer, "SetWords"):
                    self._recognizer.SetWords(True)
