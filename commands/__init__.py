"""
K3 — Güvenli Komut Eşleme ve Yürütme Paketi (`commands/`)
İzinli Sahip: Katılımcı 3 (K3)

GÜVENLİK KURALI:
- Yalnızca `ALLOWED_COMMANDS` içindeki 4 sabit ifade komuta dönüşebilir.
- `subprocess`, `os.system`, `shell=True`, `eval`, `exec` kesinlikle YASAKTIR.
"""

from commands.executor import SafeCommandExecutor
from commands.matcher import AllowlistCommandMatcher

__all__ = ["AllowlistCommandMatcher", "SafeCommandExecutor"]
