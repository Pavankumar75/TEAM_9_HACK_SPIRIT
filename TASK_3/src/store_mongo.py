
import pymongo
import json
import os
import sys
import logging
from typing import List, Dict

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from config import MONGO_URI, DB_NAME, COLLECTION_NAME
except ImportError:
    from src.config import MONGO_URI, DB_NAME, COLLECTION_NAME

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class MongoStore:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            self.collection = self.db[COLLECTION_NAME]
            
            # Create Index on Link (unique) to avoid duplicates
            self.collection.create_index("link", unique=True)
            logging.info("Connected to MongoDB and ensured indexes.")
        except Exception as e:
            logging.error(f"MongoDB Connection Error: {e}")

    def store_articles(self, json_path="data/processed/processed_articles.json"):
        if not os.path.exists(json_path):
            logging.error(f"File {json_path} not found.")
            return

        with open(json_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        count = 0
        for article in articles:
            try:
                # Upsert based on link
                self.collection.update_one(
                    {"link": article['link']},
                    {"$set": article},
                    upsert=True
                )
                count += 1
            except Exception as e:
                logging.error(f"Error storing article {article.get('title')}: {e}")

        logging.info(f"Successfully stored/updated {count} articles in MongoDB.")

    def get_recent_articles(self, limit=20):
        return list(self.collection.find().sort("published", -1).limit(limit))

    def get_stats(self):
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]
        return list(self.collection.aggregate(pipeline))

if __name__ == "__main__":
    store = MongoStore()
    store.store_articles()
