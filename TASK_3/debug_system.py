
import os
import sys
import pymongo
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from config import MONGO_URI, DB_NAME, COLLECTION_NAME
    from utils_embeddings import get_embedding
    from rag_engine import RAGEngine, cosine_similarity
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def diagnose():
    print("--- DIAGNOSTIC START ---")
    
    # 1. MongoDB Check
    try:
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        count = collection.count_documents({})
        print(f"Total Articles in MongoDB: {count}")
        
        if count == 0:
            print("ERROR: Database is empty. Please run Ingestion from the Dashboard.")
            return

        # 2. Check for Sports articles
        # This regex check is case-insensitive for 'sports' in title, category, or summary
        sports_count = collection.count_documents({
            "$or": [
                {"category_group": {"$regex": "Sports", "$options": "i"}},
                {"title": {"$regex": "Sports", "$options": "i"}},
                {"llm_summary": {"$regex": "Sports", "$options": "i"}}
            ]
        })
        print(f"Articles matching 'Sports': {sports_count}")

        # 3. Check Embeddings
        sample_doc = collection.find_one()
        if 'embedding' not in sample_doc or not sample_doc['embedding']:
            print("ERROR: Sample document has no embedding!")
        else:
            emb_len = len(sample_doc['embedding'])
            print(f"Sample document has embedding of length: {emb_len}")
            
        # 4. Test Local Embedding Generation
        print("\nTesting Embedding Generation...")
        query = "latest sports news"
        try:
            query_emb = get_embedding(query)
            print(f"Generated query embedding of length: {len(query_emb)}")
        except Exception as e:
            print(f"ERROR generating embedding: {e}")
            return

        # 5. Test Retrieval Directly
        print("\nTesting RAG Retrieval logic...")
        try:
            candidates = list(collection.find({"embedding": {"$exists": True, "$ne": []}}))
            print(f"Found {len(candidates)} candidates with embeddings.")
            
            scored_candidates = []
            for doc in candidates:
                try:
                    score = cosine_similarity(query_emb, doc['embedding'])
                    scored_candidates.append((score, doc['title']))
                except Exception as e:
                    pass
            
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            print(f"Top 3 matches for '{query}':")
            for score, title in scored_candidates[:3]:
                print(f" - [{score:.4f}] {title}")
                
        except Exception as e:
            print(f"ERROR in retrieval test: {e}")

    except Exception as e:
        print(f"General Error: {e}")

    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    diagnose()
