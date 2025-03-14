import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
import time
import requests
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk
from nltk.corpus import stopwords

# İlk kez çalıştırıyorsan stopwords veri setini indir
nltk.download('stopwords')

# Türkçe stop words listesi
turkish_stopwords = stopwords.words('turkish')
# .env dosyasını yükle
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_keywords(text, num_keywords=5):
    """Haber metninden önemli kelimeleri çıkar."""
    text = re.sub(r'[^\w\s]', '', text).lower()  # Temizleme işlemi

    # TF-IDF ile anahtar kelime çıkarımı
    vectorizer = TfidfVectorizer(stop_words=turkish_stopwords)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray().flatten()

    keywords = [feature_names[i] for i in scores.argsort()[-num_keywords:][::-1]]
    return keywords

class TelegramShare:
    def __init__(self, mongodb_uri: str = None):
        # MongoDB bağlantısını .env'den al
        self.client = MongoClient(mongodb_uri or os.getenv('MONGODB_URI'))
        self.db = self.client.news_db
        self.collection = self.db.news
        
        # Telegram API kimlik bilgilerini .env'den al
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID')
        
        # Son kullanılan kaynakları takip etmek için koleksiyon
        self.last_used = self.db.last_used_sources

    def send_message(self, message_text):
        """Telegram kanalına mesaj gönder."""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                "chat_id": self.channel_id,
                "text": message_text,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Telegram API hatası: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Mesaj gönderiminde hata: {str(e)}")
            return None

    def get_next_sources(self, limit=4):
        """Sıradaki kaynakları seç."""
        try:
            # Tüm kaynakları al
            all_sources = set(self.collection.distinct("source"))
            
            # Son kullanılan kaynakları al
            last_used = set(doc['source'] for doc in self.last_used.find({}, {'source': 1}))
            
            # Henüz kullanılmamış kaynakları seç
            available_sources = list(all_sources - last_used)
            
            # Eğer yeterli kullanılmamış kaynak yoksa, last_used'ı temizle
            if len(available_sources) < limit:
                self.last_used.delete_many({})
                available_sources = list(all_sources)
            
            # Limit kadar kaynak seç
            selected_sources = available_sources[:limit]
            
            # Seçilen kaynakları last_used'a ekle
            for source in selected_sources:
                self.last_used.insert_one({
                    'source': source,
                    'used_at': datetime.utcnow().isoformat()
                })
            
            return selected_sources
            
        except Exception as e:
            logger.error(f"Kaynak seçiminde hata: {str(e)}")
            return []

    def share_latest_news(self):
        """Günde maksimum 17 haber paylaşacak şekilde haberleri paylaş."""
        try:
            # Günlük paylaşım limitini kontrol et
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            daily_shares = self.collection.count_documents({
                "shared": True,
                "shared_at": {"$gte": today_start}
            })

            if daily_shares >= 17:
                logger.info("Günlük paylaşım limiti doldu (17/17). Yarını bekleyeceğiz.")
                return

            # Kaç paylaşım yapabileceğimizi hesapla
            remaining_shares = 17 - daily_shares
            
            # Her çalıştırmada maksimum 4 kaynak yerine, kalan limit kadar kaynak seç
            share_count = min(4, remaining_shares)
            sources = self.get_next_sources(limit=share_count)
            
            for source in sources:
                try:
                    # Bu kaynak için paylaşılmamış en son haberi bul
                    latest_news = self.collection.find_one(
                        {
                            "source": source,
                            "shared": {"$ne": True},
                            "created_at": {
                                "$gte": (datetime.utcnow() - timedelta(days=1)).isoformat()
                            }
                        },
                        sort=[("created_at", -1)]
                    )

                    if not latest_news:
                        logger.info(f"{source} için paylaşılmamış haber bulunamadı")
                        continue

                    keywords = extract_keywords(latest_news['title'])
                    hashtags = " ".join([f"#{word}" for word in keywords])

                    message_text = (
                        f"<b>{latest_news['title']}</b>\n\n"
                        f"Kaynak: {latest_news['source']}\n"
                        f"{latest_news['url']}\n\n"
                        f"#haber #{latest_news['source'].lower()} {hashtags}"
                    )
                    
                    response = self.send_message(message_text)
                    
                    if response and response.get('ok'):
                        # Haberi paylaşıldı olarak işaretle
                        self.collection.update_one(
                            {"_id": latest_news["_id"]},
                            {
                                "$set": {
                                    "shared": True,
                                    "shared_at": datetime.utcnow().isoformat(),
                                    "message_id": str(response['result']['message_id'])
                                }
                            }
                        )
                        logger.info(f"{source} kaynağından haber paylaşıldı: {latest_news['title']}")
                        time.sleep(300)  # Her paylaşım arasında 5 dakika bekle
                    else:
                        logger.warning(f"{source} kaynağından haber paylaşılamadı")
                        
                except Exception as e:
                    logger.error(f"{source} kaynağı işlenirken hata: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"share_latest_news'de hata: {str(e)}") 