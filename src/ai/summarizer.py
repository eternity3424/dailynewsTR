"""
AI summarizer module.
Gemini API kullanarak haberleri analiz eder, finansal okuryazarlık açıklamaları ekler,
hikayeleri günceller ve yarının beklentilerini oluşturur.
Otomatik yeniden deneme ve model yedekleme (fallback) mekanizması içerir.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Dict, List, Any

from google import genai
from google.genai import types

from src import config
from src.utils.helpers import is_friday
from src.ai import prompts

logger = logging.getLogger(__name__)


def clean_json_text(text: str) -> str:
    """Markdown kod bloklarını temizler ve salt JSON metnini döndürür."""
    clean = text.strip()
    if clean.startswith("```json"):
        clean = clean[7:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    return clean.strip()


def _is_quota_exhausted(err_str: str) -> bool:
    """
    429'un "dakikalık hız limiti" mi yoksa "kota tamamen tükenmiş" mi
    olduğunu ayırır. Kota tükenmişse beklemenin anlamı yoktur.
    """
    if "429" not in err_str and "RESOURCE_EXHAUSTED" not in err_str:
        return False
    exhausted_markers = (
        "exceeded your current quota",
        "quota exceeded",
        "billing",
        "free tier",
    )
    return any(marker in err_str.lower() for marker in exhausted_markers)


def call_gemini_json_with_retry(
    client: genai.Client,
    prompt: str,
    primary_model: str | None = None,
    max_retries_per_model: int = 3,
) -> str:
    """
    Gemini API'den JSON yanıt alır.
    503 veya 429 gibi yoğunluk durumlarında üstel bekleme ve model yedekleme uygular.
    """
    # Sıra önemli: en güvenilir model önce denenir, güçlü ama kotada sorunlu
    # modeller sona bırakılır. Hepsi sabitlenmiş GA model id'leridir — kayan
    # "-latest" alias'ları kullanılmıyor, çünkü arkasındaki model sessizce
    # değişebiliyor.
    candidate_models = [
        primary_model or config.GEMINI_MODEL,
        "gemini-3.6-flash",
        "gemini-3.8-flash",
    ]
    # Tekrarları kaldır
    models = list(dict.fromkeys(candidate_models))

    last_error = None
    for model in models:
        for attempt in range(max_retries_per_model):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.3,
                    ),
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                err_str = str(e)

                # Kota tamamen tükendiyse aynı modeli tekrar denemenin anlamı
                # yok; beklemek sadece run süresini uzatır. Sıradaki modele geç.
                if _is_quota_exhausted(err_str):
                    logger.warning(
                        f"{model} kotası tükenmiş, tekrar denenmeden "
                        "sonraki modele geçiliyor."
                    )
                    break

                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    wait_time = (2 ** attempt) + 1.5
                    logger.warning(
                        f"Gemini {model} geçici olarak meşgul, {wait_time:.1f}s bekleniyor "
                        f"(Model: {model}, Deneme {attempt + 1}/{max_retries_per_model})..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.warning(f"{model} modeli yanıt veremedi ({err_str[:120]}), bir sonraki modele geçiliyor.")
                    break

    if last_error:
        raise last_error
    return "{}"


def summarize_news(
    articles: List[Dict[str, Any]],
    market_data: List[Dict[str, Any]],
    calendar_events: List[Dict[str, Any]],
    tracked_stories: List[Dict[str, Any]],
    mode: str
) -> Dict[str, Any]:
    """
    Haberleri özetler, hikayeleri günceller, takvim beklentilerini ve (Cuma ise) haftalık özeti üretir.
    """
    if not config.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY ayarlanmamış! AI özetleme yapılamaz.")
        return {}

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini istemcisi başlatılamadı: {e}")
        return {}

    result: Dict[str, Any] = {
        "summary": {},
        "stories_update": {},
        "tomorrow_preview": [],
        "weekly_summary": None,
    }

    # ── 1. Haber Özeti ve Finansal Açıklamalar ─────────────────
    try:
        logger.info("Gemini ile haber özeti üretiliyor...")
        compact_articles = [
            {
                "title": a.get("title"),
                "summary": a.get("summary")[:280] if a.get("summary") else "",
                "source": a.get("source_name"),
                "url": a.get("link"),
                "category": a.get("category"),
            }
            for a in articles[:35]
        ]

        data = {
            "articles": compact_articles,
            "market_data": market_data,
            "calendar_events": calendar_events[:10],
        }
        prompt = prompts.NEWS_SUMMARY_PROMPT.format(data=json.dumps(data, ensure_ascii=False))

        raw_text = call_gemini_json_with_retry(client, prompt)
        cleaned = clean_json_text(raw_text)
        result["summary"] = json.loads(cleaned)
        logger.info("Haber özeti başarıyla oluşturuldu.")
    except Exception as e:
        logger.error(f"Haber özeti oluşturulurken hata: {e}")
        result["summary"] = {}

    time.sleep(1.0)

    # ── 2. Devam Eden Hikaye Takibi ──────────────────────────
    try:
        logger.info("Gemini ile hikaye takibi güncelleniyor...")
        prompt = prompts.STORY_TRACKING_PROMPT.format(
            tracked_stories=json.dumps(tracked_stories, ensure_ascii=False),
            today_news=json.dumps(articles[:20], ensure_ascii=False)
        )
        raw_text = call_gemini_json_with_retry(client, prompt)
        cleaned = clean_json_text(raw_text)
        result["stories_update"] = json.loads(cleaned)
        logger.info("Hikaye takibi güncellendi.")
    except Exception as e:
        logger.error(f"Hikaye takibi yapılırken hata: {e}")
        result["stories_update"] = {}

    time.sleep(1.0)

    # ── 3. Yarın/Bugün Ne Beklenmeli (Takvim Analizi) ──────────
    try:
        logger.info("Ekonomik takvim beklentileri analiz ediliyor...")
        events_to_analyze = calendar_events[:12] if calendar_events else [
            {"time": "Günün Akışı", "event_name": "Piyasa Takibi", "country": "Türkiye"}
        ]
        prompt = prompts.TOMORROW_PREVIEW_PROMPT.format(
            calendar_events=json.dumps(events_to_analyze, ensure_ascii=False)
        )
        raw_text = call_gemini_json_with_retry(client, prompt)
        cleaned = clean_json_text(raw_text)
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "events_preview" in parsed:
            result["tomorrow_preview"] = parsed["events_preview"]
        elif isinstance(parsed, list):
            result["tomorrow_preview"] = parsed
        else:
            result["tomorrow_preview"] = []
        logger.info(f"Takvim beklentileri hazırlandı ({len(result['tomorrow_preview'])} etkinlik).")
    except Exception as e:
        logger.error(f"Takvim beklentisi oluşturulurken hata: {e}")
        result["tomorrow_preview"] = []

    time.sleep(1.0)

    # ── 4. Haftalık Değerlendirme (Cuma Akşamı) ────────────────
    if mode == "evening" and is_friday():
        try:
            logger.info("Cuma akşamı haftalık değerlendirme hazırlanıyor...")
            headline = result.get("summary", {}).get("headline_news", {}).get("title", "")
            concepts = [c.get("term", "") for c in result.get("summary", {}).get("new_concepts", [])]
            weekly_data = {
                "headline": headline,
                "market_data": market_data,
                "concepts": concepts,
                "active_stories": [s.get("title", "") for s in tracked_stories],
            }
            prompt = prompts.WEEKLY_SUMMARY_PROMPT.format(
                weekly_summaries=json.dumps(weekly_data, ensure_ascii=False)
            )
            raw_text = call_gemini_json_with_retry(client, prompt)
            cleaned = clean_json_text(raw_text)
            result["weekly_summary"] = json.loads(cleaned)
            logger.info("Haftalık değerlendirme başarıyla üretildi.")
        except Exception as e:
            logger.error(f"Haftalık değerlendirme üretilirken hata: {e}")
            result["weekly_summary"] = None

    return result
