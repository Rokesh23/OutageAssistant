import os
import pickle
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
# Dynamic top_k for broad queries
    if any(phrase in query_raw for phrase in ["all incidents", "list incidents", "all rca", "show all"]):
        top_k = 15
    else:
        top_k = 5

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


_, metadata = load_index()
if metadata is None:
    metadata = []


def search_documents(query: str, top_k: int = TOP_K):
    index, metadata_data = load_index()
    
    if not metadata_data:
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    query_raw = query.strip().lower()
    # Normalize query terms (e.g. split on spaces, remove punctuation)
    query_terms = [t for t in re.split(r'\W+', query_raw) if t]

    matches = []
    
    for item in metadata_data:
        text = item.get("text", "") if isinstance(item, dict) else str(item)
        source = item.get("source", "RCA Record") if isinstance(item, dict) else "RCA Record"
        text_lower = text.lower()

        score = 0.0

        # 1. High-Priority Exact Match Boost (For Incident IDs like INC0176274 or key phrases)
        if query_raw in text_lower:
            score += 10.0

        # 2. Individual Term Matching
        for term in query_terms:
            if len(term) > 2 and term in text_lower:
                score += 2.0
            elif term in text_lower:
                score += 0.5

        # 3. Synonym / Keyword alias mapping for common outage terms
        aliases = {
            "timeout": ["504", "timed out", "slow", "gateway"],
            "504": ["timeout", "gateway", "bad gateway"],
            "502": ["bad gateway", "ui package"],
            "503": ["patching", "unavailable"],
            "ssl": ["cert", "certificate", "err_bad_ssl"]
        }

        for term in query_terms:
            if term in aliases:
                for alias in aliases[term]:
                    if alias in text_lower:
                        score += 1.5

        if score > 0:
            truncated_text = text[:1000] if len(text) > 1000 else text
            formatted_item = {
                "text": truncated_text,
                "source": source,
                "score": score
            }
            matches.append((score, formatted_item, f"Source ({source}): {truncated_text}"))
            
    matches.sort(key=lambda x: x[0], reverse=True)
    
    if not matches:
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    top_matches = matches[:top_k]
    matched_results = [m[1] for m in top_matches]
    context_str = "\n\n---\n\n".join([m[2] for m in top_matches])
    
    top_score = top_matches[0][0]
    confidence = min(round((top_score / 10.0) * 100, 1), 100.0)

    return context_str, matched_results, confidence


retrieve = search_documents
