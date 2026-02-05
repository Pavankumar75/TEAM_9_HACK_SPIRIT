import os

# Configuration for NewsStream AI

# Classification Categories
CATEGORIES = [
    "Political",
    "Author Opinion",
    "Threatful",
    "Entertainment"
]

# RSS Feeds Configuration
RSS_FEEDS = {
    "Sports": [
        "https://www.espn.com/espn/rss/news",
        "http://sportstechie.net/feed",
        "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30&tags=fs/news"
    ],
    "Tech": [
        "https://techcrunch.com/feed/",
        "https://www.wired.com/feed/rss",
        "https://feeds.feedburner.com/TheHackersNews"
    ],
    "India": [
        "https://timesofindia.indiatimes.com/rss.cms",
        "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms",
        "https://feeds.feedburner.com/ndtvnews-top-stories",
        "https://www.thehindu.com/news/national/feeder/default.rss"
    ],
    "Auto": [
        "https://www.autocarindia.com/RSS/rss.ashx",
        "https://www.motor1.com/rss/news/all/",
        "https://www.team-bhp.com/rss/rss.xml"
    ]
}

# Database Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "news_stream_db"
COLLECTION_NAME = "articles"

# LLM Configuration
LLM_PROVIDER = "groq"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile" 

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Lightweight local model

# App Configuration
UPDATE_INTERVAL_SECONDS = 300  # 5 minutes
