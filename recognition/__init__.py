"""
K2 — Çevrimdışı Konuşma Tanıma Paketi (`recognition/`)
İzinli Sahip: Katılımcı 2 (K2)

KURAL:
Konuşma tanıma tamamen çevrimdışı (internetsiz) çalışır.
Model yolu sabit yazılmaz; yapılandırmadan okunur.
"""

from recognition.fake_recognizer import FakeSpeechRecognizer, normalize_turkish_text
from recognition.vosk_recognizer import VoskSpeechRecognizer

__all__ = [
    "FakeSpeechRecognizer",
    "VoskSpeechRecognizer",
    "normalize_turkish_text",
]
