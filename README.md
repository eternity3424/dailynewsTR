# 📰 Günlük Haber Özet & Finansal Okuryazarlık Sistemi

Türkiye ve dünya gündemini takip eden, **Gemini AI** ile özetleyen, finansal okuryazarlık eğitimi sunan ve sonuçları güzel tasarlanmış HTML e-posta ile gönderen tam otomatik bir sistem.

## ✨ Özellikler

- 📰 **Haber Özetleme** — Türkiye ve dünya haberlerini RSS feed'lerden toplar, AI ile özetler
- 📊 **Piyasa Verileri** — Döviz, altın, borsa, kripto anlık verileri
- 📚 **Finansal Okuryazarlık** — Her haberde terim açıklamaları ve "Bu Neden Önemli" bölümleri
- 🔄 **Devam Eden Hikayeler** — Önemli gelişmeleri gün gün takip eder
- ❓ **Mini Quiz** — Öğrenilen kavramlardan günlük quiz
- 📅 **Yarın Ne Beklenmeli** — Ekonomi takviminden önemli etkinlikler
- 📈 **Tarihsel Bağlam** — Büyük olayları geçmişle karşılaştırır
- 📊 **Haftalık Değerlendirme** — Her Cuma haftanın özeti

## 🛠️ Teknoloji

| Bileşen | Teknoloji | Maliyet |
|---------|-----------|---------|
| AI Özetleme | Gemini API (`gemini-3.5-flash-lite`) | Ücretsiz (kota sınırlı) |
| Haber Toplama | RSS Feed'ler (feedparser) | Ücretsiz |
| Piyasa Verileri | yfinance | Ücretsiz |
| Ekonomi Takvimi | Investing.com (scraping) | Ücretsiz |
| Bulut Çalıştırma | GitHub Actions | Ücretsiz |
| E-posta | Gmail SMTP | Ücretsiz |

## 📋 Ön Gereksinimler

1. **Python 3.12+**
2. **Gemini API Key** — [Google AI Studio](https://aistudio.google.com/apikey) üzerinden ücretsiz alınır
3. **Gmail Hesabı** — App Password gerekir (aşağıya bakın)
4. **GitHub Hesabı** — Actions için

## 🚀 Kurulum

### 1. Repoyu klonlayın

```bash
git clone https://github.com/KULLANICI/Project2.git
cd Project2
```

### 2. Python bağımlılıklarını yükleyin

```bash
pip install -r requirements.txt
```

### 3. Ortam değişkenlerini ayarlayın

```bash
cp .env.example .env
```

`.env` dosyasını düzenleyin:

```env
GEMINI_API_KEY=your_api_key_here
GMAIL_ADDRESS=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=where_to_send@example.com
```

### 4. Gmail App Password oluşturun

1. [Google Hesap Güvenlik](https://myaccount.google.com/security) sayfasına gidin
2. **2 Adımlı Doğrulama**'yı aktifleştirin (zaten aktifse atlayın)
3. [Uygulama Şifreleri](https://myaccount.google.com/apppasswords) sayfasına gidin
4. Uygulama adı olarak "Haber Bulteni" yazın
5. **Oluştur**'a tıklayın
6. Verilen 16 karakterli şifreyi `GMAIL_APP_PASSWORD` olarak kullanın

### 5. Lokal test

```bash
# Sabah raporu (e-posta göndermez, HTML dosyası oluşturur)
python -m src.main --mode morning --test

# Akşam raporu
python -m src.main --mode evening --test
```

Oluşan HTML dosyasını tarayıcıda açarak görünümü kontrol edin.

### 6. GitHub Actions kurulumu

Repoyu GitHub'a push ettikten sonra:

1. **Settings → Secrets and variables → Actions** sayfasına gidin
2. Şu secret'ları ekleyin:

| Secret Adı | Değer |
|------------|-------|
| `GEMINI_API_KEY` | Gemini API anahtarınız |
| `GMAIL_ADDRESS` | Gönderici Gmail adresiniz |
| `GMAIL_APP_PASSWORD` | Gmail App Password |
| `RECIPIENT_EMAIL` | Alıcı e-posta adresiniz |

3. **Actions** sekmesine gidin ve workflow'u etkinleştirin

İsteğe bağlı: modeli kod değiştirmeden değiştirmek için aynı sayfadaki
**Variables** sekmesine `GEMINI_MODEL` değerini ekleyin.
Tanımlı değilse kod varsayılanı kullanır.

> **Kota notu.** Gemini ücretsiz katmanı model başına günlük çağrı sınırı uygular.
> Denenen model sırası:
> `GEMINI_MODEL` → `gemini-3.6-flash` → `gemini-3.8-flash`.
>
> Varsayılan `gemini-3.5-flash-lite` seçildi çünkü ölçümde
> `gemini-3.8-flash` kotayı tamamen tüketmiş durumdaydı (`429
> RESOURCE_EXHAUSTED`), `gemini-3.6-flash` ise sık `503 Service Unavailable`
> döndürüyordu. Günlük otomasyon için güvenilirlik tercih edildi.
>
> Kota yeniden dolduğunda daha güçlü bir model isterseniz Variables'a
> `GEMINI_MODEL = gemini-3.8-flash` yazmanız yeterli. Run loglarında
> `kotası tükenmiş, ... sonraki modele geçiliyor` veya `geçici olarak meşgul`
> görürseniz neden bu.

## ⏰ Zamanlama

| Rapor | Saat (Türkiye) | UTC | İçerik |
|-------|---------------|-----|--------|
| Sabah | 08:13 | 05:13 | Gece gelişmeleri + piyasa açılış |
| Akşam | 20:07 | 17:07 | Gün özeti + piyasa kapanış |
| Haftalık | Cuma akşamı (akşam raporuna eklenir) | — | Haftanın değerlendirmesi |

> **Neden 08:00 değil de 08:13?**
> GitHub Actions cron'u UTC'dir ve **saatin tam başında yoğunluk arttığı için
> zamanlayıcı bazı işleri sessizce düşürebilir** ("High load times include the
> start of every hour... some queued jobs may be dropped"). Dakikayı `00`'dan
> kaydırmak (burada `13` ve `7`) düşürme ihtimalini azaltır.
> Workflow, `timezone: 'Europe/Istanbul'` alanıyla TR saatini doğrudan yazar;
> yorum satırlarında UTC karşılığı da durur.

## 📁 Proje Yapısı

```
Project2/
├── .github/workflows/
│   ├── daily-report.yml       # GitHub Actions cron (bülteni üretir ve gönderir)
│   └── cron-heartbeat.yml     # GEÇİCİ zamanlayıcı teşhisi (24-48 saat sonra silin)
├── src/
│   ├── main.py                # Ana orchestrator
│   ├── config.py              # Ayarlar
│   ├── collectors/            # Veri toplama
│   │   ├── rss_collector.py
│   │   ├── market_data.py
│   │   └── economic_calendar.py
│   ├── ai/                    # Gemini AI
│   │   ├── prompts.py
│   │   ├── summarizer.py
│   │   └── quiz_generator.py
│   ├── tracking/              # Hikaye takibi
│   │   └── story_tracker.py
│   ├── email/                 # E-posta sistemi
│   │   ├── builder.py
│   │   └── sender.py
│   └── utils/
│       └── helpers.py
├── templates/                 # HTML şablonları
│   ├── daily_report.html
│   └── weekly_report.html
├── data/                      # Kalıcı veriler
│   ├── tracked_stories.json
│   ├── learned_concepts.json
│   └── quiz_history.json
├── requirements.txt
├── .env.example
└── README.md
```

## 🧪 Manuel Test

```bash
# Gerçek e-posta gönderimi testi
python -m src.main --mode evening

# GitHub Actions'ı manuel tetikleme
# GitHub repo → Actions → Günlük Haber Bülteni → Run workflow
```

## 🔍 Sorun Giderme: Zamanlanmış Bülten Gelmiyor

Manuel tetikleme çalışıyorsa sorun **zamanlayıcıdadır**, kodda değildir.
Şu sırayla kontrol edin:

1. **Actions → olay türü filtresi = `schedule`.** Hiç kayıt yoksa zamanlayıcı
   hiç koşu üretmemiştir.
2. **`cron-heartbeat.yml` teşhis iş akışına bakın** (`*/15 * * * *`).
   - `:15`, `:30`, `:45` dakikalarında düzenli run varsa ama **`:00`'da yoksa**
     bu, saat başı düşürme sorunudur.
   - Hiç run yoksa zamanlayıcı hiç devreye girmiyor; `main`'e bir cron değişikliği
     push edip Actions sekmesinden workflow'u yeniden etkinleştirin.
   - Teşhis tamamlanınca `.github/workflows/cron-heartbeat.yml` dosyasını silin.
3. **Workflow dosyası default branch'te mi?** GitHub zamanlanmış iş akışlarını
   yalnızca default branch'ten (`main`) çalıştırır; başka bir daldaki `schedule`
   asla tetiklenmez.
4. **Repo 60 gün hareketsiz kaldıysa** (public repo) GitHub zamanlanmış iş
   akışlarını sessizce devre dışı bırakır. Bir commit push edin.
5. **"Raporu sakla" artifact'ini indirin** — `python -m src.main` logları orada
   bulunur.
6. **Hata olursa artık alarm maili gelir.** Rapor üretilemezse workflow
   `RECIPIENT_EMAIL` adresine `[HATA]` önekli bir bildirim gönderir.

## 📄 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.
