# K1 — Hafta 1 Teknik ve Manuel Doğrulama Notu (`docs/audio/week1.md`)

- **Modül Sorumlusu:** K1 (`e1`) — `@TheletterM16`
- **İlgili Görev / Dal:** Issue #1 / `e1/issue-1-mic-capture`
- **Hedef Dal:** `week/1`
- **Doğrulama Ortamı:** `Windows 11 (10.0.26200), Python 3.14.7, sounddevice 0.5.1`

---

## 1. Uygulama Özeti
- **Mikrofon Listeleme (`list_devices`):** `sounddevice.query_devices()` üzerinden yalnızca `max_input_channels > 0` olan ses giriş cihazları filtrelenerek `id`, `name`, `max_input_channels` ve `default_samplerate` alanlarını içeren standart sözlük listesi döndürüldü.
- **16 kHz Mono Ses Çerçevesi (`AudioFrame`) Üretimi:** `sounddevice.RawInputStream` (`samplerate=16000`, `channels=1`, `dtype="int16"`, `blocksize=1600`) kullanılarak her 100 ms'lik blok (3200 bayt) bellekte `AudioFrame` nesnesine dönüştürüldü. `struct.unpack` ile 16-bit örneklerden normalize edilmiş `rms_level` (`[0.0, 1.0]`) ve `is_silence` bilgisi hesaplandı.
- **Güvenli Başlat / Durdur (`start` / `stop`):** `start()` metodu idempotent olarak tasarlandı (aktif akış varken ikinci kez çağrıldığında yeni akış açmaz). `collections.deque(maxlen=queue_max_frames)` ve `threading.Condition` ile sınırlı halka kuyruk (ring buffer) kuruldu; ardışık sessizlik çerçevelerinin kuyruğu şişirmesi engellendi. `stop()` çağrısında PortAudio akışı güvenli biçimde kapatılıp kuyruk temizlendi.
- **Hata Yönetimi (`device_not_found`, `mic_permission_denied`, `device_lost`):** Geçersiz `device_id` veya giriş cihazı bulunmaması durumunda `RuntimeError("device_not_found")`, işletim sistemi mikrofon izin reddinde `PermissionError("mic_permission_denied")`, akış sırasında cihaz kopmasında ise `RuntimeError("device_lost")` standart hata kodları üretildi.

---

## 2. Manuel Doğrulama Sonuç Tablosu

| Senaryo | Uygulanan Adım / Komut | Beklenen Davranış | Gözlenen Sonuç | Durum |
|---|---|---|---|---|
| **Cihaz Listeleme** | `src.list_devices()` | Giriş aygıtlarının listelenmesi | `5` adet giriş cihazı standart sözlük şemasıyla listelendi | `GEÇTİ` |
| **16 kHz Mono Akış** | `src.start()` → `read_frame()` | `sample_rate=16000`, `channels=1` çerçeve üretimi | `AudioFrame(rate=16000, ch=1, bytes=3200)` bellekte üretildi | `GEÇTİ` |
| **Idempotent Start** | Ardışık iki `src.start()` çağrısı | İkinci akış açılmadan güvenli devam | İkinci `start()` çağrısı hata vermeden mevcut akışı korudu (`is_running=True`) | `GEÇTİ` |
| **Hata Yolu** | Geçersiz `device_id=9999` ile başlatma | Çökmeden `device_not_found` hatası | `RuntimeError: device_not_found` yakalandı | `GEÇTİ` |
| **Gizlilik Denetimi** | Çalışma sonrası disk kontrolü | Diskte `.wav` / `.pcm` dosyası oluşmaması | Çalışma dizininde yeni `.wav` veya `.pcm` dosyası oluşmadı | `GEÇTİ` |

---

## 3. Doğrulama Kanıtı (Terminal Çıktısı / Ekran Görüntüsü)

```text
1) list_devices count: 5
   Sample device: {'id': 0, 'name': 'Microsoft Ses Eşleştiricisi - Input', 'max_input_channels': 2, 'default_samplerate': 44100}
2) is_running after start: True
3) idempotent second start ok, is_running: True
4) frame: AudioFrame rate: 16000 ch: 1 bytes: 3200 rms: 0.0 silence: True
5) is_running after stop: False read after stop: None
6) invalid device error code: device_not_found

=== BİLKOD Proje 3 | İskelet ve Sözleşme Doğrulaması ===
Model yolu ayarı : models/vosk-model-small-tr-0.3
Ses örnekleme    : 16000 Hz, 1 kanal
İzinli komutlar  : dinlemeyi durdur, son cümleyi sil, metni temizle, metni kaydet
Durum: TÜM İSKELET VE SÖZLEŞME KONTROLLERİ BAŞARILI.

Ran 8 tests in 0.049s — OK
```
