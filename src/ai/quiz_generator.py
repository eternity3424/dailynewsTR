"""
Quiz generator using Gemini.
Öğrenilen finansal okuryazarlık kavramlarından pekiştirici mini test soruları üretir.
Otomatik yeniden deneme ve model yedekleme (fallback) mekanizması içerir.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, List, Any

from google import genai

from src import config
from src.ai import prompts
from src.ai.summarizer import call_gemini_json_with_retry, clean_json_text

logger = logging.getLogger(__name__)


def generate_quiz(learned_concepts: List[Dict[str, Any]], quiz_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Öğrenilen kavramlara dayanarak 2 adet çoktan seçmeli test sorusu üretir.
    """
    if not config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY eksik, quiz üretilemedi.")
        return {"questions": []}

    default_concepts = [
        {"term": "Politika Faizi", "explanation": "Merkez bankalarının bankalara borç verirken uyguladığı faiz oranı."},
        {"term": "Enflasyon", "explanation": "Fiyatlar genel düzeyinin sürekli ve hissedilir artışıdır."},
        {"term": "Cari Açık", "explanation": "Bir ülkenin yurtdışından aldığı mal ve hizmetin, sattığından fazla olması."},
        {"term": "BIST 100", "explanation": "Borsa İstanbul'da işlem gören en yüksek piyasa değerine sahip 100 hissenin endeksi."},
    ]
    concepts_to_use = learned_concepts[-10:] if learned_concepts else default_concepts

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        prompt = prompts.QUIZ_PROMPT.format(
            learned_concepts=json.dumps(concepts_to_use, ensure_ascii=False),
            quiz_history=json.dumps(quiz_history[-5:], ensure_ascii=False)
        )

        raw_text = call_gemini_json_with_retry(client, prompt)
        cleaned = clean_json_text(raw_text)
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict) and "questions" in parsed:
            return parsed
        elif isinstance(parsed, list):
            return {"questions": parsed}
        return {"questions": []}
    except Exception as e:
        logger.error(f"Quiz üretilirken hata oluştu: {e}")
        return {"questions": []}
