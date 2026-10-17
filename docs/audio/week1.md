# K1 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/audio/week1.md`)

- **Modül Sorumlusu:** K1 (`e1`) — `@TheletterM16`
- **İlgili Görev / Dal:** Issue #1 / `e1/issue-1-mic-capture`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** `[Örn: Windows 11, Python 3.12.8, sounddevice 0.5.1]`

---

## 1. Uygulama Özeti
- **Mikrofon Listeleme (`list_devices`):**
- **16 kHz Mono Ses Çerçevesi (`AudioFrame`) Üretimi:**
- **Güvenli Başlat / Durdur (`start` / `stop`):**
- **Hata Yönetimi (`device_not_found`, `mic_permission_denied`):**

---

## 2. Manuel Doğrulama Sonuç Tablosu

| Senaryo | Uygulanan Adım / Komut | Beklenen Davranış | Gözlenen Sonuç | Durum |
|---|---|---|---|---|
| **Cihaz Listeleme** | `src.list_devices()` | Giriş aygıtlarının listelenmesi | `...` | `[GEÇTİ / BEKLİYOR]` |
| **16 kHz Mono Akış** | `src.start()` → `read_frame()` | `sample_rate=16000`, `channels=1` çerçeve üretimi | `...` | `[GEÇTİ / BEKLİYOR]` |
| **Idempotent Start** | Ardışık iki `src.start()` çağrısı | İkinci akış açılmadan güvenli devam | `...` | `[GEÇTİ / BEKLİYOR]` |
| **Hata Yolu** | Geçersiz `device_id` ile başlatma | Çökmeden `device_not_found` hatası | `...` | `[GEÇTİ / BEKLİYOR]` |
| **Gizlilik Denetimi** | Çalışma sonrası disk kontrolü | Diskte `.wav` / `.pcm` dosyası oluşmaması | `...` | `[GEÇTİ / BEKLİYOR]` |

---

## 3. Doğrulama Kanıtı (Terminal Çıktısı / Ekran Görüntüsü)

```text
[Doğrulama çıktısı buraya eklenecektir]
```
