"""
BİLKOD Proje 3 — Konuşmayı Yazıya ve Güvenli Komuta Dönüştürme
Uygulama Giriş Noktası (`app.py`)
Sahip: Proje Lideri

Kullanım:
  python app.py           # Masaüstü arayüzünü başlatır
  python app.py --fake    # Sahte sağlayıcılarla (mikrofon/model olmadan) başlatır
  python app.py --check   # Arayüz açmadan sözleşme ve iskelet doğrulaması yapar
"""

from __future__ import annotations

import argparse
import sys
import tkinter as tk

from contracts.models import ALLOWED_COMMANDS
from core.config import load_settings
from core.controller import AppController
from ui.main_window import MainWindow


def run_self_check(controller: AppController) -> int:
    """İskeletin, sözleşmelerin ve 4 izinli komutun çalışırlığını doğrular."""
    print("=== BİLKOD Proje 3 | İskelet ve Sözleşme Doğrulaması ===")
    print(f"Model yolu ayarı : {controller.settings.model_path}")
    print(f"Ses örnekleme    : {controller.settings.sample_rate} Hz, {controller.settings.channels} kanal")
    print(f"İzinli komutlar  : {', '.join(ALLOWED_COMMANDS.keys())}")

    # 1. Sahte mikrofon başlat/durdur kontrolü
    controller.start_listening()
    frame = controller.audio_source.read_frame()
    assert frame is not None and frame.sample_rate == 16000, "AudioFrame üretilemedi!"
    controller.stop_listening()

    # 2. İzinli komut eşleme kontrolü
    intent_ok = controller.evaluate_text("Dinlemeyi durdur!", command_mode_enabled=True)
    assert intent_ok.matched is True, "İzinli komut eşleşmedi!"

    # 3. Bilinmeyen komut reddi kontrolü
    intent_bad = controller.evaluate_text("Bilgisayarı kapat", command_mode_enabled=True)
    assert intent_bad.matched is False, "Bilinmeyen komut yanlışlıkla eşleşti!"

    print("Durum: TÜM İSKELET VE SÖZLEŞME KONTROLLERİ BAŞARILI.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="BİLKOD Proje 3 — Konuşmayı Yazıya ve Güvenli Komuta Dönüştürme"
    )
    parser.add_argument(
        "--fake",
        action="store_true",
        help="Gerçek mikrofon/model olmadan sahte sağlayıcılarla çalıştır.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Arayüz açmadan sözleşme ve başlangıç doğrulamasını çalıştır.",
    )
    args = parser.parse_args(argv)

    settings = load_settings()
    controller = AppController(settings=settings)

    if args.check:
        return run_self_check(controller)

    root = tk.Tk()
    MainWindow(
        root=root,
        devices=controller.list_device_names(),
        on_start_listening=controller.start_listening,
        on_stop_listening=controller.stop_listening,
        on_test_phrase=lambda text, cmd_mode: controller.evaluate_text(
            text, command_mode_enabled=cmd_mode
        ),
    )
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
