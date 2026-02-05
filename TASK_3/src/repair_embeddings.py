
import os
import sys
import logging
import pymongo

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from config import MONGO_URI, DB_NAME, COLLECTION_NAME
    from utils_embeddings import get_embedding
except ImportError:
    from src.config import MONGO_URI, DB_NAME, COLLECTION_NAME
    from src.utils_embeddings import get_embedding

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def repair_embeddings():
    print("Connecting to MongoDB...")
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Find documents with missing or empty embeddings
    cursor = collection.find({
        "$or": [
            {"embedding": {"$exists": False}},
            {"embedding": []},
            {"embedding": {"$size": 0}}
        ]
    })
    
    docs_to_repair = list(cursor)
    print(f"Found {len(docs_to_repair)} documents needing embeddings.")
    
    updated_count = 0
    
    for doc in docs_to_repair:
        try:
            # Use full_text if available, else summary
            text = doc.get('full_text') or doc.get('summary_rss') or doc.get('title', '')
            
            if not text:
                print(f"Skipping {doc['_id']} - No text content.")
                continue
                
            # Generate embedding
            embedding = get_embedding(text)
            
            if embedding:
                collection.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"embedding": embedding}}
                )
                updated_count += 1
                if updated_count % 5 == 0:
                    print(f"Updated {updated_count} articles...")
            else:
                print(f"Failed to generate embedding for {doc['_id']}")
                
        except Exception as e:
            print(f"Error updating doc {doc.get('title', 'Unknown')}: {e}")
            
    print(f"Repair Complete. Updated {updated_count} documents.")

if __name__ == "__main__":
    repair_embeddings()
