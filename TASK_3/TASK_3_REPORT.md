# Task 3: NewsStream AI - Analysis and Structure Report

## 1. System Architecture Analysis
The **NewsStream AI** platform is defined as a real-time news intelligence pipeline having 4 distinct stages:

### Stage 1: INGEST (RSS Monitor)
- **Objective**: Continuously monitor defined RSS feeds.
- **Target Feeds**:
    - **Sports**: (e.g., ESPN, Sports Techie)
    - **Tech**: (e.g., TechCrunch, Wired)
    - **India**: (e.g., Times of India, NDTV)
    - **Auto**: (e.g., Autocar India, Motor1)
- **Requirements**:
    - Full text extraction.
    - Graceful handling of failures.
    - Continuous mode.

### Stage 2: PROCESS (LLM Core)
- **Core Intelligence**:
    - **Summarization**: Generate concise article summaries.
    - **Classification**: Assign one of the required categories:
        - `Political`
        - `Author Opinion`
        - `Threatful`
        - `Entertainment`
    - **Sentiment Analysis**: Analyze and tag sentiment.

### Stage 3: STORE (Knowledge Base)
- **Database**: MongoDB (preferred for Structured/Unstructured data).
- **Indexing**: Vector indexing to support RAG (Retrieval-Augmented Generation) for the chatbot.

### Stage 4: SERVE (User Interface)
- **Interactive Chatbot**: Context-aware RAG to answer questions about the news.
- **Real-time Dashboard**:
    - Visualize data trends.
    - Sentiment breakdown.
    - Topic clustering.
- **JSON API**: Provide structured output.

## 2. Proposed Project Structure for TASK_3
We will implement a modular Python structure.

```text
TASK_3/
├── data/
│   ├── raw/                  # Temporary storage for fetched RSS content
│   └── processed/            # Cleaned JSONs ready for DB/Analysis
├── src/
│   ├── __init__.py
│   ├── config.py             # Feeds list, DB connection strings, Prompts
│   ├── ingest_rss.py         # Logic to poll RSS feeds and extract content
│   ├── process_llm.py        # Ollama integration for Summary, Class, Sentiment
│   ├── store_mongo.py        # Database operations (CRUD + Vector Search)
│   ├── rag_engine.py         # Retriever logic for the chatbot
│   └── dashboard_ui.py       # Streamlit/Dash application for the Frontend
├── notebooks/                # For testing individual components
├── requirements.txt          # Python dependencies
└── TASK_3_REPORT.md          # Project documentation
```

## 3. Implementation Workflow

1.  **Environment Setup**: Install `feedparser`, `pymongo`, `streamlit`, `ollama` (or `langchain`).
2.  **Ingestion Module**:
    - Build `ingest_rss.py` to fetch from the provided RSS URLs.
    - Parse XML, extract title, link, and description.
    - *Challenge*: Extracting "Full Text" might require `beautifulsoup` if the RSS only provides partial snippets.
3.  **Processing Module**:
    - Hook up the LLM (model choice: `llama3.2` or similar) in `process_llm.py`.
    - Create a strict prompt to ensure output JSON matches the required schema (Category, Sentiment, Summary).
4.  **Storage**:
    - Store the processed JSON in MongoDB.
    - Generate embeddings for the summary/text and store in a vector collection (or local vector store like Chroma if MongoDB Atlas Vector Search is not used).
5.  **User Interface**:
    - Build a Streamlit app.
    - **Tab 1: Dashboard**: Charts using `plotly` showing Sentiment distribution and Category counts.
    - **Tab 2: Chat**: Chat interface querying the RAG engine.
    - **Tab 3: Feed**: Live view of latest ingested articles.

## 4. Immediate Next Steps
- Create the folder structure.
- Create `src/config.py` with the RSS feed URLs.
- Create `src/ingest_rss.py`.
