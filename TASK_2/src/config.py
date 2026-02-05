import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configs removed
# MONGO_URI = os.getenv("MONGO_URI") 

CHROMA_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "policy_documents")

LLM_MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
