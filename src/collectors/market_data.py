import logging
from typing import List, Dict, Any
import yfinance as yf

from src import config
from src.utils.helpers import network_timeout

logger = logging.getLogger(__name__)

def get_market_data() -> List[Dict[str, Any]]:
    """
    yfinance kütüphanesini kullanarak piyasa verilerini çeker.
    
    Returns:
        List[Dict[str, Any]]: Piyasa verilerinin listesi.
    """
    logger.info("Piyasa verileri çekiliyor...")
    market_data = []
    
    for name, symbol in config.MARKET_SYMBOLS.items():
        try:
            ticker = yf.Ticker(symbol)
            # yfinance bu sürümde timeout parametresi kabul etmiyor.
            with network_timeout(15):
                hist = ticker.history(period="2d")
            
            if hist.empty or len(hist) < 1:
                logger.warning(f"{symbol} ({name}) için veri bulunamadı.")
                continue
                
            current_price = float(hist['Close'].iloc[-1])
            
            if len(hist) >= 2:
                prev_price = float(hist['Close'].iloc[-2])
                change_percent = ((current_price - prev_price) / prev_price) * 100
            else:
                change_percent = 0.0
                
            if change_percent > 0:
                direction = "up"
            elif change_percent < 0:
                direction = "down"
            else:
                direction = "flat"
                
            # Fiyatı mantıklı basamaklara yuvarla (döviz/hisse/kripto)
            formatted_price = round(current_price, 2) if current_price >= 10 else round(current_price, 4)

            market_data.append({
                "name": name,
                "symbol": symbol,
                "current_price": formatted_price,
                "change_percent": round(change_percent, 2),
                "direction": direction
            })
            
        except Exception as e:
            logger.error(f"{symbol} ({name}) verisi çekilirken hata oluştu: {e}")
            
    logger.info(f"Toplam {len(market_data)} adet piyasa verisi çekildi.")
    return market_data
