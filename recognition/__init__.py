"""
K2 — Çevrimdışı Konuşma Tanıma Paketi (`recognition/`)
İzinli Sahip: Katılımcı 2 (K2)

KURAL:
Konuşma tanıma tamamen çevrimdışı (internetsiz) çalışır.
Model yolu sabit yazılmaz; yapılandırmadan okunur.
"""

from recognition.fake_recognizer import FakeSpeechRecognizer, normalize_turkish_text

__all__ = ["FakeSpeechRecognizer", "normalize_turkish_text"]
