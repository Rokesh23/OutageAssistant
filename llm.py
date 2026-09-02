import os
import streamlit as st

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))

try:
    from groq import Groq
    HAS_GROQ = True if GROQ_API_KEY else False
except ImportError:
    HAS_GROQ = False


def ask_llm_stream(question, context):
    system_prompt = (
        "You are an accurate IT Support RCA Assistant.\n"
        "Your task is to answer questions strictly using ONLY the provided RCA Documents.\n"
        "Do NOT mention outside systems like Teams, NotebookLM, or ChatGPT unless explicitly written in the context.\n"
        "Do NOT output template labels or debug text.\n"
        "If the context does not contain relevant information, state clearly: "
        "'Sorry, I could not find any RCA document related to your query in the indexed records.'"
    )

    # Safely trim context to max 2500 characters to prevent Groq 400 token overflow errors
    safe_context = context[:2500] if context else ""

    user_prompt = f"""
RCA DOCUMENTS CONTEXT:
{safe_context}

USER QUESTION:
{question}

Provide a direct, concise response based strictly on the context above.
"""

    if not HAS_GROQ or not GROQ_API_KEY:
        yield "⚠️ **Groq API Key missing or not configured in Streamlit Secrets.**\n\n"
        yield "### 📄 Matched RCA Context:\n\n"
        yield context if context else "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    client = Groq(api_key=GROQ_API_KEY)
    
    # Priority list of working models on Groq
    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192"
    ]
    
    available_models = []
    try:
        models_list = client.models.list()
        available_models = [m.id for m in models_list.data]
    except Exception:
        pass

    candidate_models = []
    for model in preferred_models:
        if not available_models or model in available_models:
            candidate_models.append(model)
            
    for model in available_models:
        if model not in candidate_models and ("llama" in model or "mixtral" in model or "gemma" in model):
            candidate_models.append(model)

    if not candidate_models:
        candidate_models = preferred_models

    last_error = None
    for model_name in candidate_models:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=400,
                stream=True,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return

        except Exception as e:
            last_error = e
            continue

    yield f"⚠️ **Groq API Connection issue:** `{str(last_error)}`\n\n"
    yield f"### 📄 Matched Context:\n\n{context}"


ask_llm = ask_llm_stream
