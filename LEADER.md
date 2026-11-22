# LEADER.md — Proje Lideri ve Entegrasyon Rehberi

Bu belge, **BİLKOD Proje 3 (Konuşmayı Yazıya ve Güvenli Komuta Dönüştürme)** proje liderinin haftalık hazırlık, Issue oluşturma, PR inceleme, güvenlik taraması ve `week/X → main` entegrasyon süreçlerini tanımlar.

---

## 🤖 Coding Agent İçin Lider Protokolü

Proje lideri seninle çalıştığında:
1. Liderin yerel notları için `.leader.local.md` dosyasını kontrol et (bu dosya `.gitignore` içindedir, repoya gönderilmez).
2. Liderin sahip olduğu alanlar: `contracts/`, `core/`, `app.py`, `fixtures/`, `tests/integration/`, `README.md`, `LEADER.md`, `TEAM_MEMBER.md`, `requirements.txt`, `.github/`.
3. Katılımcı PR'larını incelerken veya `week/X` entegrasyonu yaparken aşağıdaki **8 Birleştirme Kontrolü** ve **3 Güvenlik Taramasını** otomatik olarak doğrula.

---

## 1. Liderin Sorumluluk Alanı ve Değişmez İlkeleri

- **Sözleşme Önceliği:** Katılımcılar aynı hafta birbirini beklemez. Hafta başlamadan önce gerekli tüm ortak veri yapıları (`contracts/`) ve örnek veriler (`fixtures/`) lider tarafından `main` dalına alınır ve `week/X` dalı güncel `main` üzerinden açılır.
- **Dal (Branch) Koruması:**
  - `main`: Yalnızca lider onayıyla, haftalık bütünleştirme ve manuel doğrulama tamamlandıktan sonra güncellenir.
  - `week/1`, `week/2`, `week/3`, `week/4`, `week/5`: Katılımcı PR'larının toplandığı haftalık entegrasyon dallarıdır.
- **Kapı Kuralı:** Bir önceki haftanın üç PR'ı `week/X` üzerinde birleştirilip liderin kendi bilgisayarında çalışır durumda gözlemlenmeden ve `main`'e alınmadan sonraki hafta başlatılmaz.
- **Özellik Dondurma (Feature Freeze):** 4. hafta sonunda çekirdek akış dondurulur; 5. hafta yalnızca belgeleme, kurulum doğrulaması, tasarım rötuşu ve demo hazırlığına ayrılır.

---

## 2. Haftalık Ritim

| Gün | Lider Eylemi |
|---|---|
| **Pazartesi** | Sözleşme/fixture güncellemesini `main`'e al, `week/X` dalını aç ve 3 katılımcının Issue'sunu yayımla. |
| **Çarşamba** | Kısa durum ve engel kontrolü yap; kapsamı sessizce büyütmeden engelleri kaldır. |
| **Cuma 20.00** | Katılımcı PR teslim saati (`base: week/X`). |
| **Cumartesi** | PR incelemesi, `core/` bağlantı kodunun (glue code) yazılması, `week/X` üzerinde uçtan uca manuel test. |
| **Pazar 20.00** | Haftalık ekip toplantısı, kısa TXT raporlarının değerlendirilmesi ve `week/X → main` birleştirmesi. |

---

## 3. PR Birleştirme Öncesi 8 Zorunlu Kontrol

Her katılımcı PR'ı `week/X` dalına alınmadan önce sırasıyla kontrol edilir:

1. **Doğru Issue ve Sahip:** PR ilgili haftanın Issue'suna ve doğru katılımcıya (`e1`, `e2`, `e3`) mı ait?
2. **Doğru PR Hedefi:** Base branch `main` değil, ilgili haftanın `week/X` dalı mı?
3. **Dosya Sahipliği:** Katılımcı yalnızca izinli klasörlerine (`audio/`, `recognition/`, `commands/`, `ui/`, `docs/...`) mi dokunmuş?
4. **Bağımlılık ve Sabit Yol Kontrolü:** Onaysız paket eklenmiş mi? Kodda sabit bilgisayar yolu (`C:\Users\...` vb.) var mı?
5. **Gizli Bilgi ve Kişisel Veri:** `.env`, yerel kimlik dosyası veya izinsiz ses kaydı var mı?
6. **Gerçek Manuel Test Kanıtı:** Katılımcı kendi cihazında denediği adımları, gözlenen sonucu ve ekran görüntüsünü eklemiş mi?
7. **Fixture / Sahte Kod Ayrımı:** Gerçek özellik istendiği hâlde sahte veri (fixture) nihai çözüm gibi bırakılmış mı?
8. **Birleşik Açılış:** PR birleştirildikten sonra `python app.py` ve entegrasyon testleri liderin bilgisayarında hatasız çalışıyor mu?

---

## 4. Proje 3'e Özel 3 Güvenlik Taraması

Her entegrasyonda aşağıdaki komut veya testlerle (`tests/integration/test_contracts_and_smoke.py`) kod tabanı taranır:

1. **Tehlikeli Çağrı Yasağı:** `subprocess`, `os.system`, `os.popen`, `shell=True`, `eval(`, `exec(` çağrısı **yok**.
2. **Ham Ses Kaydı Yasağı:** `audio/`, `recognition/`, `commands/`, `ui/`, `core/` altında mikrofondan alınan sesi diske `.wav` veya `.pcm` olarak yazan kod **yok**.
3. **Çevrim İçi Ağ Çağrısı Yasağı:** `urllib`, `requests`, `http.client`, `socket` ile dış servise veri gönderen kod **yok**.

---

## 5. Kabul Kapıları Özeti (5 Haftalık Plan)

- **G0 (Hazırlık):** Repo iskeleti, 7+ ortak sözleşme, sahte sağlayıcılar, 3 fixture WAV, `app.py` açılışı hazır.
- **G1 (Hafta 1):** K1 mikrofon/sahte akış, K2 çevrimdışı fixture WAV tanıma, K3 arayüz iskeleti ve yazılı 4 komut eşleme ayrı ayrı çalışıyor.
- **G2 (Hafta 2):** Sınırlı kuyruk ile canlı konuşmadan kısmi/nihai metin ekranda görünüyor; arayüz donmuyor; komut yürütme kapalı.
- **G3 (Hafta 3):** Komut modu, Türkçe normalizasyon, düşük güven (`low_confidence`) reddi, `"metni temizle"` / `"metni kaydet"` onay penceresi ve cihaz/model hata kodları çalışıyor.
- **G4 (Hafta 4 - Özellik Dondurma):** Gerçek sesle uçtan uca 4 komut akışı, işlem günlüğü ve 10/10 bilinmeyen cümlenin reddedilmesi doğrulandı.
- **G5 (Hafta 5 - Teslim):** Kurulum ve gizlilik belgeleri, temiz kurulum testi ve 2 dakikalık demo hazır.
