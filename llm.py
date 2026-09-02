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
        "You are an expert IT Support RCA Assistant.\n"
        "Your task is to answer user queries strictly using ONLY the provided RCA Documents context.\n\n"
        "FORMATTING RULES:\n"
        "1. If the user asks to list incidents, show all incidents, or summarize RCAs, ALWAYS present the response in a complete, neat Markdown table format.\n"
        "2. Table headers for incident lists MUST be: | Incident Number | Project / Env | Start Time | End Time | Severity | Summary / Issue | Root Cause | Fix / Resolution |\n"
        "3. Table headers for RCA summaries MUST be: | Project | Total RCAs | Key Focus & Coverage | Storage / Source |\n"
        "4. Output EVERY incident found in the context. Do not truncate or omit rows.\n"
        "5. If specific information is missing or not found in context, explicitly state: 'Sorry, I could not find any RCA document related to your query in the indexed records.'"
    )

    safe_context = context[:12000] if context else ""
    user_prompt = f"RCA CONTEXT:\n{safe_context}\n\nUSER QUESTION:\n{question}"

    if not HAS_GROQ or not GROQ_API_KEY:
        yield "⚠️ **Groq API Key missing or not configured in Streamlit Secrets.**\n\n"
        yield "### 📄 Matched RCA Context:\n\n"
        yield context if context else "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    client = Groq(api_key=GROQ_API_KEY)

    # 1. Dynamically fetch models available for this specific API Key
    active_models = []
    try:
        models_list = client.models.list()
        active_models = [m.id for m in models_list.data]
    except Exception:
        pass

    preferred_order = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192"
    ]

    models_to_try = []
    if active_models:
        for p in preferred_order:
            if p in active_models:
                models_to_try.append(p)
        for m in active_models:
            if m not in models_to_try and ("llama" in m.lower() or "gpt" in m.lower() or "mixtral" in m.lower()):
                models_to_try.append(m)

    if not models_to_try:
        models_to_try = ["llama-3.3-70b-versatile"]

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
                max_tokens=1500,  # High token limit to allow complete table rendering
                stream=True,
            )

            for chunk in completion:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            return  # Successful completion!

        except Exception as e:
            last_error = e
            continue

    # Fallback output if all model calls hit errors
    yield f"⚠️ **Groq API Connection issue:** `{str(last_error)}`\n\n"
    yield f"### 📄 Matched Context:\n\n{context}"


ask_llm = ask_llm_stream
