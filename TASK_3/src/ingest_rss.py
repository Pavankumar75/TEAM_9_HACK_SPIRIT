
import feedparser
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from datetime import datetime
import os
import sys

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from config import RSS_FEEDS
except ImportError:
    # Fallback if running directly
    from src.config import RSS_FEEDS

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ingestion.log"),
        logging.StreamHandler()
    ]
)

class RSSIngester:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_full_text(self, url):
        """
        Fetches the full text content from a URL using BeautifulSoup.
        This attempts to get the main article content.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                logging.warning(f"Failed to fetch {url}: Status {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Heuristic to find the main article text
            # This is a generic approach; specific sites might need specific selectors
            # 1. Look for <article> tag
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
            else:
                # 2. Fallback to all <p> tags in the body
                paragraphs = soup.find_all('p')
            
            text_content = ' '.join([p.get_text() for p in paragraphs])
            return text_content.strip()
            
        except Exception as e:
            logging.error(f"Error fetching full text for {url}: {e}")
            return None

    def ingest_feeds(self):
        """
        Iterates through all configured feeds and fetches articles.
        Returns a list of dictionaries.
        """
        all_articles = []
        
        for category, urls in RSS_FEEDS.items():
            logging.info(f"Processing category: {category}")
            for url in urls:
                logging.info(f"Fetching RSS: {url}")
                try:
                    feed = feedparser.parse(url)
                    
                    if feed.bozo:
                        logging.warning(f"Bozo exception parsing {url}: {feed.bozo_exception}")
                        # Continue anyway as some content might be parsed
                        
                    for entry in feed.entries[:5]: # Limit to latest 5 per feed for speed/demo
                        article = {
                            "source_url": url,
                            "category_group": category,
                            "title": entry.get('title', 'No Title'),
                            "link": entry.get('link', ''),
                            "published": entry.get('published', datetime.now().isoformat()),
                            "summary_rss": entry.get('summary', ''),
                            "full_text": None,
                            "ingested_at": datetime.now().isoformat()
                        }
                        
                        # Fetch full text
                        if article['link']:
                            logging.info(f"Fetching full text for: {article['title'][:30]}...")
                            full_text = self.fetch_full_text(article['link'])
                            if full_text:
                                article['full_text'] = full_text
                            else:
                                article['full_text'] = article['summary_rss'] # Fallback
                        
                        all_articles.append(article)
                        time.sleep(1) # Polite delay
                        
                except Exception as e:
                    logging.error(f"Error processing feed {url}: {e}")
                    
        return all_articles

    def save_raw_data(self, articles, output_file="data/raw/latest_articles.json"):
        import json
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4)
        logging.info(f"Saved {len(articles)} articles to {output_file}")

if __name__ == "__main__":
    ingester = RSSIngester()
    articles = ingester.ingest_feeds()
    ingester.save_raw_data(articles)
    print(f"Ingestion Complete. Fetched {len(articles)} articles.")
