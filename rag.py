import os
import pickle

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for index files in root and inside 'index/' folder
POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, "index"),
    BASE_DIR
]

def resolve_file_paths():
    metadata_file = None
    index_file = None
    
    for path in POSSIBLE_PATHS:
        meta_test = os.path.join(path, "metadata.pkl")
        if os.path.exists(meta_test):
            metadata_file = meta_test
            
        for idx_name in ["index.faiss", "faiss_index.bin", "faiss_index.index"]:
            idx_test = os.path.join(path, idx_name)
            if os.path.exists(idx_test):
                index_file = idx_test
                break
                
        if metadata_file:
            break
            
    return index_file, metadata_file

INDEX_FILE, METADATA_FILE = resolve_file_paths()
TOP_K = 3

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False


def load_index():
    if not METADATA_FILE or not os.path.exists(METADATA_FILE):
        return None, None
    try:
        index = faiss.read_index(INDEX_FILE) if (HAS_FAISS and INDEX_FILE and os.path.exists(INDEX_FILE)) else None
        with open(METADATA_FILE, "rb") as f:
            metadata_data = pickle.load(f)
        return index, metadata_data
    except Exception:
        return None, None


# Load metadata globally so app.py displays accurate counts in sidebar
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
        # Check dictionary fields or string items
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        score = sum(1 for word in query_words if word in text.lower())
        if score > 0:
            source = item.get("source", "RCA Record") if isinstance(item, dict) else "RCA Record"
            formatted_item = {
                "text": text,
                "source": source,
                "score": score
            }
            matches.append((score, formatted_item, f"Source ({source}): {text}"))
            
    matches.sort(key=lambda x: x[0], reverse=True)
    
    if not matches:
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    top_matches = matches[:top_k]
    matched_results = [m[1] for m in top_matches]
    context_str = "\n\n---\n\n".join([m[2] for m in top_matches])
    
    top_score = top_matches[0][0]
    confidence = min(round((top_score / max(len(query_words), 1)) * 100, 1), 100.0)

    return context_str, matched_results, confidence


retrieve = search_documents
