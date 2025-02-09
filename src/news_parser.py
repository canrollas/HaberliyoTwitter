import pandas as pd
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup
import pymongo
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsParser:
    def __init__(self, mongodb_uri: str, csv_file: str):
        self.client = pymongo.MongoClient(mongodb_uri)
        self.db = self.client.news_db
        self.collection = self.db.news
        self.csv_file = csv_file
        
        # Create unique index on url field
        self.collection.create_index([("url", pymongo.ASCENDING)], unique=True)
        
        # Configure feedparser
        feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def _extract_image_from_description(self, description: str) -> str:
        """Extract image URL from HTML description."""
        soup = BeautifulSoup(description, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag["src"]
        return None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def parse_feeds(self) -> None:
        """Parse all RSS feeds and save to MongoDB."""
        try:
            # Updated CSV reading to include source name
            df = pd.read_csv(self.csv_file, header=None, names=['rss_url', 'image_url', 'source_name'])
            
            current_time = datetime.utcnow().isoformat()
            
            for _, row in df.iterrows():
                try:
                    feed = feedparser.parse(row['rss_url'])
                    
                    if not feed.entries:
                        logger.warning(f"No entries found for {row['rss_url']}")
                        continue
                        
                    for entry in feed.entries:
                        # First check if URL already exists
                        existing_news = self.collection.find_one({"url": entry.get("link", "")})
                        
                        if existing_news:
                            logger.info(f"News already exists: {entry.get('title')} from {row['source_name']}")
                            continue
                            
                        description_html = entry.get("summary", "")
                        clean_description = self._clean_html(description_html)
                        image_url = (entry.get("media_content", [{}])[0].get("url") or 
                                   self._extract_image_from_description(description_html))
                        
                        news_item = {
                            "source": row['source_name'],
                            "date": entry.get("published", ""),
                            "image": image_url if image_url else row['image_url'],
                            "title": self._clean_html(entry.get("title")),
                            "description": clean_description,
                            "created_at": current_time,
                            "url": entry.get("link", ""),
                            "last_updated": datetime.utcnow(),
                            "shared": False
                        }
                        
                        # Insert only if URL doesn't exist
                        try:
                            self.collection.insert_one(news_item)
                            logger.info(f"Added new news: {news_item['title']} from {row['source_name']}")
                        except pymongo.errors.DuplicateKeyError:
                            logger.info(f"Duplicate URL found, skipping: {news_item['url']}")
                        
                except Exception as e:
                    logger.error(f"Error processing feed {row['rss_url']}: {str(e)}")
                    
            logger.info("Feed parsing completed successfully")
            
        except Exception as e:
            logger.error(f"Fatal error in parse_feeds: {str(e)}")
            raise

    def run_periodic(self, interval_seconds: int = 3600):
        """Run the parser periodically."""
        while True:
            logger.info("Starting news parsing cycle")
            self.parse_feeds()
            logger.info(f"Sleeping for {interval_seconds} seconds")
            time.sleep(interval_seconds) 