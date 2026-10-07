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

| Rapor | Saat | Mod | İçerik |
|-------|------|-----|--------|
| Sabah | **08:13** | `morning` | Gece gelişmeleri + piyasa açılış |
| Akşam | **20:07** | `evening` | Gün özeti + piyasa kapanış |
| Haftalık | Cuma akşamı | — | Akşam raporuna ek bölüm olarak düşer |

Zamanlama **Windows Görev Zamanlayıcısı** ile yapılır; saatler bilgisayarın
yerel saatidir (Türkiye saati).

> **Neden GitHub Actions cron'u değil?**
> Bu repo GitHub Actions ile denendi ve cron güvenilir çalışmadı:
>
> | Slot (UTC) | Beklenen | Gözlenen |
> |---|---|---|
> | 07.10 05:00 | 07.10 05:00 | 07.10 **11:31** (+6s31dk) |
> | 07.10 17:00 | 07.10 17:00 | hiç gelmedi |
>
> `*/15` frekanslı ayrı bir test workflow'u bile art arda 4 slot kaçırdı;
> saat başı olmayan `:15`/`:45` dakikaları da dahildi. Repo public yapıldı,
> fork kontrol edildi, Actions durum sayfası temiz, billing uyarısı yok —
> yine de tetiklenmedi. GitHub'ın `dispatch` tetikleyicisi ise sorunsuz
> çalışıyor ve maili ulaştırıyordu; yani sorun yalnızca zamanlayıcıdaydı.
>
> Bu nedenle zamanlama işletim sistemine taşındı: ücretsiz, üçüncü parti
> bağımlılığı yok ve tam zamanında çalışıyor.

### Görevleri kurma

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode morning   # elle deneme (mail gider)
powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode evening
powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode morning -Test  # mail gitmez, HTML üretir
```

`scripts\run_report.ps1` her çalıştırmada sırasıyla: repoyu günceller →
bülteni üretip **gerçek e-posta gönderir** → `data/` dosyalarını commit edip
push eder → `logs/` altına UTF-8 log yazar.

Görevleri PowerShell ile kaydetmek için:

```powershell
$script = "C:\...\Project2\scripts\run_report.ps1"
$a = New-ScheduledTaskAction -Execute 'powershell.exe' `
     -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""
$p = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive
$s = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable `
     -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 45)

Register-ScheduledTask -TaskName 'DailyNewsTR-Sabah' -Action $a `
  -Trigger (New-ScheduledTaskTrigger -Daily -At '08:13') -Principal $p -Settings $s -Force
Register-ScheduledTask -TaskName 'DailyNewsTR-Aksam' -Action $a `
  -Trigger (New-ScheduledTaskTrigger -Daily -At '20:07') -Principal $p -Settings $s -Force
```

Görevleri silmek için:

```powershell
Unregister-ScheduledTask -TaskName 'DailyNewsTR-Sabah' -Confirm:$false
Unregister-ScheduledTask -TaskName 'DailyNewsTR-Aksam' -Confirm:$false
```

> **Bilgisayar kapalıysa ne olur?**
> `StartWhenAvailable` açık olduğu için bilgisayar 08:13'te kapalıysa
> bülten bir sonraki açılışta üretilir (gecikmiş olarak).
> `WakeToRun` ile bilgisayar uyku modundaysa 08:13'te kendisi uyanır.
> Görev "Interactive" oturum tanımıyla kaydedildiği için **Windows
> kullanıcısı oturum açık olmalıdır**. `LogonType S4U` ile oturum açma
> şartını kaldırmak mümkündür ama S4U görevleri ağ erişiminde sorun
> yaşayabildiği için varsayılan bırakılmadı.

## 📁 Proje Yapısı

```
Project2/
├── .github/workflows/
│   └── daily-report.yml       # Yalnızca ELLE tetikleme (yedek yol / veri senkronu)
├── scripts/
│   └── run_report.ps1         # Windows Görev Zamanlayıcısı çalıştırıcısı
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

```powershell
# Gerçek e-posta gönderimi
powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode evening

# E-posta göndermeden HTML üret (tarayıcıda açıp incele)
powershell -ExecutionPolicy Bypass -File scripts\run_report.ps1 -Mode morning -Test

# Zamanlanmış görevi elle tetikle (gerçek mail gider)
Start-ScheduledTask -TaskName 'DailyNewsTR-Sabah'

# Görev durumunu ve son çalışma sonucunu gör
Get-ScheduledTaskInfo -TaskName 'DailyNewsTR-Sabah'
```

## 🔍 Sorun Giderme

**Bülten gelmediyse önce loga bakın.** Her çalıştırma
`logs/run_<mod>_<tarih>.log` dosyasına yazılır:

```powershell
Get-ChildItem logs\*.log | Sort-Object LastWriteTime | Select-Object -Last 1 |
  Get-Content -Encoding UTF8 -Tail 40
```

**Görev hiç çalışmadıysa** (log dosyası yok):

1. `Get-ScheduledTask -TaskName 'DailyNewsTR-*'` → durum `Ready` olmalı.
2. **Windows kullanıcı oturumu açık mı?** Görevler `Interactive`
   oturum tanımıyla kayıtlı; oturum kapalıyken çalışmazlar.
3. Görevi elle tetikleyip sonucu okuyun:
   ```powershell
   Start-ScheduledTask -TaskName 'DailyNewsTR-Sabah'
   Get-ScheduledTaskInfo -TaskName 'DailyNewsTR-Sabah' | Select-Object LastRunTime, LastTaskResult
   ```
   `LastTaskResult` `0` ise başarılı, `0x1` ise script hata verdi (loga bakın).

**Çalıştı ama mail gitmediyse** logda `E-posta başarıyla gönderildi!`
yazmıyordur. `sender.py` 3 deneme yapar; son deneme de başarısızsa
`main.py` `sys.exit(1)` verir. Gmail App Password'in geçerli olduğundan
ve 2 Adımlı Doğrulama'nın açık olduğundan emin olun.

**Gemini hataları:** logda `kotası tükenmiş` görüyorsanız kotadadır,
`geçici olarak meşgul` görüyorsanız 503 alınıp yeniden denenmiştir.
Her iki durumda da bülten piyasa verileriyle gönderilir, AI bölümü boş
kalır. `zaman bütçesi doldu` mesajı 180 saniyelik süre aşımını gösterir.

**Bilinen zararsız uyarılar:**

- `'TRT Spor' ... mismatched tag` → kaynak feed'in XML'i bozuk; atlanır.
- `Automatic function calling (AFC)` → `google-genai` bilgi mesajı.
- Bazen `SSL: WRONG_VERSION_NUMBER` → tek bir RSS kaynağına ağ erişim
  sorunu; o kaynak atlanır, diğerleri işlenir.

**GitHub Actions yedeği:** `.github/workflows/daily-report.yml` artık
zamanlamasızdır ama elle tetiklenebilir (Actions → Run workflow). Yedek
yol olarak kullanışlıdır; verileri de `main`'e commit eder.

## 📄 Lisans

Bu proje kişisel kullanım için geliştirilmiştir.
