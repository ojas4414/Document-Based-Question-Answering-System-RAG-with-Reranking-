import os

import requests

from backend.logger import setup

logger = setup()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def build_prompt(context: str, question: str) -> str:
    """The single prompt used by BOTH generation paths, so the two are comparable."""
    return f"""
You are an assistant answering questions strictly from the context.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}

Answer clearly and concisely.
"""


def _as_text(context) -> str:
    """main.py passes a list of chunks; accept either that or a plain string."""
    if isinstance(context, str):
        return context
    return "\n\n---\n\n".join(context)


def generate_with_openai(prompt: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    # Imported here so a missing openai package falls back instead of breaking startup.
    from openai import OpenAI

    client = OpenAI(api_key=api_key, timeout=30.0, max_retries=1)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def generate_with_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=180,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def generate_answer(context, question: str) -> str:
    """Try OpenAI first; fall back to the local Ollama server on any failure."""
    prompt = build_prompt(_as_text(context), question)

    try:
        answer = generate_with_openai(prompt)
        logger.info(f"GENERATION PATH = OPENAI (model={OPENAI_MODEL})")
        return answer
    except Exception as e:
        logger.warning(
            f"OpenAI generation failed ({type(e).__name__}: {e}) - falling back to Ollama"
        )

    try:
        answer = generate_with_ollama(prompt)
        logger.info(f"GENERATION PATH = OLLAMA FALLBACK (model={OLLAMA_MODEL})")
        return answer
    except Exception as e:
        logger.error(
            f"Ollama fallback also failed ({type(e).__name__}: {e})", exc_info=True
        )
        raise RuntimeError(
            "Both generation paths failed. Check OPENAI_API_KEY, or that "
            "`ollama serve` is running and the model is pulled."
        ) from e
