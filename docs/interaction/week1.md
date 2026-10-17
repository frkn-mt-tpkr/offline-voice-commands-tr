# K3 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/interaction/week1.md`)

- **Modül Sorumlusu:** K3 (`e3`) — `@iremsutavuz26`
- **İlgili Görev / Dal:** Issue #3 / `e3/issue-3-ui-typed-commands`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** `[Örn: Windows 11, Python 3.12.8, Tkinter]`

---

## 1. Uygulama Özeti
- **Tkinter Dinleme Ekranı İskeleti (`ui/main_window.py`):**
- **Allowlist Eşleme Mekanizması (`commands/matcher.py`):**
- **Komut Yürütmeme Kuralı (Hafta 1 Kapsamı):**

---

## 2. Yazılı Komut Eşleme ve Arayüz Doğrulama Tablosu

| Test İfadesi | Komut Modu | Beklenen Sonuç (`matched` / `command_id`) | Gözlenen Sonuç / Günlük Kaydı | Onay Gereksinimi | Durum |
|---|---|---|---|---|---|
| `"dinlemeyi durdur"` | Kapalı (Dikte) | `matched=False` | `...` | Hayır | `[GEÇTİ / BEKLİYOR]` |
| `"dinlemeyi durdur"` | Açık | `matched=True` (`stop_listening`) | `...` | Hayır | `[GEÇTİ / BEKLİYOR]` |
| `"son cümleyi sil"` | Açık | `matched=True` (`delete_last_sentence`) | `...` | Hayır | `[GEÇTİ / BEKLİYOR]` |
| `"metni temizle"` | Açık | `matched=True` (`clear_text`) | `...` | **Evet** | `[GEÇTİ / BEKLİYOR]` |
| `"metni kaydet"` | Açık | `matched=True` (`save_text`) | `...` | **Evet** | `[GEÇTİ / BEKLİYOR]` |
| `"bilgisayarı kapat"` | Açık | `matched=False` (`unknown_command`) | `...` | Hayır | `[GEÇTİ / BEKLİYOR]` |
| `"dosyayı sil"` | Açık | `matched=False` (`unknown_command`) | `...` | Hayır | `[GEÇTİ / BEKLİYOR]` |

---

## 3. Doğrulama Kanıtı (Ekran Görüntüsü / Not)
- Arayüz ekran görüntüsü PR açıklamasına eklendi mi? `[Evet / Hayır]`
