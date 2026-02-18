import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_answer(context: str, question: str) -> str:
    prompt = f"""
You are an assistant answering questions strictly from the context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"].strip()
