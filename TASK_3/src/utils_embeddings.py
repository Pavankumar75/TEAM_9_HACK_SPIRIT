
import logging
from sentence_transformers import SentenceTransformer
import sys
import os

# Create a singleton for the model to avoid reloading it multiple times
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        try:
            logging.info("Loading SentenceTransformer model...")
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("Model loaded.")
        except Exception as e:
            logging.error(f"Failed to load embedding model: {e}")
            raise e
    return _model

def get_embedding(text):
    model = get_embedding_model()
    return model.encode(text).tolist()
