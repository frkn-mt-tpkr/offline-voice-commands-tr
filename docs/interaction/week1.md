# K3 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/interaction/week1.md`)

- **Modül Sorumlusu:** K3 (`e3`) — `@iremsutavuz26`
- **İlgili Görev / Dal:** Issue #3 / `e3/issue-3-ui-typed-commands`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** Windows 11, Visual Studio Code + GitHub Copilot, Python 3.15.2, Tkinter

---

## 1. Uygulama Özeti
- **Tkinter Dinleme Ekranı İskeleti (`ui/main_window.py`):** Dikte/Komut modu ve Hazır, Dinleniyor, Metin işleniyor, Onay bekleniyor ve Hata durumları kullanıcıya ayrı etiketlerle gösterilir.
- **Allowlist Eşleme Mekanizması (`commands/matcher.py`):** Yalnızca aşağıdaki dört izinli ifade tam eşleşmeyle kabul edilir; Dikte modu ve bilinmeyen ifadeler reddedilir.
- **Komut Yürütmeme Kuralı (Hafta 1 Kapsamı):** Yazılı/sahte ifade yalnızca eşleşme denetiminden geçer. Hiçbir eşleşme gerçek bir komut işlemi başlatmaz.

---

## 2. Yazılı Komut Eşleme ve Arayüz Doğrulama Tablosu

| Test İfadesi | Komut Modu | Beklenen Sonuç (`matched` / `command_id`) | Gözlenen Sonuç / Günlük Kaydı | Onay Gereksinimi | Durum |
|---|---|---|---|---|---|
| `"dinlemeyi durdur"` | Kapalı (Dikte) | `matched=False` | `[REDDEDİLDİ] 'dinlemeyi durdur' -> Komut modu kapalı (yalnızca dikte modu aktif).` | Hayır | `[GEÇTİ]` |
| `"dinlemeyi durdur"` | Açık | `matched=True` (`stop_listening`) | `[EŞLEŞTİ, ÇALIŞTIRILMADI] 'dinlemeyi durdur' -> stop_listening (Onay gerekir: Hayır)` | Hayır | `[GEÇTİ]` |
| `"son cümleyi sil"` | Açık | `matched=True` (`delete_last_sentence`) | `[EŞLEŞTİ, ÇALIŞTIRILMADI] 'son cümleyi sil' -> delete_last_sentence (Onay gerekir: Hayır)` | Hayır | `[GEÇTİ]` |
| `"metni temizle"` | Açık | `matched=True` (`clear_text`) | `[EŞLEŞTİ, ÇALIŞTIRILMADI] 'metni temizle' -> clear_text (Onay gerekir: Evet)` | **Evet** | `[GEÇTİ]` |
| `"metni kaydet"` | Açık | `matched=True` (`save_text`) | `[EŞLEŞTİ, ÇALIŞTIRILMADI] 'metni kaydet' -> save_text (Onay gerekir: Evet)` | **Evet** | `[GEÇTİ]` |
| `"bilgisayarı kapat"` | Açık | `matched=False` (`unknown_command`) | `[REDDEDİLDİ] 'bilgisayarı kapat' -> Anlaşılamadı: İfade izinli 4 komuttan biriyle eşleşmedi.` | Hayır | `[GEÇTİ]` |
| `"dosyayı sil"` | Açık | `matched=False` (`unknown_command`) | `[REDDEDİLDİ] 'dosyayı sil' -> Anlaşılamadı: İfade izinli 4 komuttan biriyle eşleşmedi.` | Hayır | `[GEÇTİ]` |
| `"internete bağlan"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"uygulamayı kapat"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"tüm metni hemen sil"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"metni masaüstüne kaydet"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"dinlemeyi başlat"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"son kelimeyi sil"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"komut çalıştır"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |
| `"merhaba nasılsın"` | Açık | `matched=False` (`unknown_command`) | Bu oturumda test edilmedi. | Hayır | `[BEKLİYOR]` |

---

## 3. Arayüz Durum Etiketleri

| Durum | Beklenen Ekran Etiketi | Düğmeler |
|---|---|---|
| `IDLE` | Hazır (Mikrofon Kapalı) | Başlat açık, Durdur kapalı |
| `LISTENING` | Dinleniyor (Mikrofon Açık) | Başlat kapalı, Durdur açık |
| `PROCESSING` | Metin işleniyor | Başlat kapalı, Durdur açık |
| `AWAITING_CONFIRMATION` | Onay bekleniyor | Başlat kapalı, Durdur açık |
| `ERROR` | Hata | Başlat açık, Durdur kapalı |

---

## 4. Doğrulama Kanıtı (Ekran Görüntüsü / Not)
- Arayüz ekran görüntüsü PR açıklamasına eklendi mi? `[Evet / Hayır]`
- Kullanıcının manuel test sonucu: **6/6 adım geçti.**
- Altıncı adımda listelenen 10 bilinmeyen ifadeden 2'si (`bilgisayarı kapat`, `dosyayı sil`) denendi ve reddedildi; kalan 8 ifade bu oturumda denenmedi.
- Komut yürütme: Hafta 1 kapsamında yapılmaz.
