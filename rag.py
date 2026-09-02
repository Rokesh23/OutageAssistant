import os
import pickle

# Hardcoded defaults to ensure no dependency on config.py
INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "metadata.pkl"
TOP_K = 3

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
        return None, None
    try:
        index = faiss.read_index(INDEX_FILE) if HAS_FAISS else None
        with open(METADATA_FILE, "rb") as f:
            metadata_data = pickle.load(f)
        return index, metadata_data
    except Exception:
        return None, None

# Load metadata globally so "from rag import metadata" works in app.py
_, metadata = load_index()
if metadata is None:
    metadata = []

def search_documents(query: str, top_k: int = TOP_K):
    index, metadata_data = load_index()
    
    if not metadata_data:
        return "Sorry, I could not find any RCA document related to your query in the indexed records."

    query_words = set(query.lower().split())
    matches = []
    
    for item in metadata_data:
        text = item.get("text", "")
        # Calculate keyword overlap score
        score = sum(1 for word in query_words if word in text.lower())
        if score > 0:
            source = item.get("source", "Unknown Source")
            matches.append((score, f"Source ({source}): {text}"))
            
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # Return clear message if no keywords match
    if not matches:
        return "Sorry, I could not find any RCA document related to your query in the indexed records."

    results = [m[1] for m in matches[:top_k]]
    return "\n\n---\n\n".join(results)

# Alias retrieve to search_documents so "from rag import retrieve" works in app.py
retrieve = search_documents
