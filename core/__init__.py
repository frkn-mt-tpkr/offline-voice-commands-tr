"""
Lider — Çekirdek Bağlantı ve Koordinasyon Paketi (`core/`)
Sahip: Proje Lideri

Katılımcılar (K1, K2, K3) bu klasörü doğrudan değiştirmez.
"""

from core.config import AppSettings, load_settings
from core.controller import AppController

__all__ = ["AppController", "AppSettings", "load_settings"]
