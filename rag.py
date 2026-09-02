import os
import pickle

# Hardcoded defaults to ensure no external config issues
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
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    query_words = set(query.lower().split())
    matches = []
    
    for item in metadata_data:
        text = item.get("text", "")
        # Calculate keyword overlap score
        score = sum(1 for word in query_words if word in text.lower())
        if score > 0:
            source = item.get("source", "Unknown Source")
            formatted_item = {
                "text": text,
                "source": source,
                "score": score
            }
            matches.append((score, formatted_item, f"Source ({source}): {text}"))
            
    # Sort matches by keyword relevance score in descending order
    matches.sort(key=lambda x: x[0], reverse=True)
    
    # If no keyword matches are found, return clear empty result tuple
    if not matches:
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    top_matches = matches[:top_k]
    matched_results = [m[1] for m in top_matches]
    context_str = "\n\n---\n\n".join([m[2] for m in top_matches])
    
    # Calculate a simple confidence percentage based on keyword match hits
    top_score = top_matches[0][0]
    confidence = min(round((top_score / max(len(query_words), 1)) * 100, 1), 100.0)

    return context_str, matched_results, confidence


# Alias retrieve to search_documents so app.py unpacks (context, results, confidence)
retrieve = search_documents
