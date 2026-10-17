"""
Lider — Yapılandırma Yükleyici (`core/config.py`)
Model yolu ve ses ayarlarını sabit kodlamadan (hardcoded path olmadan)
`config.local.json`, `config.example.json` veya ortam değişkenlerinden okur.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from contracts.models import AudioConfig


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class AppSettings:
    model_path: str = "models/vosk-model-small-tr-0.3"
    sample_rate: int = 16000
    channels: int = 1
    frame_duration_ms: int = 100
    queue_max_frames: int = 50
    min_confidence: float = 0.65
    default_command_mode: bool = False
    use_fake_providers_by_default: bool = False

    def to_audio_config(self) -> AudioConfig:
        return AudioConfig(
            sample_rate=self.sample_rate,
            channels=self.channels,
            frame_duration_ms=self.frame_duration_ms,
            queue_max_frames=self.queue_max_frames,
        )


def load_settings(root_dir: Path = PROJECT_ROOT) -> AppSettings:
    """Önce `config.local.json`, yoksa `config.example.json` ve `VOSK_MODEL_PATH` okur."""
    local_cfg = root_dir / "config.local.json"
    example_cfg = root_dir / "config.example.json"

    raw_data = {}
    target_file = local_cfg if local_cfg.exists() else example_cfg
    if target_file.exists():
        with open(target_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

    env_model_path = os.environ.get("VOSK_MODEL_PATH")
    model_path = env_model_path or raw_data.get(
        "model_path", "models/vosk-model-small-tr-0.3"
    )

    return AppSettings(
        model_path=str(model_path),
        sample_rate=int(raw_data.get("sample_rate", 16000)),
        channels=int(raw_data.get("channels", 1)),
        frame_duration_ms=int(raw_data.get("frame_duration_ms", 100)),
        queue_max_frames=int(raw_data.get("queue_max_frames", 50)),
        min_confidence=float(raw_data.get("min_confidence", 0.65)),
        default_command_mode=bool(raw_data.get("default_command_mode", False)),
        use_fake_providers_by_default=bool(
            raw_data.get("use_fake_providers_by_default", False)
        ),
    )
