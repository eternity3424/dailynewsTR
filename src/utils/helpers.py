"""Yardımcı fonksiyonlar."""

from __future__ import annotations

import re
import logging
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from typing import Any

logger = logging.getLogger(__name__)

TR_TZ = timezone(timedelta(hours=3))


def now_tr() -> datetime:
    """Şu anki Türkiye saatini döndürür."""
    return datetime.now(TR_TZ)


def deduplicate_news(articles: list[dict[str, Any]], threshold: float = 0.65) -> list[dict[str, Any]]:
    """Başlık benzerliğine göre tekrar eden haberleri filtreler."""
    unique: list[dict[str, Any]] = []
    for article in articles:
        title = article.get("title", "")
        is_dup = False
        for existing in unique:
            ratio = SequenceMatcher(None, title.lower(), existing["title"].lower()).ratio()
            if ratio >= threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(article)
    logger.info("Duplicate filtresi: %d → %d haber", len(articles), len(unique))
    return unique


def truncate_text(text: str, max_length: int = 500) -> str:
    """Metni belirli uzunlukta keser."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rsplit(" ", 1)[0] + "..."


def format_change(change: float | None) -> str:
    """Yüzde değişimi formatlı string'e çevirir. Örn: '▲ %2.35' veya '▼ %1.10'."""
    if change is None:
        return "— N/A"
    arrow = "▲" if change >= 0 else "▼"
    color = "green" if change >= 0 else "red"
    return f'<span style="color:{color}">{arrow} %{abs(change):.2f}</span>'


def get_report_period(mode: str) -> tuple[datetime, datetime]:
    """
    Rapor periyodunu hesaplar.
    - Sabah raporu: Dün 20:00 → Bugün 08:00
    - Akşam raporu: Bugün 08:00 → Bugün 20:00
    """
    now = now_tr()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)

    if mode == "morning":
        start = (today - timedelta(days=1)).replace(hour=20)
        end = today.replace(hour=8)
    else:  # evening
        start = today.replace(hour=8)
        end = today.replace(hour=20)

    return start, end


def clean_html(text: str) -> str:
    """HTML tag'lerini temizler."""
    return re.sub(r"<[^>]+>", "", text).strip()


def is_friday() -> bool:
    """Bugün Cuma mı?"""
    return now_tr().weekday() == 4
