"""
Günlük Haber Özet & Finansal Okuryazarlık Sistemi
Ana orchestrator — tüm bileşenleri koordine eder.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime

from src.collectors.rss_collector import collect_news
from src.collectors.market_data import get_market_data
from src.collectors.economic_calendar import get_economic_calendar
from src.ai.summarizer import summarize_news
from src.ai.quiz_generator import generate_quiz
from src.tracking.story_tracker import StoryTracker
from src.email.builder import build_email, build_subject
from src.email.sender import send_email
from src.utils.helpers import now_tr, is_friday

# Windows konsolunda UTF-8 / emoji desteği
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ─── Logging Ayarları ─────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

# Türkçe ay isimleri
TR_MONTHS = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
    5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
    9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık",
}

TR_DAYS = {
    0: "Pazartesi", 1: "Salı", 2: "Çarşamba", 3: "Perşembe",
    4: "Cuma", 5: "Cumartesi", 6: "Pazar",
}


def format_turkish_date(dt: datetime) -> str:
    """Tarihi Türkçe formatla: '6 Ekim 2026, Salı'"""
    day_name = TR_DAYS[dt.weekday()]
    month_name = TR_MONTHS[dt.month]
    return f"{dt.day} {month_name} {dt.year}, {day_name}"


def run(mode: str, test: bool = False) -> None:
    """
    Ana çalıştırma fonksiyonu.

    Args:
        mode: 'morning' veya 'evening'
        test: True ise e-posta göndermez, HTML'yi dosyaya yazar
    """
    current_time = now_tr()
    time_label = "Sabah" if mode == "morning" else "Akşam"
    date_str = format_turkish_date(current_time)

    logger.info("=" * 60)
    logger.info("📰 Günlük Haber Bülteni — %s %s", date_str, time_label)
    logger.info("=" * 60)

    # ── 1. Haberleri topla ────────────────────────────────────
    logger.info("📡 Haberler toplanıyor...")
    hours_back = 12 if mode == "morning" else 14
    articles = collect_news(hours_back=hours_back)
    logger.info("✅ %d haber toplandı", len(articles))

    if not articles:
        logger.warning("⚠️ Hiç haber bulunamadı. RSS kaynakları kontrol edilmeli.")
        # Boş haberle bile devam et — en azından piyasa verileri gönderilebilir

    # ── 2. Piyasa verilerini çek ──────────────────────────────
    logger.info("📊 Piyasa verileri çekiliyor...")
    market_data = get_market_data()
    logger.info("✅ %d piyasa verisi alındı", len(market_data))

    # ── 3. Ekonomi takvimini çek ──────────────────────────────
    logger.info("📅 Ekonomi takvimi alınıyor...")
    calendar_events = get_economic_calendar()
    logger.info("✅ %d ekonomi takvimi etkinliği alındı", len(calendar_events))

    # ── 4. Hikaye takipçisini yükle ───────────────────────────
    logger.info("🔄 Devam eden hikayeler yükleniyor...")
    tracker = StoryTracker()
    active_stories = tracker.get_active_stories()
    logger.info("✅ %d aktif hikaye takip ediliyor", len(active_stories))

    # ── 5. Gemini ile özetle ──────────────────────────────────
    logger.info("🧠 Gemini AI ile haberler özetleniyor...")
    ai_result = summarize_news(
        articles=articles,
        market_data=market_data,
        calendar_events=calendar_events,
        tracked_stories=active_stories,
        mode=mode,
    )
    logger.info("✅ AI özetleme tamamlandı")

    # ── 6. Hikayeleri güncelle ────────────────────────────────
    if ai_result.get("stories_update"):
        logger.info("🔄 Hikayeler güncelleniyor...")
        tracker.update_stories(ai_result["stories_update"])
        tracker.save()
        logger.info("✅ Hikayeler güncellendi")

    # ── 7. Yeni kavramları kaydet ─────────────────────────────
    summary = ai_result.get("summary", {})
    new_concepts = summary.get("new_concepts", [])
    if new_concepts:
        logger.info("📚 %d yeni finansal kavram kaydediliyor...", len(new_concepts))
        tracker.add_concepts(new_concepts)
        logger.info("✅ Kavramlar kaydedildi")

    # ── 8. Quiz oluştur ───────────────────────────────────────
    logger.info("❓ Mini quiz oluşturuluyor...")
    learned_concepts = tracker.get_concepts()
    quiz_history = tracker.get_quiz_history()
    quiz = generate_quiz(learned_concepts, quiz_history)
    if quiz and quiz.get("questions"):
        tracker.add_quiz(quiz)
        logger.info("✅ Quiz oluşturuldu (%d soru)", len(quiz["questions"]))
    else:
        logger.info("ℹ️ Quiz oluşturulamadı (henüz yeterli kavram yok olabilir)")
        quiz = {"questions": []}

    # ── 9. Rapor verisini hazırla ─────────────────────────────
    report_data = {
        "mode": mode,
        "date": date_str,
        "time_label": time_label,
        "market_data": market_data,
        "summary": summary,
        "tracked_stories": tracker.get_active_stories(),
        "tomorrow_preview": ai_result.get("tomorrow_preview", []),
        "quiz": quiz,
        "weekly_summary": ai_result.get("weekly_summary") if (mode == "evening" and is_friday()) else None,
    }

    # ── 10. HTML e-posta oluştur ──────────────────────────────
    logger.info("📧 HTML e-posta oluşturuluyor...")
    html_content = build_email(report_data)
    subject = build_subject(report_data)
    logger.info("✅ E-posta oluşturuldu: %s", subject)

    # ── 11. Gönder veya test ──────────────────────────────────
    if test:
        # Test modu: HTML'yi dosyaya yaz
        output_file = f"test_report_{mode}_{current_time.strftime('%Y%m%d_%H%M')}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info("🧪 TEST MODU: Rapor '%s' dosyasına yazıldı", output_file)
        logger.info("   Tarayıcıda açarak görünümü kontrol edebilirsiniz.")
    else:
        logger.info("📤 E-posta gönderiliyor...")
        success = send_email(subject, html_content)
        if success:
            logger.info("✅ E-posta başarıyla gönderildi!")
        else:
            logger.error("❌ E-posta gönderilemedi!")
            sys.exit(1)

    logger.info("=" * 60)
    logger.info("✅ Rapor tamamlandı!")
    logger.info("=" * 60)


def main() -> None:
    """Komut satırı giriş noktası."""
    parser = argparse.ArgumentParser(
        description="📰 Günlük Haber Özet & Finansal Okuryazarlık Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python -m src.main --mode morning          Sabah raporu gönder
  python -m src.main --mode evening          Akşam raporu gönder
  python -m src.main --mode morning --test   Sabah raporunu test et (e-posta göndermez)
        """,
    )
    parser.add_argument(
        "--mode",
        choices=["morning", "evening"],
        required=True,
        help="Rapor modu: 'morning' (sabah) veya 'evening' (akşam)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test modu: E-posta göndermez, HTML dosyası oluşturur",
    )

    args = parser.parse_args()

    try:
        run(mode=args.mode, test=args.test)
    except KeyboardInterrupt:
        logger.info("\n⛔ Kullanıcı tarafından iptal edildi.")
        sys.exit(0)
    except Exception as e:
        logger.exception("❌ Beklenmeyen hata: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
