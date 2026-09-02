import os
import pickle
import re
import faiss
import numpy as np
import ollama
import streamlit as st

from config import *

os.environ["OLLAMA_KEEP_ALIVE"] = "-1"

@st.cache_resource
def load_faiss_assets():
    index_path = f"{INDEX_FOLDER}/index.faiss"
    meta_path = f"{INDEX_FOLDER}/metadata.pkl"
    
    if os.path.exists(index_path) and os.path.exists(meta_path):
        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata
    return None, []

index, metadata = load_faiss_assets()

def find_incident(question):
    match = re.search(r"(INC\d+|QA-INC-\d+)", question.upper())
    if match:
        return match.group()
    return None

def retrieve(question):
    if not index or not metadata:
        return "", [], {"score": 0, "level": "No Match"}

    query_lower = question.lower().strip()
    incident = find_incident(question)

    # 1. Exact Incident Match (e.g. QA-INC-003, INC0176274)
    if incident:
        incident_chunks = [
            item for item in metadata
            if item.get("incident", "").upper() == incident.upper()
        ]
        if incident_chunks:
            context = "\n\n".join([f"Source ({chunk['source']}): {chunk['text']}" for chunk in incident_chunks])
            return context[:6000], incident_chunks, {"score": 100, "level": "High"}

    # 2. Extract Key Terms & Substrings (Aspose, Elastic, Disk, etc.)
    stopwords = {"show", "total", "me", "incidents", "incident", "created", "any", "related", "was", "there", "is", "for", "list", "the", "in", "of", "please", "about", "have", "has"}
    words = [w for w in re.findall(r'\b\w+\b', query_lower) if w not in stopwords and len(w) > 2]

    if words:
        matching_chunks = []
        for item in metadata:
            text_lower = item.get("text", "").lower()
            source_lower = item.get("source", "").lower()
            
            # Match if ANY key search word exists in chunk text or file name
            if any(word in text_lower or word in source_lower for word in words):
                matching_chunks.append(item)

        if matching_chunks:
            context = "\n\n".join([f"Source ({chunk['source']}): {chunk['text']}" for chunk in matching_chunks])
            return context[:6000], matching_chunks, {"score": 95, "level": "High"}

    # 3. Vector Similarity Fallback
    try:
        response = ollama.embed(
            model=EMBEDDING_MODEL,
            input=question,
            keep_alive=-1
        )
        embedding = np.array([response["embeddings"][0]], dtype="float32")
        distances, indices = index.search(embedding, TOP_K)

        context = ""
        results = []
        DISTANCE_THRESHOLD = 2.5  # Increased threshold to avoid rejecting weak matches

        for i, idx in enumerate(indices[0]):
            if idx == -1 or distances[0][i] > DISTANCE_THRESHOLD:
                continue
            item = metadata[idx]
            context += f"Source ({item['source']}): {item['text']}\n\n"
            results.append(item)

        if results and context.strip():
            return context[:6000], results, {"score": 80, "level": "Medium"}
    except Exception as e:
        print(f"Embedding search error: {e}")

    return "", [], {"score": 0, "level": "No Match"}