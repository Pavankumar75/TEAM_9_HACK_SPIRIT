import os
import sys
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.chat_models import ChatOllama
import src.config as config
from src.ingest_structured import load_employee_master, load_leave_data
from src.ingest_semi_structured import load_attendance_logs

# Initialize Global DataFrames
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMP_CSV = os.path.join(BASE_DIR, "employee_master.csv")
LEAVE_XLSX = os.path.join(BASE_DIR, "leave_intelligence.xlsx")
ATTENDANCE_JSON = os.path.join(BASE_DIR, "attendance_logs_detailed.json")

class RetrievalManager:
    def __init__(self):
        print("Initializing RetrievalManager...")
        self.embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
        
        # ChromaDB Connection
        print(f"Loading ChromaDB from {config.CHROMA_DB_DIR}...")
        self.vector_store = Chroma(
            persist_directory=config.CHROMA_DB_DIR,
            embedding_function=self.embeddings,
            collection_name=config.COLLECTION_NAME
        )

        # Load DataFrames
        self.load_data()

    def load_data(self):
        """Loads or reloads the structured data."""
        print("Loading structured data...")
        self.df_emp = load_employee_master(EMP_CSV)
        self.df_leave = load_leave_data(LEAVE_XLSX)
        self.df_attendance = load_attendance_logs(ATTENDANCE_JSON)
        print("Data loaded.")

    def reload_data(self):
        """Public method to trigger reload."""
        self.load_data()
        # We also need to re-create the agent if the data changes, 
        # but the agent is created in generation.py using these DFs.
        # This implies we might need a way to signal the RAGSystem to refresh.

    def search_policy_documents(self, query: str, k: int = 3):
        """
        Performs semantic search on the policy documents in ChromaDB.
        """
        results = self.vector_store.similarity_search(query, k=k)
        return results

    def get_structured_data_agent(self, llm):
        """
        Returns a LangChain agent that can query the DataFrames.
        We pass all three DataFrames to it.
        """
        return create_pandas_dataframe_agent(
            llm,
            [self.df_emp, self.df_leave, self.df_attendance],
            verbose=True,
            allow_dangerous_code=True,
            handle_parsing_errors=True,
            agent_type="zero-shot-react-description",
            number_of_head_rows=5,
            max_iterations=30,  # Increased from default
            max_execution_time=None # Allow it to run as long as needed
        )

# Initialize global instance
retriever = RetrievalManager()
