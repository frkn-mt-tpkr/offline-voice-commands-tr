# K2 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/recognition/week1.md`)

- **Modül Sorumlusu:** K2 (`e2`) — `@omerkonacoglu`
- **İlgili Görev / Dal:** Issue #2 / `e2/issue-2-offline-fixture-recognition`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** `[Örn: Windows 11, Python 3.12.8, vosk 0.3.45]`

---

## 1. Uygulama Özeti
- **Vosk Türkçe Model Kurulumu ve Yapılandırma:**
- **Çevrimdışı (Offline) Çözümleme Doğrulaması:**
- **Model Eksikliği (`model_missing`) Hata Yönetimi:**

---

## 2. Fixture WAV Çözümleme Sonuç Tablosu

| Fixture WAV Dosyası | Beklenen İfade | Üretilen Ham Metin (`text`) | Normalize Metin (`normalized_text`) | Hata Kodu (`error_code`) | Durum |
|---|---|---|---|---|---|
| `cmd_dinlemeyi_durdur.wav` | `"dinlemeyi durdur"` | `...` | `...` | `None` | `[GEÇTİ / BEKLİYOR]` |
| `cmd_metni_kaydet.wav` | `"metni kaydet"` | `...` | `...` | `None` | `[GEÇTİ / BEKLİYOR]` |
| `unknown_bilgisayari_kapat.wav` | `"bilgisayarı kapat"` | `...` | `...` | `None` | `[GEÇTİ / BEKLİYOR]` |
| *Geçersiz model yolu testi* | Kontrollü hata | `""` | `None` | `ErrorCode.MODEL_MISSING` | `[GEÇTİ / BEKLİYOR]` |

---

## 3. Doğrulama Kanıtı (Terminal Çıktısı / Ekran Görüntüsü)

```text
[Doğrulama çıktısı buraya eklenecektir]
```
