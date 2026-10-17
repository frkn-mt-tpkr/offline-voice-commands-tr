# Ortak Test ve Fixture Verileri (`fixtures/`)

**Sahip:** Proje Lideri

Bu klasör, K1, K2 ve K3 katılımcılarının birbirinin modülünü beklemeden geliştirme ve doğrulama yapabilmesi için hazırlanan örnek verileri içerir.

## 1. Ses Fixture Dosyaları (`fixtures/audio/`)
Biçim: **16 kHz, 16-bit PCM, Mono (`.wav`)**

| Dosya Adı | Beklenen Türkçe Metin | Beklenen Niyet (`CommandId`) | Açıklama |
|---|---|---|---|
| `cmd_dinlemeyi_durdur.wav` | `"dinlemeyi durdur"` | `STOP_LISTENING` | Onaysız izinli komut örneği |
| `cmd_metni_kaydet.wav` | `"metni kaydet"` | `SAVE_TEXT` | Onay gerektiren izinli komut örneği |
| `unknown_bilgisayari_kapat.wav` | `"bilgisayarı kapat"` | `None` (`unknown_command`) | Kesinlikle **reddedilmesi** gereken bilinmeyen cümle |

> **Gizlilik ve İzin Notu:** Bu klasördeki WAV dosyaları yalnızca ekip içi test amacıyla izinli olarak üretilmiştir ve kişisel veri içermez. Uygulama normal çalışırken mikrofondan diske hiçbir `.wav` veya `.pcm` dosyası yazmaz.

## 2. Metin ve Normalizasyon Fixture Verileri (`fixtures/text/sample_phrases.json`)
K2 Türkçe normalizasyon (`İ/ı`, noktalama temizliği) ve K3 Allowlist/Red testlerinde kullanılacak standart cümle setini içerir.
