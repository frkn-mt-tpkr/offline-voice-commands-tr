"""
K3 — Kullanıcı Arayüzü Paketi (`ui/`)
İzinli Sahip: Katılımcı 3 (K3)

MİMARİ KURAL:
Arayüz doğrudan mikrofon (`sounddevice`) veya model (`vosk`) koduna bağlanmaz;
yalnızca ortak sözleşmeleri (`contracts/`) ve denetleyici geri çağrılarını kullanır.
"""

from ui.main_window import MainWindow

__all__ = ["MainWindow"]
