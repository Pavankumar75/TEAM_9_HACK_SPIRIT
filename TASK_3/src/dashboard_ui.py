
import streamlit as st
import pandas as pd
import plotly.express as px
import threading
import time
import sys
import os

# Add project root to path (one level up from this file)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

try:
    from src.config import RSS_FEEDS
    from src.ingest_rss import RSSIngester
    from src.process_llm import ArticleProcessor
    from src.store_mongo import MongoStore
    from src.rag_engine import RAGEngine
except ImportError:
    # Fallback if running directly from src folder
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import RSS_FEEDS
    from ingest_rss import RSSIngester
    from process_llm import ArticleProcessor
    from store_mongo import MongoStore
    from rag_engine import RAGEngine

# Initialize Components
mongo_store = MongoStore()
rag_engine = RAGEngine(mongo_store)

st.set_page_config(page_title="NewsStream AI", layout="wide", page_icon="📰")

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background: #0e1117;
        color: white;
    }
    .stCard {
        background-color: #262730;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📰 NewsStream AI: Real-Time Intelligence")

# Sidebar for controls
with st.sidebar:
    st.header("Pipeline Controls")
    if st.button("🔄 Trigger Ingestion Pipeline"):
        with st.status("Running Pipeline...", expanded=True) as status:
            # 1. Ingestion Phase
            start_ingest = time.time()
            st.write("1. Fetching RSS Feeds...")
            ingester = RSSIngester()
            articles = ingester.ingest_feeds()
            ingester.save_raw_data(articles)
            end_ingest = time.time()
            
            ingest_duration = end_ingest - start_ingest
            ingest_speed = len(articles) / ingest_duration if ingest_duration > 0 else 0
            
            # Save to session state
            st.session_state['last_ingest_speed'] = ingest_speed
            st.session_state['last_ingest_count'] = len(articles)
            
            st.success(f"Fetched {len(articles)} articles in {ingest_duration:.2f}s")
            
            # 2. Processing Phase
            if articles:
                start_process = time.time()
                st.write(f"2. Processing {len(articles)} Articles with LLM...")
                processor = ArticleProcessor()
                processor.process_batch()
                end_process = time.time()
                
                process_duration = end_process - start_process
                process_speed = len(articles) / process_duration if process_duration > 0 else 0
                
                # Save to session state
                st.session_state['last_process_speed'] = process_speed
                
                st.success(f"AI Processing complete in {process_duration:.2f}s")
            else:
                st.warning("No articles to process.")
            
            # 3. Storage Phase
            st.write("3. Storing and Indexing...")
            mongo_store.store_articles()
            
            status.update(label="Pipeline Complete!", state="complete", expanded=False)

    st.divider()
    
    # Performance Metrics Display
    st.header("⚡ System Performance")
    if 'last_ingest_speed' in st.session_state:
        st.metric(
            label="Ingestion Speed",
            value=f"{st.session_state['last_ingest_speed']:.2f} arts/s",
            delta=f"{st.session_state.get('last_ingest_count', 0)} articles"
        )
    
    if 'last_process_speed' in st.session_state:
        st.metric(
            label="LLM Processing Speed",
            value=f"{st.session_state['last_process_speed']:.2f} arts/s",
            help="Speed of Summarization + Classification + Sentiment Analysis"
        )

    st.divider()
    st.header("Active Feeds")
    for cat, urls in RSS_FEEDS.items():
        with st.expander(cat):
            for url in urls:
                st.caption(url)

# Main Content Tabs
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "💬 AI Chatbot", "📡 Live Feed"])

# Fetch Data
data = mongo_store.get_recent_articles(limit=100)
df = pd.DataFrame(data)

with tab1:
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Articles", len(df))
        col2.metric("Positive Sentiment", len(df[df['sentiment'] == 'Positive']))
        col3.metric("Political News", len(df[df['category'] == 'Political']))
        col4.metric("Threatful", len(df[df['category'] == 'Threatful']))
        
        row1_col1, row1_col2 = st.columns(2)
        
        with row1_col1:
            st.subheader("Sentiment Distribution")
            fig_sent = px.pie(df, names='sentiment', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_sent, use_container_width=True)
            
        with row1_col2:
            st.subheader("Category Breakdown")
            fig_cat = px.bar(df, x='category', color='category', title="Articles by Category")
            st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No data available. Please trigger the ingestion pipeline.")

with tab2:
    st.subheader("Ask the News Agent")
    # Chat Interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is the latest news on..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = rag_engine.answer_query(prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

with tab3:
    st.subheader("Latest Ingested Articles")
    if not df.empty:
        for index, row in df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="stCard">
                    <h3>{row.get('title')}</h3>
                    <p style='color: #aaa; font-size: 0.8rem;'>{row.get('published')} | <b>{row.get('category')}</b> | {row.get('source_url')}</p>
                    <p>{row.get('llm_summary')}</p>
                    <span style='background-color: #333; padding: 2px 6px; border-radius: 4px; font-size: 0.8em;'>{row.get('sentiment')}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.write("No articles found.")
