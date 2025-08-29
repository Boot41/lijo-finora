"""Configuration settings for the document parser and RAG pipeline."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMADB_DIR = DATA_DIR / "chromadb"

# Ensure data directories exist
DATA_DIR.mkdir(exist_ok=True)
CHROMADB_DIR.mkdir(exist_ok=True)

# Model configurations
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_TOKENS = 512  # Chunk size for sentence transformers
CHUNK_OVERLAP = 50

# ChromaDB settings
CHROMADB_PATH = str(CHROMADB_DIR)
COLLECTION_NAME = "document_chunks"

# Chat settings
DEFAULT_MODEL = "gemini-pro"  # Google Gemini model
TEMPERATURE = 0.7
MAX_SEARCH_RESULTS = 5

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Chunking settings
MERGE_PEERS = True
MIN_CHUNK_SIZE = 100
