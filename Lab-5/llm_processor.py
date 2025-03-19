import ollama


def process_text(text):
    model = "mistral"  # Change this to an available model in Ollama
    prompt = f"Summarize the following text:\n\n{text}"

    try:
        response = ollama.chat(model=model, messages=[{"role": "user",
                                                       "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        print(f"LLM Error: {e}")
        return "Failed to process text."
