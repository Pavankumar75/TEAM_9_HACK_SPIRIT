
import numpy as np
import logging
from typing import List, Dict
from groq import Groq
import sys
import os

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from config import GROQ_API_KEY, GROQ_MODEL
    from utils_embeddings import get_embedding
except ImportError:
    from src.config import GROQ_API_KEY, GROQ_MODEL
    from src.utils_embeddings import get_embedding

# Basic cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class RAGEngine:
    def __init__(self, mongo_store):
        self.store = mongo_store
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model_name = GROQ_MODEL

    def retrieve(self, query: str, top_k=5, date_filter=None):
        """
        Retrieves relevant articles based on vector similarity.
        Optionally filters by date (string match on Published field).
        """
        try:
            # 1. Get Query Embedding locally
            query_embedding = get_embedding(query)
            
            if not query_embedding:
                return []

            # 2. Build Query Filter
            mongo_query = {"embedding": {"$exists": True, "$ne": []}}
            if date_filter:
                # Simple string match for date in published field (YYYY-MM-DD or similar)
                mongo_query["published"] = {"$regex": date_filter, "$options": "i"}

            # 3. Fetch all candidates matching filter
            candidates = list(self.store.collection.find(mongo_query))
            
            scored_candidates = []
            for doc in candidates:
                try:
                    score = cosine_similarity(query_embedding, doc['embedding'])
                    scored_candidates.append((score, doc))
                except:
                    continue
            
            # 4. Sort and slice
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in scored_candidates[:top_k]]

        except Exception as e:
            logging.error(f"Retrieval error: {e}")
            return []

    def answer_query(self, query: str):
        """
        Generates an answer using RAG.
        """
        # Extract potential date from query (simple YYYY-MM-DD regex)
        import re
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        date_match = re.search(date_pattern, query)
        date_filter = date_match.group(0) if date_match else None
        
        context_docs = self.retrieve(query, date_filter=date_filter)
        if not context_docs:
            if date_filter:
                return f"No news found specifically for the date {date_filter} matching your query."
            return "No relevant news found to answer your query."

        # Format context
        context_text = "\n\n".join([f"Source: {doc.get('title')}\nDate: {doc.get('published')}\nSummary: {doc.get('llm_summary')}" for doc in context_docs])
        
        prompt = f"""
        You are a News Intelligence Agent. Use the provided news summaries to answer the user's question.
        
        Rules:
        1. Answer strictly based on the provided context.
        2. If the context contains relevant information, summarize it to answer the question.
        3. Mention the source titles when possible.
        4. If the context is empty or irrelevant, politely state you don't have that info.

        News Context:
        {context_text}

        User Question: {query}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful news assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
