import streamlit as st
import os
import sys

# Ensure src can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.ingest_unstructured import ingest_pdf, ingest_text
from src.generation import get_rag_system
import src.config as config

# --- Page Config ---
st.set_page_config(
    page_title="Helix HR Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
<style>
    /* Main Background and Text */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
        background: -webkit-linear-gradient(45deg, #58a6ff, #a371f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Chat Message Bubbles */
    .stChatMessage {
        background-color: #161b22;
        border-radius: 12px;
        border: 1px solid #30363d;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* User Message Override */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #238636 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #238636;
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 1px dashed #30363d;
        border-radius: 8px;
        padding: 20px;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #161b22;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- Main Layout ---

col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
with col2:
    st.title("Helix HR Intelligence")
    st.markdown("##### 🚀 Enterprise Data Assistant powered by RAG")

st.markdown("---")

# --- Sidebar: Configuration & Ingestion ---
with st.sidebar:
    st.markdown("### 🛠️ Control Panel")
    
    with st.expander("System Configuration", expanded=True):
        st.markdown(f"**LLM Model:** `{config.LLM_MODEL}`")
        if os.path.exists(config.CHROMA_DB_DIR):
            st.success("✅ Vector Store Active")
        else:
            st.warning("⚠️ Vector Store Empty")
            
    st.markdown("---")
    st.markdown("### 📂 Data Ingestion")
    st.info("Upload documents to enhance the bot's knowledge.")
    
    uploaded_file = st.file_uploader(
        "Drop files here", 
        type=["pdf", "txt", "csv", "json", "xlsx"],
        help="Supported formats: PDF, TXT, CSV, JSON, Excel"
    )
    
    if uploaded_file:
        file_ext = uploaded_file.name.split(".")[-1].lower()
        save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), uploaded_file.name)
        
        # Save file locally
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.markdown(f"**Detected:** `{file_ext.upper()}`")
        
        if st.button("🚀 Process & Ingest", use_container_width=True):
            with st.status("Processing Document...", expanded=True) as status:
                try:
                    if file_ext == "pdf":
                        st.write("📄 Extracting text from PDF...")
                        ingest_pdf(save_path)
                        st.write("🧠 Generating embeddings...")
                        st.write("💾 Saving to Vector Store...")
                        status.update(label="Ingestion Complete!", state="complete", expanded=False)
                        st.success("Ready for Retrieval!")
                        
                    elif file_ext == "txt":
                        st.write("📄 Reading text file...")
                        ingest_text(save_path)
                        status.update(label="Ingestion Complete!", state="complete", expanded=False)
                        st.success("Ready for Retrieval!")
                        
                    elif file_ext in ["csv", "json", "xlsx"]:
                        st.write("📊 Analyzing structured data...")
                        from src.retrieval import retriever
                        retriever.reload_data()
                        rag_system = get_rag_system()
                        rag_system.refresh_agent()
                        
                        st.write("💾 Updating DataFrames...")
                        status.update(label="Data Reloaded!", state="complete", expanded=False)
                        st.success("New data is live! You can ask questions about it now.")
                        
                    else:
                        status.update(label="Failed", state="error")
                        st.error("Unsupported file format.")
                        
                except Exception as e:
                    status.update(label="Error Occurred", state="error")
                    st.error(f"Details: {str(e)}")

# --- Main Grid: Chat ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm the Helix HR Bot. Ask me about company policies, employee data, or leave records."}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Type your question here..."):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant message
    response_text = None
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Analyzing Helix Knowledge Base..."):
            try:
                rag_system = get_rag_system()
                response_text, docs = rag_system.generate_response(prompt)
                
                # Display Result
                message_placeholder.markdown(response_text)
                
                # Citations
                if docs:
                    with st.expander("📚 View Referenced Source Material"):
                        for i, doc in enumerate(docs):
                            source_name = doc.metadata.get('source', 'Unknown Source')
                            page_num = doc.metadata.get('page', 'N/A')
                            st.markdown(f"**Source {i+1}:** `{source_name}` (Page {page_num})")
                            st.caption(f'"{doc.page_content[:300]}..."')
                            st.divider()
                            
            except Exception as e:
                response_text = f"❌ **Error:** I encountered an issue while processing your request.\n\n`{str(e)}`"
                message_placeholder.error(response_text)
    
    # Save to history
    if response_text:
        st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Helix HR Intelligence Bot | Powered by Llama 3.2 & ChromaDB | © 2026 Helix Corp
    </div>
    """, 
    unsafe_allow_html=True
)
