"""
Günlük Haber Özet & Finansal Okuryazarlık Sistemi
Merkezi yapılandırma dosyası
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    load_dotenv(Path(__file__).resolve().parent.parent / "1.env")

# ─── Proje Yolları ────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"

# ─── Gemini API ───────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# ─── E-posta Ayarları ────────────────────────────────────────
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ─── RSS Feed Kaynakları ─────────────────────────────────────
RSS_FEEDS = {
    "ekonomi": [
        {
            "name": "Bloomberg HT",
            "url": "https://www.bloomberght.com/rss",
            "lang": "tr",
        },
        {
            "name": "Dünya Gazetesi",
            "url": "https://www.dunya.com/rss",
            "lang": "tr",
        },
        {
            "name": "TRT Haber Ekonomi",
            "url": "https://www.trthaber.com/ekonomi_articles.rss",
            "lang": "tr",
        },
        {
            "name": "BBC Business",
            "url": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "lang": "en",
        },
    ],
    "siyaset": [
        {
            "name": "Anadolu Ajansı - Güncel",
            "url": "https://www.aa.com.tr/tr/rss/default?cat=guncel",
            "lang": "tr",
        },
        {
            "name": "Anadolu Ajansı - Politika",
            "url": "https://www.aa.com.tr/tr/rss/default?cat=politika",
            "lang": "tr",
        },
        {
            "name": "TRT Haber Gündem",
            "url": "https://www.trthaber.com/gundem_articles.rss",
            "lang": "tr",
        },
        {
            "name": "BBC Türkçe",
            "url": "https://feeds.bbci.co.uk/turkce/rss.xml",
            "lang": "tr",
        },
    ],
    "dunya": [
        {
            "name": "BBC World",
            "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "lang": "en",
        },
        {
            "name": "Al Jazeera",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
            "lang": "en",
        },
        {
            "name": "TRT Haber Dünya",
            "url": "https://www.trthaber.com/dunya_articles.rss",
            "lang": "tr",
        },
        {
            "name": "Anadolu Ajansı - Dünya",
            "url": "https://www.aa.com.tr/tr/rss/default?cat=dunya",
            "lang": "tr",
        },
    ],
    "teknoloji": [
        {
            "name": "Anadolu Ajansı - Bilim Teknoloji",
            "url": "https://www.aa.com.tr/tr/rss/default?cat=bilim-teknoloji",
            "lang": "tr",
        },
        {
            "name": "TRT Haber Bilim Teknoloji",
            "url": "https://www.trthaber.com/bilim_teknoloji_articles.rss",
            "lang": "tr",
        },
    ],
    "spor": [
        {
            "name": "TRT Spor",
            "url": "https://www.trtspor.com.tr/rss/gundem.rss",
            "lang": "tr",
        },
    ],
    "genel": [
        {
            "name": "NTV Son Dakika",
            "url": "https://www.ntv.com.tr/son-dakika.rss",
            "lang": "tr",
        },
    ],
}

# ─── Piyasa Sembolleri (yfinance) ────────────────────────────
MARKET_SYMBOLS = {
    "USD/TRY": "USDTRY=X",
    "EUR/TRY": "EURTRY=X",
    "GBP/TRY": "GBPTRY=X",
    "Altın (Ons)": "GC=F",
    "BIST 100": "XU100.IS",
    "S&P 500": "^GSPC",
    "Bitcoin": "BTC-USD",
}

# ─── Kategori Ağırlıkları ────────────────────────────────────
# Rapordaki haber sayısını belirler
CATEGORY_LIMITS = {
    "ekonomi": 5,
    "siyaset": 5,
    "dunya": 3,
    "teknoloji": 2,
    "spor": 1,
    "genel": 2,
}

# ─── Zamanlama ────────────────────────────────────────────────
MORNING_REPORT_HOUR = 8   # 08:00 TR
EVENING_REPORT_HOUR = 20  # 20:00 TR

# ─── Hikaye Takibi ───────────────────────────────────────────
MAX_ACTIVE_STORIES = 10
STORY_ARCHIVE_DAYS = 14

# ─── Ekonomi Takvimi ─────────────────────────────────────────
ECONOMIC_CALENDAR_COUNTRIES = ["turkey", "united-states", "euro-zone", "germany", "united-kingdom"]
ECONOMIC_CALENDAR_IMPORTANCE = ["high", "medium"]  # Düşük önemdekiler atlanır

# ─── Veri Dosyaları ───────────────────────────────────────────
TRACKED_STORIES_FILE = DATA_DIR / "tracked_stories.json"
LEARNED_CONCEPTS_FILE = DATA_DIR / "learned_concepts.json"
QUIZ_HISTORY_FILE = DATA_DIR / "quiz_history.json"
