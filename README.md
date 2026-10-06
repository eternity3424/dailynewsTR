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
| AI Özetleme | Gemini API (gemini-2.0-flash) | Ücretsiz |
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

## ⏰ Zamanlama

| Rapor | Saat (Türkiye) | İçerik |
|-------|---------------|--------|
| Sabah | 08:00 | Gece gelişmeleri + piyasa açılış |
| Akşam | 20:00 | Gün özeti + piyasa kapanış |
| Haftalık | Cuma 20:00 | Haftanın değerlendirmesi (ek bölüm) |

## 📁 Proje Yapısı

```
Project2/
├── .github/workflows/
│   └── daily-report.yml       # GitHub Actions cron
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

## 📄 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.
