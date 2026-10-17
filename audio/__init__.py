"""
K1 — Mikrofon ve Ses Paketi (`audio/`)
İzinli Sahip: Katılımcı 1 (K1)

GİZLİLİK KURALI:
Mikrofondan alınan ham ses verisi varsayılan olarak diske (.wav / .pcm) YAZILMAZ.
"""

from audio.fake_source import FakeAudioSource

__all__ = ["FakeAudioSource"]
