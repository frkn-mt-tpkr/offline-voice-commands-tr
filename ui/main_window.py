"""
K3 — Tkinter Masaüstü Arayüz İskeleti (`ui/main_window.py`)
İzinli Sahip: Katılımcı 3 (K3)
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, List, Optional

from contracts.models import ALLOWED_COMMANDS, CommandIntent, ListeningState


class MainWindow:
    """
    Konuşmayı Yazıya ve Güvenli Komuta Dönüştürme masaüstü arayüz iskeleti.
    Doğrudan mikrofon veya model kütüphanesi çağırmaz; olayları controller'a iletir.
    """

    def __init__(
        self,
        root: tk.Tk,
        devices: Optional[List[str]] = None,
        on_start_listening: Optional[Callable[[], None]] = None,
        on_stop_listening: Optional[Callable[[], None]] = None,
        on_test_phrase: Optional[Callable[[str, bool], CommandIntent]] = None,
    ) -> None:
        self.root = root
        self.root.title("BİLKOD Proje 3 — Konuşmayı Yazıya ve Güvenli Komuta Dönüştürme")
        self.root.geometry("760x560")
        self.root.minsize(680, 480)

        self._devices = devices or ["Varsayılan Mikrofon (16 kHz Mono)"]
        self._on_start_listening = on_start_listening
        self._on_stop_listening = on_stop_listening
        self._on_test_phrase = on_test_phrase

        self._state = ListeningState.IDLE
        self._command_mode_var = tk.BooleanVar(value=False)
        self._status_var = tk.StringVar(value="Durum: Hazır (Mikrofon Kapalı)")
        self._partial_var = tk.StringVar(value="Kısmi metin: —")
        self._test_input_var = tk.StringVar(value="dinlemeyi durdur")

        self._build_layout()

    def _build_layout(self) -> None:
        container = ttk.Frame(self.root, padding=14)
        container.pack(fill=tk.BOTH, expand=True)

        # Üst Başlık ve Mod Bilgisi
        header_frame = ttk.LabelFrame(container, text="Mikrofon ve Çalışma Modu", padding=10)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="Mikrofon:").grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        self.device_combo = ttk.Combobox(
            header_frame,
            values=self._devices,
            state="readonly",
            width=42,
        )
        self.device_combo.current(0)
        self.device_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 12))

        self.start_btn = ttk.Button(
            header_frame,
            text="Dinlemeyi Başlat",
            command=self._handle_start,
        )
        self.start_btn.grid(row=0, column=2, padx=4)

        self.stop_btn = ttk.Button(
            header_frame,
            text="Durdur",
            command=self._handle_stop,
            state=tk.DISABLED,
        )
        self.stop_btn.grid(row=0, column=3, padx=4)

        self.mode_check = ttk.Checkbutton(
            header_frame,
            text="Komut Modu Açık (Kapalıyken yalnızca dikte yapılır)",
            variable=self._command_mode_var,
        )
        self.mode_check.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(8, 0))

        self.status_label = ttk.Label(
            header_frame,
            textvariable=self._status_var,
            font=("Segoe UI", 9, "bold"),
        )
        self.status_label.grid(row=1, column=3, sticky=tk.E, pady=(8, 0))

        # Kısmi ve Nihai Metin Alanı
        text_frame = ttk.LabelFrame(container, text="Çevrimdışı Türkçe Metin Ekranı", padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        partial_lbl = ttk.Label(
            text_frame,
            textvariable=self._partial_var,
            foreground="#555555",
            font=("Segoe UI", 9, "italic"),
        )
        partial_lbl.pack(anchor=tk.W, pady=(0, 6))

        self.transcript_text = tk.Text(text_frame, height=8, wrap=tk.WORD, font=("Segoe UI", 10))
        self.transcript_text.pack(fill=tk.BOTH, expand=True)

        # Hafta 1 Sahte/Yazılı Komut Eşleme Test Çubuğu
        sim_frame = ttk.LabelFrame(
            container,
            text="Yazılı / Sahte Metin ile Komut Eşleme Doğrulaması (İskelet Testi)",
            padding=10,
        )
        sim_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(sim_frame, text="Test Cümlesi:").pack(side=tk.LEFT, padx=(0, 6))
        sim_entry = ttk.Entry(sim_frame, textvariable=self._test_input_var, width=36)
        sim_entry.pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(
            sim_frame,
            text="Eşleşmeyi Denetle",
            command=self._handle_test_phrase,
        ).pack(side=tk.LEFT)

        allowed_str = " | ".join(f'"{k}"' for k in ALLOWED_COMMANDS.keys())
        ttk.Label(
            sim_frame,
            text=f"İzinli 4 Komut: {allowed_str}",
            foreground="#444444",
        ).pack(side=tk.RIGHT)

        # Oturum İçi İşlem Günlüğü
        log_frame = ttk.LabelFrame(container, text="Oturum İçi İşlem ve Güvenlik Günlüğü", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=False)

        self.log_list = tk.Listbox(log_frame, height=6, font=("Consolas", 9))
        self.log_list.pack(fill=tk.BOTH, expand=True)
        self.append_log("Uygulama iskeleti hazır. Ham ses diske yazılmaz; çevrimdışı mod aktif.")

    def _handle_start(self) -> None:
        self.set_listening_state(ListeningState.LISTENING)
        if self._on_start_listening is not None:
            self._on_start_listening()

    def _handle_stop(self) -> None:
        self.set_listening_state(ListeningState.IDLE)
        if self._on_stop_listening is not None:
            self._on_stop_listening()

    def _handle_test_phrase(self) -> None:
        phrase = self._test_input_var.get().strip()
        if not phrase:
            return
        self.append_final_text(phrase)
        if self._on_test_phrase is not None:
            intent = self._on_test_phrase(phrase, self._command_mode_var.get())
            if intent.matched:
                self.append_log(
                    f"[EŞLEŞTİ] '{phrase}' -> {intent.command_id.value if intent.command_id else ''} "
                    f"(Onay gerekir: {'Evet' if intent.requires_confirmation else 'Hayır'})"
                )
            else:
                self.append_log(f"[REDDEDİLDİ] '{phrase}' -> {intent.reason}")

    def set_listening_state(self, state: ListeningState, message: Optional[str] = None) -> None:
        self._state = state
        if state == ListeningState.LISTENING:
            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self._status_var.set(message or "Durum: Dinleniyor (Mikrofon Açık)")
            self.append_log("Mikrofon dinlemesi başlatıldı.")
        elif state == ListeningState.IDLE:
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self._status_var.set(message or "Durum: Hazır (Mikrofon Kapalı)")
            self.append_log("Mikrofon dinlemesi durduruldu.")
        elif state == ListeningState.ERROR:
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)
            self._status_var.set(message or "Durum: Hata")
            if message:
                self.append_log(f"[HATA] {message}")

    def set_partial_text(self, text: str) -> None:
        self._partial_var.set(f"Kısmi metin: {text or '—'}")

    def append_final_text(self, text: str) -> None:
        if not text:
            return
        self.transcript_text.insert(tk.END, text + "\n")
        self.transcript_text.see(tk.END)

    def delete_last_sentence(self) -> str:
        content = self.transcript_text.get("1.0", tk.END).strip()
        if not content:
            return "Metin alanı zaten boş."
        lines = content.splitlines()
        removed = lines.pop()
        self.transcript_text.delete("1.0", tk.END)
        if lines:
            self.transcript_text.insert(tk.END, "\n".join(lines) + "\n")
        return f"Son cümle silindi: '{removed}'"

    def clear_all_text(self) -> str:
        self.transcript_text.delete("1.0", tk.END)
        return "Metin alanının tamamı temizlendi."

    def ask_confirmation(self, prompt_message: str) -> bool:
        return bool(messagebox.askyesno("Güvenli Komut Onayı", prompt_message, parent=self.root))

    def append_log(self, entry: str) -> None:
        self.log_list.insert(tk.END, entry)
        self.log_list.see(tk.END)
