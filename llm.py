import os
from config import CHAT_MODEL

# Try local Ollama first; fallback to direct context format
try:
    import ollama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False

def ask_llm_stream(question, context):
    system_prompt = (
        "You are an accurate IT Support RCA Assistant.\n"
        "Your task is to answer questions strictly using ONLY the provided RCA Documents.\n"
        "Do NOT mention outside systems unless explicitly written in the context.\n"
        "If the context does not contain relevant information, state clearly: "
        "'Sorry, I could not find any RCA document related to your query in the indexed records.'"
    )

    user_prompt = f"RCA DOCUMENTS CONTEXT:\n{context}\n\nUSER QUESTION:\n{question}\n\nProvide a direct, concise response based strictly on the context above."

    # If running locally with Ollama
    if HAS_OLLAMA:
        try:
            stream = ollama.chat(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True,
                options={"temperature": 0.0, "num_predict": 300}
            )
            for chunk in stream:
                yield chunk["message"]["content"]
            return
        except Exception:
            pass

    # Cloud Fallback (Formats context cleanly if LLM engine is offline)
    yield "### 📄 Relevant Outage & RCA Records Found:\n\n"
    if context and "Sorry" not in context:
        cleaned_context = context.replace("Incident NumberIncident Number", "Incident Number: ")
        yield cleaned_context
    else:
        yield "Sorry, I could not find any RCA document related to your query in the indexed records."

ask_llm = ask_llm_stream
