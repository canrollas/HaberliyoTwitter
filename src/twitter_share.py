import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
import time
import requests
from requests_oauthlib import OAuth1
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


class TwitterShare:
    def __init__(self, mongodb_uri: str = None):
        # MongoDB bağlantısını .env'den al
        self.client = MongoClient(mongodb_uri or os.getenv('MONGODB_URI'))
        self.db = self.client.news_db
        self.collection = self.db.news
        
        # Twitter API kimlik bilgilerini .env'den al
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Twitter API ayarları
        self.api_url = "https://api.twitter.com/2/tweets"
        
        # OAuth 1.0a kurulumu
        self.auth = OAuth1(
            self.api_key,
            self.api_secret,
            self.access_token,
            self.access_token_secret
        )
        
        # Son kullanılan kaynakları takip etmek için koleksiyon
        self.last_used = self.db.last_used_sources

    def post_tweet(self, tweet_text):
        """Post a tweet using Twitter API v2 with OAuth 1.0a."""
        try:
            payload = {
                "text": tweet_text
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                auth=self.auth,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:  # Created
                return response.json()
            elif response.status_code == 429:  # Rate limit
                reset_time = int(response.headers.get("x-rate-limit-reset", time.time() + 900))
                print("Reset time",reset_time)
                wait_time = max(0, reset_time - time.time())
                logger.warning(f"Rate limit hit. Waiting {int(wait_time)} seconds...")
                time.sleep(wait_time + 5)  # 5 saniye ekstra bekleme
                return None
            else:
                logger.error(f"Twitter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
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
        """Her çalıştırmada 4 farklı kaynaktan haber paylaş."""
        try:
            # Sıradaki 4 kaynağı al
            sources = self.get_next_sources(limit=4)
            
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
                    keywords = extract_keywords(latest_news['title'])
                    hashtags = " ".join([f"#{word}" for word in keywords])

                    if latest_news:
                        tweet_text = (
                            f"{latest_news['title']}\n\n"
                            f"Kaynak: {latest_news['source']}\n"
                            f"{latest_news['url']}\n\n"
                            f"#haber #{latest_news['source'].lower()} {hashtags}"
                        )
                        
                        response = self.post_tweet(tweet_text)
                        
                        if response and 'data' in response:
                            # Haberi paylaşıldı olarak işaretle
                            self.collection.update_one(
                                {"_id": latest_news["_id"]},
                                {
                                    "$set": {
                                        "shared": True,
                                        "shared_at": datetime.utcnow().isoformat(),
                                        "tweet_id": str(response['data']['id'])
                                    }
                                }
                            )
                            logger.info(f"{source} kaynağından haber paylaşıldı: {latest_news['title']}")
                            time.sleep(120)  # Her tweet arasında 2 dakika bekle
                        else:
                            logger.warning(f"{source} kaynağından haber paylaşılamadı")
                            
                    else:
                        logger.info(f"{source} için paylaşılmamış haber bulunamadı")
                        
                except Exception as e:
                    logger.error(f"{source} kaynağı işlenirken hata: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"share_latest_news'de hata: {str(e)}")