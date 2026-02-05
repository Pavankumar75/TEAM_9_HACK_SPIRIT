# 🧬 Helix HR Intelligence Bot

**Enterprise-grade Retrieval Augmented Generation (RAG) System for HR Data Analytics.**

This application integrates unstructured corporate policies (PDFs) with structured employee data (CSV, Excel, JSON) to provide a unified, intelligent chat interface. It leverages **Llama 3.2** (via Ollama) and a **Hybrid RAG** architecture to route questions to the correct data source—whether it requires semantic search or precise data aggregation.

---

## 🚀 Key Features

*   **Hybrid RAG Architecture**: Automatically routes user queries:
    *   **"Policy" Mode**: Uses **ChromaDB** vector search for unstructured documents (e.g., *Helix_Pro_Policy_v2.pdf*).
    *   **"Data" Mode**: Uses a **LangChain Pandas Agent** to query, filter, and aggregate structured data (e.g., *employee_master.csv*, *attendance_logs.json*).
    *   **"Hybrid" Mode**: Combines policy context with data lookups (e.g., "Is John's leave valid according to policy?").
*   **Multi-Format Ingestion**: Supports drag-and-drop upload for:
    *   📄 **PDF / TXT**: Vectorized for semantic search.
    *   📊 **CSV / Excel / JSON**: Loaded into DataFrames for SQL-like analytics.
*   **Local Privacy**: Powered by local LLMs (**Ollama**) and local vector storage (**ChromaDB**)—no data leaves your environment.
*   **Premium UI**: Built with **Streamlit**, featuring a modern dark theme, real-time ingestion status, and source citations.

---

## 🛠️ Tech Stack

*   **Frontend**: Streamlit
*   **LLM Engine**: Ollama (Llama 3.2:3b)
*   **Framework**: LangChain (Core, Community, Experimental)
*   **Vector Store**: ChromaDB (Local persistent storage)
*   **Data Processing**: Pandas, OpenPyXL, PyPDF
*   **Embeddings**: HuggingFace (`all-MiniLM-L6-v2`)

---

## ⚙️ Installation & Setup

### 1. Prerequisites
*   **Python 3.10+**
*   **Ollama Desktop**: [Download Here](https://ollama.com/)
    *   Pull the model: `ollama pull llama3.2:3b`

### 2. Clone Repository
```bash
git clone <your-repo-url>
cd helix-hr-bot
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root (optional if using defaults):
```ini
# .env
CHROMA_DB_DIR=chroma_db
COLLECTION_NAME=policy_documents
LLM_MODEL=llama3.2:3b
```

---

## ▶️ Usage

### 1. Run the Application
```bash
streamlit run app.py
```

### 2. Ingest Data
*   **Policies**: Use the sidebar to upload `Helix_Pro_Policy_v2.pdf`. Click **"Process & Ingest File"**. This builds the vector index.
*   **Employee Data**: Upload `employee_master.csv`, `leave_intelligence.xlsx`, or `attendance_logs_detailed.json`. These are hot-reloaded into the analysis engine.

### 3. Chat
Ask questions in natural language:
*   *Global Policy*: "What is the maternity leave duration?"
*   *Specific Data*: "How many days was EMP1001 absent in November?"
*   *Complex*: "List all employees in the IT department who have taken more than 5 days leave."

---

## 📂 Project Structure

```text
├── chrome_db/               # Persistent Vector Store (Auto-generated)
├── data/                    # Raw data files storage
├── src/
│   ├── config.py            # Configuration loader
│   ├── generation.py        # RAG Logic, Router, and LLM Chains
│   ├── ingestion_*.py       # Scripts for PDF, CSV, JSON ingestion
│   └── retrieval.py         # Retrievers & Pandas Agent setup
├── app.py                   # Main Streamlit Application
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

---

## 🛡️ Data Integrity & Reliability

*   **Date Normalization**: All incoming date fields are standardized to `YYYY-MM-DD` to ensure accurate temporal queries.
*   **Guardrails**: The bot is prompted to strictly cite sources and refuse to answer if data is insufficient, minimizing hallucinations.
*   **Error Handling**: Robust feedback loops for file uploads and query parsing errors.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

**© 2026 Helix Corporation**
