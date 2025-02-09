import os
from src.news_parser import NewsParser
from src.twitter_share import TwitterShare
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main2():
    logger = logging.getLogger(__name__)
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    csv_file = os.getenv("RSS_FILE", "rss_feed_list.csv")
    parser = NewsParser(mongodb_uri=mongodb_uri, csv_file=csv_file)
    twitter = TwitterShare(mongodb_uri=mongodb_uri)

    while True:
        try:
            parser.parse_feeds()
            logger.info("News parsed successfully and this is for debugging updater.sh!!!")
            twitter.share_latest_news()

            logger.info("Waiting 15 minutes before next batch...")
            time.sleep(3600)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            time.sleep(60)

def main():
    # MongoDB URI'yi çevre değişkeninden al
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    csv_file = os.getenv("RSS_FILE", "rss_feed_list.csv")
    
    # Parser ve twitter paylaşımını başlat
    parser = NewsParser(mongodb_uri=mongodb_uri, csv_file=csv_file)
    twitter = TwitterShare(mongodb_uri=mongodb_uri)
    
    while True:
        try:
            # Önce haberleri parse et ve kaydet
            parser.parse_feeds()
            logger.info("Haberler başarıyla parse edildi")
            
            # Sonra en son paylaşılmamış haberleri paylaş
            twitter.share_latest_news()
            
            # Bir sonraki çalıştırmadan önce 1 saat bekle
            logger.info("Bir sonraki batch için 1 saat bekleniyor...")
            time.sleep(3600)
            
        except Exception as e:
            logger.error(f"Ana döngüde hata: {str(e)}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    main()
