
import json
import os
import sys
import logging
from typing import List, Dict
from groq import Groq

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from config import CATEGORIES, GROQ_API_KEY, GROQ_MODEL
    from utils_embeddings import get_embedding
except ImportError:
    from src.config import CATEGORIES, GROQ_API_KEY, GROQ_MODEL
    from src.utils_embeddings import get_embedding

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ArticleProcessor:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model_name = GROQ_MODEL

    def process_article(self, article: Dict) -> Dict:
        """
        Sends article text to LLM for Summarization, Classification, and Sentiment.
        """
        text = article.get('full_text', '') or article.get('summary_rss', '')
        # Truncate text if too long
        text = text[:6000] 

        prompt = f"""
        You are a News Intelligence Agent. Analyze the following news article text.
        
        Text: "{text}"

        Task:
        1. Summarize the article concisely (max 2 sentences).
        2. Classify it into exactly ONE of these categories: {CATEGORIES}.
        3. Determine the sentiment (Positive, Negative, Neutral).

        Output strictly in valid JSON format:
        {{
            "summary": "...",
            "category": "...",
            "sentiment": "..."
        }}
        """

        try:
            logging.info(f"Processing article: {article.get('title')[:30]}...")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model_name,
                response_format={"type": "json_object"},
            )

            result_json = chat_completion.choices[0].message.content
            parsed_result = json.loads(result_json)
            
            # Enrich original article
            article['llm_summary'] = parsed_result.get('summary', 'Error generating summary')
            article['category'] = parsed_result.get('category', 'Unclassified')
            article['sentiment'] = parsed_result.get('sentiment', 'Neutral')
            
            # Generate Embedding for RAG using local model
            try:
                article['embedding'] = get_embedding(text)
            except Exception as e:
                logging.warning(f"Embedding generation failed: {e}")
                article['embedding'] = []

            article['processed_at'] = pd.Timestamp.now().isoformat()
            
            return article

        except Exception as e:
            logging.error(f"LLM Processing Error: {e}")
            article['llm_summary'] = "Processing Failed"
            article['category'] = "Unclassified"
            article['sentiment'] = "Neutral"
            return article

    def process_batch(self, input_file="data/raw/latest_articles.json", output_file="data/processed/processed_articles.json"):
        import pandas as pd 
        
        if not os.path.exists(input_file):
            logging.error(f"Input file {input_file} not found.")
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)

        processed_articles = []
        for article in articles:
            processed = self.process_article(article)
            processed_articles.append(processed)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_articles, f, indent=4)
        
        logging.info(f"Processed {len(processed_articles)} articles. Saved to {output_file}")

if __name__ == "__main__":
    processor = ArticleProcessor()
    processor.process_batch()
