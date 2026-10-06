"""
Ekonomik Takvim Veri Toplayıcı Modülü.
Investing.com üzerinden ekonomik takvim verilerini çeker.
curl_cffi ile Cloudflare/TLS korumasını aşar, başarısızlık durumunda güvenli yedekler sunar.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

try:
    from curl_cffi import requests
except ImportError:
    import requests  # fallback

from src import config

logger = logging.getLogger(__name__)


def get_economic_calendar() -> List[Dict[str, Any]]:
    """
    Investing.com üzerinden ekonomik takvim verilerini çeker.
    Bugün ve yarının etkinliklerini içerir.
    
    Returns:
        List[Dict[str, Any]]: Ekonomik etkinliklerin listesi.
    """
    logger.info("Ekonomik takvim verileri çekiliyor...")
    events: List[Dict[str, Any]] = []
    
    url = "https://www.investing.com/economic-calendar/"
    
    try:
        # curl_cffi ile chrome taklidi yaparak Cloudflare korumasını aşıyoruz
        try:
            response = requests.get(
                url,
                impersonate="chrome",
                timeout=20,
                headers={"Accept-Language": "en-US,en;q=0.9"}
            )
        except TypeError:
            # Standart requests fallback
            response = requests.get(
                url,
                timeout=20,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9"
                }
            )

        if response.status_code != 200:
            logger.warning(f"Ekonomik takvim sayfası HTTP {response.status_code} döndürdü.")
            return events

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Modern Investing.com takvim satırlarını bul (id yapısı: <id>-<date>-<Country>-<num>)
        rows = [t for t in soup.find_all("tr") if t.get("id") and len(t.get("id").split("-")) >= 4]
        
        allowed_countries = [c.lower() for c in config.ECONOMIC_CALENDAR_COUNTRIES]

        for row in rows:
            try:
                row_id = row.get("id", "")
                parts = row_id.split("-")
                country_name = parts[2] if len(parts) >= 3 else ""
                
                # Ülke filtresi (turkey, united states, germany, vb.)
                matched_country = None
                for c in allowed_countries:
                    c_clean = c.replace("-", "").replace(" ", "").lower()
                    if c_clean in country_name.lower():
                        matched_country = country_name
                        break
                        
                if not matched_country and allowed_countries:
                    continue

                # Önem derecesini belirle (yıldız sayısı)
                # Satırdaki svg yıldızları kontrol et
                svgs = row.find_all("svg")
                high_opacity_stars = 0
                for s in svgs:
                    classes = s.get("class", [])
                    if any("opacity-60" in c or "opacity-100" in c for c in classes):
                        high_opacity_stars += 1
                
                # Genellikle mobil ve masaüstü için çift svg bulunur (örn: 6 svg = 3 mobil, 3 masaüstü)
                if len(svgs) >= 6:
                    high_opacity_stars = high_opacity_stars // 2

                if high_opacity_stars >= 3:
                    importance = "high"
                elif high_opacity_stars == 2:
                    importance = "medium"
                else:
                    importance = "low"

                if importance not in config.ECONOMIC_CALENDAR_IMPORTANCE:
                    continue

                # Olay adını al
                event_link = row.find("a")
                event_name = ""
                if event_link:
                    event_name = event_link.get_text(separator=" ", strip=True)
                else:
                    event_td = row.find("td", class_=lambda x: x and "w-full" in x)
                    if event_td:
                        event_name = event_td.get_text(separator=" ", strip=True)

                if not event_name:
                    continue

                # Saat bilgisini al
                time_div = row.find("div", class_=lambda x: x and "text-sm" in x)
                time_str = time_div.get_text(strip=True) if time_div else ""

                events.append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": time_str or "Günün Etkinliği",
                    "country": matched_country or country_name,
                    "event_name": event_name,
                    "importance": importance,
                    "previous_value": "",
                    "forecast_value": "",
                })

            except Exception as e:
                logger.debug(f"Takvim satırı işlenirken hata: {e}")
                continue

        logger.info(f"Toplam {len(events)} adet filtrelenmiş ekonomik etkinlik çekildi.")

    except Exception as e:
        logger.warning(f"Ekonomik takvim çekilirken hata oluştu: {e}")

    return events
