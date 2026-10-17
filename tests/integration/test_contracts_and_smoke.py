"""
Lider — Entegrasyon, Sözleşme ve Güvenlik Taraması Testleri
(`tests/integration/test_contracts_and_smoke.py`)
Sahip: Proje Lideri

Çalıştırma:
  python -m unittest discover -s tests/integration -p "test_*.py" -v
"""

from __future__ import annotations

import json
import unittest
import wave
from pathlib import Path

from audio.fake_source import FakeAudioSource
from commands.executor import SafeCommandExecutor
from commands.matcher import AllowlistCommandMatcher
from contracts.models import (
    ALLOWED_COMMANDS,
    AudioConfig,
    CommandId,
    ErrorCode,
)
from core.config import PROJECT_ROOT, load_settings
from core.controller import AppController
from recognition.fake_recognizer import FakeSpeechRecognizer, normalize_turkish_text


class TestContractsAndSecurity(unittest.TestCase):
    """Proje 3 sözleşme, allowlist ve güvenlik kurallarını doğrular."""

    def setUp(self) -> None:
        self.settings = load_settings()
        self.controller = AppController(settings=self.settings)

    def test_four_allowed_commands_catalog(self) -> None:
        """İzinli komut listesinde yalnızca 4 tanımlı ifade bulunmalıdır."""
        self.assertEqual(len(ALLOWED_COMMANDS), 4)
        self.assertIn("dinlemeyi durdur", ALLOWED_COMMANDS)
        self.assertIn("son cümleyi sil", ALLOWED_COMMANDS)
        self.assertIn("metni temizle", ALLOWED_COMMANDS)
        self.assertIn("metni kaydet", ALLOWED_COMMANDS)

        self.assertFalse(ALLOWED_COMMANDS["dinlemeyi durdur"].requires_confirmation)
        self.assertFalse(ALLOWED_COMMANDS["son cümleyi sil"].requires_confirmation)
        self.assertTrue(ALLOWED_COMMANDS["metni temizle"].requires_confirmation)
        self.assertTrue(ALLOWED_COMMANDS["metni kaydet"].requires_confirmation)

    def test_turkish_normalization_dotted_and_dotless_i(self) -> None:
        """Türkçe İ->i ve I->ı dönüşümü doğru çalışmalıdır."""
        norm1 = normalize_turkish_text("DİNLEMEYİ DURDUR!")
        self.assertEqual(norm1.normalized_text, "dinlemeyi durdur")

        norm2 = normalize_turkish_text("  SON   CÜMLEYİ   SİL... ")
        self.assertEqual(norm2.normalized_text, "son cümleyi sil")

        norm3 = normalize_turkish_text("BİLGİSAYARI KAPAT")
        self.assertEqual(norm3.normalized_text, "bilgisayarı kapat")

    def test_ten_unknown_phrases_are_strictly_rejected(self) -> None:
        """Bilinmeyen 10 cümlenin tamamı komut modunda reddedilmelidir."""
        phrases_path = PROJECT_ROOT / "fixtures" / "text" / "sample_phrases.json"
        with open(phrases_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        unknown_phrases = data["rejected_unknown_phrases_10"]
        self.assertEqual(len(unknown_phrases), 10)

        for phrase in unknown_phrases:
            intent = self.controller.evaluate_text(phrase, command_mode_enabled=True)
            self.assertFalse(
                intent.matched,
                f"Bilinmeyen cümle yanlışlıkla komut olarak eşleşti: '{phrase}'",
            )
            self.assertEqual(intent.error_code, ErrorCode.UNKNOWN_COMMAND)

    def test_dictation_mode_blocks_all_commands(self) -> None:
        """Komut modu kapalıyken izinli cümle söylense bile komut eşleşmemelidir."""
        intent = self.controller.evaluate_text(
            "dinlemeyi durdur", command_mode_enabled=False
        )
        self.assertFalse(intent.matched)
        self.assertIsNone(intent.command_id)

    def test_confirmation_required_commands_do_not_execute_without_confirmation(self) -> None:
        """'metni temizle' ve 'metni kaydet' onay olmadan çalışmamalıdır."""
        intent = self.controller.evaluate_text("metni temizle", command_mode_enabled=True)
        self.assertTrue(intent.matched)
        self.assertTrue(intent.requires_confirmation)

        res_unconfirmed = self.controller.execute_intent(intent, confirmed=False)
        self.assertFalse(res_unconfirmed.executed)
        self.assertTrue(res_unconfirmed.cancelled)

        res_confirmed = self.controller.execute_intent(intent, confirmed=True)
        self.assertTrue(res_confirmed.executed)
        self.assertFalse(res_confirmed.cancelled)

    def test_fake_audio_source_and_error_codes(self) -> None:
        """Sahte mikrofon 16 kHz mono çerçeve üretmeli ve hata kodlarını desteklemeli."""
        source = FakeAudioSource(AudioConfig(sample_rate=16000, channels=1))
        source.start()
        self.assertTrue(source.is_running)
        frame = source.read_frame()
        self.assertIsNotNone(frame)
        assert frame is not None
        self.assertEqual(frame.sample_rate, 16000)
        self.assertEqual(frame.channels, 1)
        source.stop()
        self.assertFalse(source.is_running)

        denied_source = FakeAudioSource(simulated_error=ErrorCode.MIC_PERMISSION_DENIED)
        with self.assertRaises(PermissionError):
            denied_source.start()

    def test_fixture_wav_files_valid_16khz_mono(self) -> None:
        """fixtures/audio/ altındaki 3 WAV dosyası 16 kHz mono formatında olmalıdır."""
        manifest_path = PROJECT_ROOT / "fixtures" / "audio" / "manifest.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        recognizer = FakeSpeechRecognizer()
        for item in manifest["fixtures"]:
            wav_path = PROJECT_ROOT / "fixtures" / "audio" / item["filename"]
            self.assertTrue(wav_path.exists(), f"Fixture WAV eksik: {wav_path}")
            with wave.open(str(wav_path), "rb") as wf:
                self.assertEqual(wf.getframerate(), 16000)
                self.assertEqual(wf.getnchannels(), 1)
                self.assertEqual(wf.getsampwidth(), 2)

            result = recognizer.transcribe_wav_file(str(wav_path))
            self.assertFalse(result.is_error)
            self.assertTrue(len(result.text.strip()) > 0)

    def test_security_scan_no_shell_or_subprocess_in_codebase(self) -> None:
        """Proje 3 Güvenlik Taraması: Kodda subprocess, os.system, shell=True, eval, exec çağrısı olmamalı."""
        import ast

        scanned_dirs = ["audio", "recognition", "commands", "ui", "core", "contracts"]
        forbidden_imports = {"subprocess", "pty", "shlex"}
        forbidden_calls = {"eval", "exec", "system", "popen", "spawn", "Popen"}

        for folder in scanned_dirs:
            folder_path = PROJECT_ROOT / folder
            for py_file in folder_path.rglob("*.py"):
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(py_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            root_pkg = alias.name.split(".")[0]
                            self.assertNotIn(
                                root_pkg,
                                forbidden_imports,
                                f"GÜVENLİK İHLALİ: {py_file.name} içinde yasaklı import '{alias.name}'!",
                            )
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        root_pkg = node.module.split(".")[0]
                        self.assertNotIn(
                            root_pkg,
                            forbidden_imports,
                            f"GÜVENLİK İHLALİ: {py_file.name} içinde yasaklı from-import '{node.module}'!",
                        )
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            self.assertNotIn(
                                node.func.id,
                                forbidden_calls,
                                f"GÜVENLİK İHLALİ: {py_file.name} içinde yasaklı '{node.func.id}()' çağrısı!",
                            )
                        elif isinstance(node.func, ast.Attribute):
                            self.assertNotIn(
                                node.func.attr,
                                forbidden_calls,
                                f"GÜVENLİK İHLALİ: {py_file.name} içinde yasaklı '.{node.func.attr}()' çağrısı!",
                            )
                        for kw in node.keywords:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                                self.fail(f"GÜVENLİK İHLALİ: {py_file.name} içinde 'shell=True' kullanımı!")


if __name__ == "__main__":
    unittest.main()
