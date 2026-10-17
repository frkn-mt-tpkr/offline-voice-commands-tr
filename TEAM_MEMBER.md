# TEAM_MEMBER.md — Geliştirici ve Coding Agent Çalışma Rehberi

Bu belge, projedeki modül sorumluları (**K1, K2, K3**) ve geliştirme sürecinde kullanılan **AI Coding Agent** araçları için mimari sınırları, güvenlik kurallarını ve doğrulama standartlarını tanımlar.

---

## 🤖 Coding Agent İçin Zorunlu Çalışma Protokolü

Bu depoda bir ekip üyesiyle çalışırken **kod değişikliği yapmadan önce** aşağıdaki adımları sırasıyla uygula:

1. **Yerel Kimlik Kaydı (`.team-member.local.md`):**
   - Proje kök dizininde `.team-member.local.md` dosyasını kontrol et.
   - Dosya mevcut değilse kullanıcının rol kodunu (`e1` / `K1`, `e2` / `K2`, `e3` / `K3`), GitHub kullanıcı adını ve işletim sistemini `.team-member.local.md` dosyasına kaydet (bu dosya `.gitignore` kapsamındadır).
2. **Sözleşme ve Görev Analizi:**
   - İlgili GitHub Issue tanımını ve `contracts/` dizinindeki ortak veri yapılarını (`AudioConfig`, `AudioFrame`, `RecognitionResult`, `NormalizedText`, `CommandIntent`, `CommandResult`, `ListeningState`, `ErrorCode`) incele.
3. **Uygulama Öncesi Plan Onayı:**
   - Değişiklik yapmadan önce kullanıcıya:
     - Görevin amacını ve ilgili teknik kavramları anlaşılır biçimde açıkla,
     - Düzenlenecek **izinli dosyaları** ve **kapsam dışı alanları** listele,
     - Geliştirme sonrasında kullanıcının kendi ortamında çalıştıracağı **manuel doğrulama komutlarını** belirt.
   - **Kullanıcı planı açıkça onaylamadan kod değişikliği yapma.**
4. **Gerçek Doğrulama İlkesi:**
   - Otomatik birim testlerinin geçmesi tek başına kabul kanıtı sayılmaz. Kullanıcıya kendi terminalinde/arayüzünde çalıştıracağı doğrulama adımlarını sun ve gözlenen gerçek sonuçları ilgili `docs/.../weekX.md` belgesine kaydet.

---

## 1. Modül Sahipliği ve İzinli Klasör Sınırları

Her geliştirici **yalnızca kendi sorumluluk alanındaki klasörlerde** değişiklik yapabilir. GitHub Actions üzerindeki `PR Ownership & Security Guard` iş akışı, yetki alanı dışındaki dosya değişikliklerini otomatik olarak reddeder:

| Rol | Kod | GitHub Kullanıcısı | İzinli Klasörler | Kapsam Dışı (Değiştirilemez) Alanlar |
|---|---|---|---|---|
| **K1 — Mikrofon ve Ses** | `e1` | `@TheletterM16` | `audio/`, `docs/audio/` | `recognition/`, `commands/`, `ui/`, `core/`, `contracts/`, `app.py`, `requirements.txt` |
| **K2 — Konuşma Tanıma** | `e2` | `@omerkonacoglu` | `recognition/`, `docs/recognition/` | `audio/`, `commands/`, `ui/`, `core/`, `contracts/`, `app.py`, `requirements.txt` |
| **K3 — Güvenli Komut ve Arayüz** | `e3` | `@iremsutavuz26` | `commands/`, `ui/`, `assets/ui/`, `docs/interaction/` | `audio/`, `recognition/`, `core/`, `contracts/`, `app.py`, `requirements.txt` |
| **Proje Lideri** | `leader` | `@frkn-mt-tpkr` | `contracts/`, `core/`, `app.py`, `fixtures/`, `tests/`, `README.md`, `requirements.txt` | — |

- **Bağımsız Geliştirme:** Aynı hafta içinde K1, K2 ve K3 birbirinin modülünü beklemez; herkes `contracts/` içindeki ortak veri yapılarını, `fixtures/` verilerini ve sahte sağlayıcıları (`FakeAudioSource`, `FakeSpeechRecognizer`) kullanarak kendi modülünü geliştirir.
- **Çakışma Yönetimi:** Görev sırasında ortak bir dosyada (`contracts/`, `core/`, `app.py`, `requirements.txt`) değişiklik ihtiyacı doğarsa kodlama durdurulur ve Issue üzerinden proje liderinden (`@frkn-mt-tpkr`) karar istenir.

---

## 2. Değişmez Güvenlik ve Gizlilik Kuralları

1. **İşletim Sistemi / Kabuk Komutu Yasağı:** Kod tabanında `subprocess`, `os.system`, `os.popen`, `pty`, `shlex`, `shell=True`, `eval()` ve `exec()` kullanımı kesinlikle yasaktır.
2. **Ham Ses Gizliliği:** Mikrofondan alınan ham ses verisi varsayılan olarak diske (`.wav`, `.pcm`, `.raw`) yazılmaz.
3. **Çevrimdışı Çalışma:** Konuşma tanıma ve komut eşleme süreçlerinde harici ağ/API çağrısı yapılmaz.
4. **Sıfır Yanlış Pozitif (Allowlist Zorunluluğu):** Komut modu kapalıyken hiçbir komut tetiklenmez. Komut modu açıkken yalnızca `ALLOWED_COMMANDS` içindeki 4 ifade eşleşebilir; düşük güvenli (`low_confidence`) veya tanımsız ifadeler (`unknown_command`) reddedilir.
5. **Taşınabilir Yapılandırma:** Kod içine sabit bilgisayar yolu (`C:\Users\...`) yazılmaz; model ve uygulama ayarları `core.config.load_settings()` veya fonksiyon parametreleri üzerinden okunur.

---

## 3. Git Dalı (Branch) ve Pull Request Standartları

1. **Yeni Görev Dalı Açma:**
   ```bash
   git switch main
   git pull origin main
   git switch -c e1/issue-1-mic-capture
   ```
2. **Kapsam Kontrolü ve Gönderim:**
   ```bash
   git status
   git add audio/ docs/audio/
   git commit -m "feat(audio): implement microphone device listing and 16khz mono capture"
   git push -u origin e1/issue-1-mic-capture
   ```
3. **Pull Request Açma:**
   - **Base branch:** İlgili haftanın entegrasyon dalı (`week/1`, `week/2` vb.). **Doğrudan `main` dalına PR açılmaz.**
   - **Compare branch:** Kişisel görev dalı (`eX/issue-N-...`).
   - PR açıklamasında gerçek manuel test adımları, gözlenen sonuç ve ekran görüntüsü paylaşılır.
   - Katılımcılar kendi PR'larını birleştirmez (merge işlemi proje lideri tarafından yapılır).

---

## 4. Coding Agent Başlangıç Yönergesi

Geliştiriciler, çalışma oturumu başında kullandıkları AI Coding Agent aracına aşağıdaki başlangıç yönergesini verebilir:

```text
TEAM_MEMBER.md dosyasını ve contracts/ altındaki ortak sözleşmeleri oku.
Bana atanmış olan GitHub Issue'sunun amacını, izinli dosyalarını, kapsam dışı alanlarını ve manuel kabul adımlarını açıkla.
Bilmem gereken teknik kavramları özetle ve adım adım uygulama planını sun.
Ben planı onaylamadan kod değişikliği yapma.
```
