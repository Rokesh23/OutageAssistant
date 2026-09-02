import os
import ollama
from config import CHAT_MODEL

os.environ["OLLAMA_KEEP_ALIVE"] = "-1"

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

    stream = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True,
        keep_alive=-1,
        options={
            "temperature": 0.0,
            "num_predict": 300,
            "num_thread": 8,
        },
    )

    for chunk in stream:
        yield chunk["message"]["content"]

ask_llm = ask_llm_stream