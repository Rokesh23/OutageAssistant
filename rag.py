import os
import glob
import re

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")


def read_docx(file_path):
    """Extracts all text including paragraphs and tables from a .docx file."""
    if not HAS_DOCX:
        return ""
    
    doc = docx.Document(file_path)
    full_text = []

    # Extract paragraph text
    for para in doc.paragraphs:
        if para.text.strip():
            full_text.append(para.text.strip())

    # Extract table text
    for table in doc.tables:
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_data:
                full_text.append(" | ".join(row_data))

    return "\n".join(full_text)


def load_all_rca_docs():
    """Reads all .docx, .txt, and .md files directly from the docs/ directory."""
    documents = []
    if not os.path.exists(DOCS_DIR):
        return documents

    # Get all .docx, .txt, and .md files
    file_paths = (
        glob.glob(os.path.join(DOCS_DIR, "*.docx")) +
        glob.glob(os.path.join(DOCS_DIR, "*.txt")) +
        glob.glob(os.path.join(DOCS_DIR, "*.md"))
    )

    for path in file_paths:
        filename = os.path.basename(path)
        # Skip temporary Office lock files starting with ~$
        if filename.startswith("~$"):
            continue

        try:
            if filename.endswith(".docx"):
                content = read_docx(path)
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()

            if content:
                documents.append({
                    "source": filename,
                    "text": content
                })
        except Exception:
            continue

    return documents


def search_documents(query: str, top_k: int = 14):
    documents = load_all_rca_docs()

    if not documents:
        msg = "Sorry, I could not find any RCA documents (.docx) in the docs/ folder."
        return msg, [], 0.0

    query_raw = query.strip().lower()

    # Determine if broad request for all incidents/documents
    is_broad_query = any(phrase in query_raw for phrase in [
        "all incidents", "list incidents", "all rca", "show all", "total incidents", "all documents"
    ])

    matches = []
    query_terms = [t for t in re.split(r'\W+', query_raw) if t]

    for item in documents:
        text = item["text"]
        source = item["source"]
        text_lower = text.lower()
        score = 0.0

        if is_broad_query:
            score = 1.0
        else:
            # Exact string boost (e.g., incident numbers)
            if query_raw in text_lower:
                score += 10.0

            # Term matching
            for term in query_terms:
                if len(term) > 2 and term in text_lower:
                    score += 2.0
                elif term in text_lower:
                    score += 0.5

            # Synonym / Keyword aliases
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
            formatted_item = {
                "text": text,
                "source": source,
                "score": score
            }
            matches.append((score, formatted_item, f"Source ({source}):\n{text}"))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        msg = "Sorry, I could not find any RCA document related to your query in the indexed records."
        return msg, [], 0.0

    selected_matches = matches if is_broad_query else matches[:top_k]
    matched_results = [m[1] for m in selected_matches]
    context_str = "\n\n---\n\n".join([m[2] for m in selected_matches])

    top_score = selected_matches[0][0]
    confidence = min(round((top_score / 10.0) * 100, 1), 100.0)

    return context_str, matched_results, confidence


retrieve = search_documents
