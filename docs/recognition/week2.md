# K2 — Hafta 2 Teknik ve Manuel Doğrulama Notu (`docs/recognition/week2.md`)

- **Modül Sorumlusu:** K2 (`e2`) — `@omerkonacoglu`
- **İlgili Görev / Dal:** Issue #8 / `e2/issue-8-live-recognition-and-normalization`
- **Hedef Dal:** `week/2`
- **Doğrulama Ortamı:** `Windows (PowerShell), Python 3.14.6 (.venv), vosk 0.3.45`

---

## 1. Uygulama Özeti

- **Canlı Kısmi (`is_final=False`) ve Nihai (`is_final=True`) Akış (`accept_frame` & `reset`):**
  - `VoskSpeechRecognizer.accept_frame` ve `FakeSpeechRecognizer.accept_frame` içinde ardışık 16 kHz mono `AudioFrame` çerçeveleri işlenirken `_last_partial_text` durumu tutuldu.
  - Konuşma devam ederken yalnızca bir önceki kısmi metinden farklı ve boş olmayan kısmi sonuçlar `RecognitionResult(is_final=False)` olarak döndürülerek tekrar eden kısmi olaylar bastırıldı.
  - Cümle sonlandığında kelime bazlı ortalama `confidence` skoru hesaplanarak `RecognitionResult(is_final=True)` döndürüldü ve `_last_partial_text` tamponu sıfırlandı.
  - `reset()` metodunda hem Vosk `KaldiRecognizer.Reset()` çağrısı yapıldı hem de `_last_partial_text` temizlenerek eski konuşma artığı kalmaması garanti altına alındı.
- **Türkçe Normalizasyon (`normalize_turkish_text`):**
  - Türkçe büyük/küçük harf kurallarına (`İ -> i`, `I -> ı`, `Ş -> ş`, `Ğ -> ğ`, `Ü -> ü`, `Ö -> ö`, `Ç -> ç`) tam uyum sağlandı; birleşik üst nokta (`\u0307`), noktalama işaretleri (`! ? . , ; : _`) ve ardışık boşluklar temizlendi.
- **Düşük Güven (`low_confidence`) ve Boş Sonuç Yönetimi:**
  - Nihai sonuçlarda ortalama güven skoru `min_confidence` eşiğinin altında kaldığında `error_code=ErrorCode.LOW_CONFIDENCE` ve açıklayıcı hata mesajı döndürüldü.
  - Sessizlik veya boş metin oluşan çerçevelerde `None` döndürülerek sahte metin/komut üretilmesi engellendi.

---

## 2. Doğrulama Sonuç Tablosu

### 2.1. Canlı `AudioFrame` Akışı (100 ms / 1600 Örnek Çerçevelerle Besleme)

| Kaynak Dosya | Olay Türü | Üretilen Metin (`text`) | Normalize Metin (`normalized_text`) | Güven (`confidence`) | Hata Kodu (`error_code`) | Durum |
|---|---|---|---|---|---|---|
| `cmd_dinlemeyi_durdur.wav` | `PARTIAL` (`is_final=False`) | `"dinlemeyi"` | `"dinlemeyi"` | `None` | `None` | `GEÇTİ` |
| `cmd_dinlemeyi_durdur.wav` | `PARTIAL` (`is_final=False`) | `"dinlemeyi durdur"` | `"dinlemeyi durdur"` | `None` | `None` | `GEÇTİ` |
| `cmd_dinlemeyi_durdur.wav` | `FINAL` (`is_final=True`) | `"dinlemeyi durdur"` | `"dinlemeyi durdur"` | `0.9802` | `None` | `GEÇTİ` |

### 2.2. Türkçe Normalizasyon ve `low_confidence` Eşik Testleri

| Test Senaryosu | Girdi | Beklenen Çıktı | Gözlenen Çıktı | Durum |
|---|---|---|---|---|
| Noktalı/Noktasız İ/I ve Fazla Boşluk | `"DİNLEMEYİ   DURDUR!"` | `"dinlemeyi durdur"` | `"dinlemeyi durdur"` | `GEÇTİ` |
| Noktalama Temizliği | `"METNİ KAYDET."` | `"metni kaydet"` | `"metni kaydet"` | `GEÇTİ` |
| Büyük `I -> ı` ve `Ş/Ç` Dönüşümü | `"IŞIKLARI AÇ"` | `"ışıkları aç"` | `"ışıkları aç"` | `GEÇTİ` |
| Karma Büyük/Küçük Harf ve Soru İşareti | `"Son Cümleyi Sil?"` | `"son cümleyi sil"` | `"son cümleyi sil"` | `GEÇTİ` |
| Yüksek Güven Eşiği (`min_confidence=0.99`) | `cmd_metni_kaydet.wav` (`conf=0.8668`) | `ErrorCode.LOW_CONFIDENCE` | `ErrorCode.LOW_CONFIDENCE` | `GEÇTİ` |

---

## 3. Doğrulama Kanıtı (Terminal Çıktısı)

```text
PARTIAL -> dinlemeyi | conf: None | err: None
PARTIAL -> dinlemeyi durdur | conf: None | err: None
FINAL -> dinlemeyi durdur | conf: 0.9802 | err: None

['dinlemeyi durdur', 'metni kaydet', 'ışıkları aç', 'son cümleyi sil']
Yüksek eşik testi: RecognitionResult(text='metni kaydet', is_final=True, confidence=0.8668, normalized=NormalizedText(raw_text='metni kaydet', normalized_text='metni kaydet', language='tr'), error_code=<ErrorCode.LOW_CONFIDENCE: 'low_confidence'>, error_message='Ses yeterince net anlaşılamadı (güven=0.87 < eşik=0.99).', timestamp_ms=1795714812293)
```
