# K2 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/recognition/week1.md`)

- **Modül Sorumlusu:** K2 (`e2`) — `@omerkonacoglu`
- **İlgili Görev / Dal:** Issue #2 / `e2/issue-2-offline-fixture-recognition`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** `Windows (PowerShell), Python 3.14.6 (.venv), vosk 0.3.45`

---

## 1. Uygulama Özeti
- **Vosk Türkçe Model Kurulumu ve Yapılandırma:** `VoskSpeechRecognizer` sınıfı model yolunu sabit (hardcoded) yazmadan dışarıdan parametre olarak (`load_settings().model_path`) veya `VOSK_MODEL_PATH` ortam değişkeninden alacak şekilde yapılandırıldı. `models/vosk-model-small-tr-0.3` dizinindeki çevrimdışı Türkçe dil modeli `Model` ve `KaldiRecognizer` (`SetWords(True)`) ile başarıyla yüklendi.
- **Çevrimdışı (Offline) Çözümleme Doğrulaması:** `transcribe_wav_file` metodu standart `wave` modülüyle 16 kHz 16-bit mono PCM fixture WAV dosyalarını 4000 frame'lik bloklar halinde `KaldiRecognizer`'a besleyerek internet bağlantısı olmadan çözümledi; kelime bazlı güven (`conf`) skorlarının ortalamasını hesapladı ve Türkçe karakter kurallarına (`İ -> i`, `I -> ı`) uygun `NormalizedText` üretti.
- **Model Eksikliği (`model_missing`) Hata Yönetimi:** Model klasörü mevcut olmadığında veya geçersiz bir model yolu verildiğinde uygulama çökmeden `load_model()` `False` döndürdü ve `transcribe_wav_file()` / `accept_frame()` çağrılarında kontrollü olarak `ErrorCode.MODEL_MISSING` içeren `RecognitionResult` üretildi.

---

## 2. Fixture WAV Çözümleme Sonuç Tablosu

| Fixture WAV Dosyası | Beklenen İfade | Üretilen Ham Metin (`text`) | Normalize Metin (`normalized_text`) | Hata Kodu (`error_code`) | Durum |
|---|---|---|---|---|---|
| `cmd_dinlemeyi_durdur.wav` | `"dinlemeyi durdur"` | `"dinlemeyi durdur"` (`conf=0.9801`) | `"dinlemeyi durdur"` | `None` | `GEÇTİ` |
| `cmd_metni_kaydet.wav` | `"metni kaydet"` | `"metni kaydet"` (`conf=0.8688`) | `"metni kaydet"` | `None` | `GEÇTİ` |
| `unknown_bilgisayari_kapat.wav` | `"bilgisayarı kapat"` | `"bilgisayarı kapat"` (`conf=0.9695`) | `"bilgisayarı kapat"` | `None` | `GEÇTİ` |
| *Geçersiz model yolu testi* | Kontrollü hata | `""` | `None` | `ErrorCode.MODEL_MISSING` | `GEÇTİ` |

---

## 3. Doğrulama Kanıtı (Terminal Çıktısı / Ekran Görüntüsü)

```text
Loaded: True
cmd_dinlemeyi_durdur.wav -> RecognitionResult(text='dinlemeyi durdur', is_final=True, confidence=0.9801, normalized=NormalizedText(raw_text='dinlemeyi durdur', normalized_text='dinlemeyi durdur', language='tr'), error_code=None, error_message=None, timestamp_ms=1795257327768)
cmd_metni_kaydet.wav -> RecognitionResult(text='metni kaydet', is_final=True, confidence=0.8688, normalized=NormalizedText(raw_text='metni kaydet', normalized_text='metni kaydet', language='tr'), error_code=None, error_message=None, timestamp_ms=1795257328268)
unknown_bilgisayari_kapat.wav -> RecognitionResult(text='bilgisayarı kapat', is_final=True, confidence=0.9695, normalized=NormalizedText(raw_text='bilgisayarı kapat', normalized_text='bilgisayarı kapat', language='tr'), error_code=None, error_message=None, timestamp_ms=1795257328783)
Missing model test -> RecognitionResult(text='', is_final=True, confidence=None, normalized=None, error_code=<ErrorCode.MODEL_MISSING: 'model_missing'>, error_message='Vosk Türkçe dil modeli bulunamadı. Lütfen README adımlarını izleyin.', timestamp_ms=1795257328792)
```
