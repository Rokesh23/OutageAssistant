import os
import streamlit as st

# Read Groq API key from Streamlit Secrets or Environment Variables
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

    user_prompt = f"""
RCA DOCUMENTS CONTEXT:
{context}

USER QUESTION:
{question}

Provide a direct, concise response based strictly on the context above.
"""

    if not HAS_GROQ:
        yield "⚠️ **Groq API Key missing.** Please configure `GROQ_API_KEY` in Streamlit Cloud Secrets.\n\n"
        yield "### 📄 Matched RCA Context:\n\n"
        yield context if context else "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    # List of stable models on Groq to try in order
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama3-8b-8192",
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]

    client = Groq(api_key=GROQ_API_KEY)
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
                max_tokens=500,
                stream=True,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return  # Successfully completed streaming

        except Exception as e:
            last_error = e
            continue  # Try next model if current model fails

    # If all candidate models failed
    yield f"⚠️ **Error connecting to Groq AI:** {str(last_error)}\n\n"
    yield f"### 📄 Matched Context:\n{context}"


ask_llm = ask_llm_stream
