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

    # Limit context length to prevent token overflow
    safe_context = context[:1500] if context else ""

    user_prompt = f"RCA CONTEXT:\n{safe_context}\n\nUSER QUESTION:\n{question}"

    if not HAS_GROQ or not GROQ_API_KEY:
        yield "⚠️ **Groq API Key missing or not configured in Streamlit Secrets.**\n\n"
        yield "### 📄 Matched RCA Context:\n\n"
        yield context if context else "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    client = Groq(api_key=GROQ_API_KEY)
    
    # Active Groq production models (decommissioned models like mixtral-8x7b-32768 removed)
    models_to_try = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

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
            return  # Success

        except Exception as e:
            last_error = e
            continue

    # Fallback if Groq API fails
    yield f"⚠️ **Groq API Connection issue:** `{str(last_error)}`\n\n"
    yield f"### 📄 Matched Context:\n\n{context}"


ask_llm = ask_llm_stream
