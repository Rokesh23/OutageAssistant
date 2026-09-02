import os
import pickle

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False

from config import INDEX_FILE, METADATA_FILE, TOP_K

def load_index():
    if not os.path.exists(INDEX_FILE) or not os.path.exists(METADATA_FILE):
        return None, None
    try:
        index = faiss.read_index(INDEX_FILE) if HAS_FAISS else None
        with open(METADATA_FILE, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    except Exception:
        return None, None

def search_documents(query: str, top_k: int = TOP_K):
    index, metadata = load_index()
    
    if metadata is None:
        return "Sorry, I could not find any RCA document related to your query in the indexed records."

    query_words = set(query.lower().split())
    matches = []
    
    for item in metadata:
        text = item.get("text", "")
        score = sum(1 for word in query_words if word in text.lower())
        if score > 0:
            source = item.get("source", "Unknown Source")
            matches.append((score, f"Source ({source}): {text}"))
            
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # If no keyword matches are found, return clear "Not Found" text
    if not matches:
        return "Sorry, I could not find any RCA document related to your query in the indexed records."

    results = [m[1] for m in matches[:top_k]]
    return "\n\n---\n\n".join(results)
