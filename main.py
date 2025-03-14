import os
from src.news_parser import NewsParser
from src.telegram_share import TelegramShare
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    csv_file = os.getenv("RSS_FILE", "rss_feed_list.csv")
    
    parser = NewsParser(mongodb_uri=mongodb_uri, csv_file=csv_file)
    telegram = TelegramShare(mongodb_uri=mongodb_uri)
    
    while True:
        try:
            # Haberleri parse et ve kaydet
            parser.parse_feeds()
            logger.info("Haberler başarıyla parse edildi")
            
            # Haberleri paylaş
            telegram.share_latest_news()
            
            # Bir sonraki çalıştırmadan önce 30 dakika bekle
            logger.info("Bir sonraki batch için 30 dakika bekleniyor...")
            time.sleep(1800)  # 30 dakika
            
        except Exception as e:
            logger.error(f"Ana döngüde hata: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    main()
