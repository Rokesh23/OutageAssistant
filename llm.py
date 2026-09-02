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
        "You are an IT Support RCA Assistant. Answer strictly using ONLY the provided RCA Documents.\n"
        "Keep your answer concise and direct.\n"
        "If no information is found, state: 'Sorry, I could not find any RCA document related to your query in the indexed records.'"
    )

    safe_context = context[:1500] if context else ""
    user_prompt = f"RCA CONTEXT:\n{safe_context}\n\nUSER QUESTION:\n{question}"

    if not HAS_GROQ or not GROQ_API_KEY:
        yield "⚠️ **Groq API Key missing or not configured in Streamlit Secrets.**\n\n"
        yield "### 📄 Matched RCA Context:\n\n"
        yield context if context else "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    client = Groq(api_key=GROQ_API_KEY)

    # 1. Fetch live models currently active on your Groq key
    active_models = []
    try:
        models_list = client.models.list()
        active_models = [m.id for m in models_list.data]
    except Exception:
        pass

    # Preferred active models sorted by availability in current Groq API specs
    preferred_order = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    models_to_try = []
    if active_models:
        for p in preferred_order:
            if p in active_models:
                models_to_try.append(p)
        for m in active_models:
            if m not in models_to_try and ("gpt" in m or "llama" in m or "qwen" in m):
                models_to_try.append(m)

    # Hard fallback list if list call fails
    if not models_to_try:
        models_to_try = ["openai/gpt-oss-20b", "llama-3.3-70b-versatile"]

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
                max_tokens=300,
                stream=True,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return  # Successful execution

        except Exception as e:
            last_error = e
            continue

    # Fallback response if all model endpoints hit issues
    yield f"⚠️ **Groq API Connection issue:** `{str(last_error)}`\n\n"
    yield f"### 📄 Matched Context:\n\n{context}"


ask_llm = ask_llm_stream
