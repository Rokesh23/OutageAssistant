import os

def ask_llm_stream(question, context):
    """
    Parses and formats retrieved RCA records cleanly without requiring 
    an external LLM API key or local Ollama service.
    """
    if not context or "could not find" in context.lower():
        yield "Sorry, I could not find any RCA document related to your query in the indexed records."
        return

    yield "### 📄 Matched Incident & RCA Records\n\n"

    # Split documents by source tags
    sections = context.split("Source (")
    
    found_match = False
    for section in sections:
        if not section.strip():
            continue
            
        found_match = True
        parts = section.split("):", 1)
        source_name = parts[0].strip() if len(parts) > 1 else "RCA Document"
        content = parts[1].strip() if len(parts) > 1 else section.strip()

        # Clean common raw extraction artifacts (e.g. repeated table headers)
        cleaned_content = content
        for dup in ["Incident Number", "Environment", "Application Name", "RCA Date", "Time", "Event / Action Taken"]:
            cleaned_content = cleaned_content.replace(f"{dup}{dup}{dup}", f"{dup}: ")
            cleaned_content = cleaned_content.replace(f"{dup}{dup}", f"{dup}: ")

        yield f"📌 **Source:** `{source_name}`\n\n"
        yield f"{cleaned_content}\n\n"
        yield "---\n\n"

    if not found_match:
        yield "Sorry, I could not find any RCA document related to your query in the indexed records."

ask_llm = ask_llm_stream
