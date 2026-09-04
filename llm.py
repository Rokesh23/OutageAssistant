import os
import streamlit as st

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))

try:
    from groq import Groq
    HAS_GROQ = True if GROQ_API_KEY else False
except ImportError:
    HAS_GROQ = False


def ask_llm(question, context):
    system_prompt = (
        "You are an expert IT Support RCA Assistant.\n"
        "Your task is to answer user queries strictly using ONLY the provided RCA Documents context.\n"
        "FORMATTING RULES:\n"
        "1. If the user asks to list incidents or show all documents/incidents, present the response in a complete Markdown table format.\n"
        "2. Include EVERY incident present in the context without omitting rows.\n"
        "3. If specific information is missing, explicitly state: 'Sorry, I could not find any RCA document related to your query in the indexed records.'"
    )

    safe_context = context[:8000] if context else ""
    user_prompt = f"RCA CONTEXT:\n{safe_context}\n\nUSER QUESTION:\n{question}"

    if not HAS_GROQ or not GROQ_API_KEY:
        return f"⚠️ **Groq API Key missing.**\n\n### Matched Context:\n{context}"

    client = Groq(api_key=GROQ_API_KEY)

    # Fetch available models for your specific key
    active_models = []
    try:
        models_list = client.models.list()
        active_models = [m.id for m in models_list.data]
    except Exception:
        pass

    preferred_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192"
    ]

    models_to_try = [m for m in preferred_models if m in active_models]
    if not models_to_try:
        models_to_try = active_models if active_models else ["llama-3.3-70b-versatile"]

    last_error = None
    for model_name in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                max_tokens=2000,
                stream=False  # Non-streaming prevents st.write_stream silent crashes
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = e
            continue

    return f"⚠️ **Groq Error:** `{str(last_error)}`\n\n### Raw Context:\n\n{context}"
