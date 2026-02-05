import os
import sys
import shutil
from typing import List

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import src.config as config

def ingest_file(file_path: str, file_type: str):
    """
    Generic ingestion for PDF and Text files into ChromaDB.
    """
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    print(f"Start ingesting {file_path}...")

    # 1. Load Document
    if file_type.lower() == 'pdf':
        loader = PyPDFLoader(file_path)
    elif file_type.lower() == 'txt':
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        print(f"Unsupported file type for vector ingestion: {file_type}")
        return

    documents = loader.load()
    print(f"Loaded {len(documents)} document(s).")

    # 2. Split Text
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks.")

    # 3. Create Embeddings
    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)

    # 4. Store in ChromaDB
    print(f"Persisting to ChromaDB at {config.CHROMA_DB_DIR}...")
    
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=config.CHROMA_DB_DIR,
        collection_name=config.COLLECTION_NAME
    )
    
    print("Ingestion complete!")

def ingest_pdf(pdf_path: str):
    """Wrapper for backward compatibility"""
    ingest_file(pdf_path, 'pdf')

def ingest_text(txt_path: str):
    """Wrapper for text ingestion"""
    ingest_file(txt_path, 'txt')

if __name__ == "__main__":
    # Example usage
    pdf_file = "Helix_Pro_Policy_v2.pdf"
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), pdf_file)
    
    ingest_pdf(file_path)
