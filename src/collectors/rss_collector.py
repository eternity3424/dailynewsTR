import logging
import time
from calendar import timegm
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import feedparser

from src import config
from src.utils import helpers

logger = logging.getLogger(__name__)

def collect_news(hours_back: int = 12) -> List[Dict[str, Any]]:
    """
    Belirli bir zaman dilimindeki haberleri RSS kaynaklarından çeker.
    
    Args:
        hours_back (int): Kaç saat geçmişe dönük haberlerin çekileceği.
        
    Returns:
        List[Dict[str, Any]]: Çekilen haberlerin listesi.
    """
    logger.info(f"RSS kaynaklarından son {hours_back} saatin haberleri çekiliyor...")
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    all_news = []
    
    for category, feeds in config.RSS_FEEDS.items():
        for feed in feeds:
            feed_name = feed.get("name")
            feed_url = feed.get("url")
            feed_lang = feed.get("lang")
            
            try:
                # feedparser timeout parametresi desteklemiyor; socket
                # seviyesinde sınır koyarak takılmayı önlüyoruz.
                with helpers.network_timeout(20):
                    parsed_feed = feedparser.parse(feed_url)
                
                if parsed_feed.bozo and getattr(parsed_feed, 'bozo_exception', None):
                    logger.warning(f"'{feed_name}' kaynağından okuma sırasında hata oluştu: {parsed_feed.bozo_exception}")
                
                for entry in parsed_feed.entries:
                    try:
                        # Yayınlanma tarihini çıkar
                        parsed_time = entry.get('published_parsed') or entry.get('updated_parsed')
                        if parsed_time:
                            pub_date = datetime.fromtimestamp(timegm(parsed_time), timezone.utc)
                        else:
                            pub_date = datetime.now(timezone.utc)
                            
                        # Belirtilen saat aralığı dışındaki haberleri atla
                        if pub_date < cutoff_time:
                            continue
                            
                        # Html içeriklerini temizle
                        summary = entry.get('summary', entry.get('description', ''))
                        summary = helpers.clean_html(summary)
                        
                        news_item = {
                            "title": entry.get('title', ''),
                            "summary": summary,
                            "link": entry.get('link', ''),
                            "source_name": feed_name,
                            "source_url": feed_url,
                            "published_date": pub_date.isoformat(),
                            "category": category,
                            "lang": feed_lang
                        }
                        
                        all_news.append(news_item)
                        
                    except Exception as e:
                        logger.error(f"Haber öğesi işlenirken hata oluştu ({feed_name}): {e}")
                        
            except Exception as e:
                logger.error(f"'{feed_name}' feed'i işlenirken hata oluştu: {e}")
                
    # Tekrarlayan haberleri temizle
    unique_news = helpers.deduplicate_news(all_news)
    
    # Yayınlanma tarihine göre azalan şekilde (en yeni en üstte) sırala
    unique_news.sort(key=lambda x: x['published_date'], reverse=True)
    
    logger.info(f"Toplam {len(unique_news)} adet tekil haber çekildi.")
    return unique_news
