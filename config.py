import os

# Base Directory Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCUMENTS_FOLDER = os.path.join(BASE_DIR, "documents")
INDEX_FOLDER = os.path.join(BASE_DIR, "index")

# Ollama Model Configurations
# Using nomic-embed-text for fast local embeddings
EMBEDDING_MODEL = "nomic-embed-text"

# Using llama3.2:1b for sub-second CPU response times
CHAT_MODEL = "llama3.2:1b"

# Retrieval Settings
# TOP_K specifies how many relevant document chunks to pull from FAISS
TOP_K = 10