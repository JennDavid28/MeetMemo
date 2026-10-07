import os
import requests
from pathlib import Path

def load_prompt(template_name: str, **kwargs) -> str:
    prompt_path = Path("prompts") / template_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template '{template_name}' not found in prompts/")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    return template.format(**kwargs)


def call_llm(prompt: str, temperature: float = 0.2) -> str:
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("LLM_MODEL", "llama3.2:1b")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": 0.9,
            "repeat_penalty": 1.15,
            "num_ctx": 4096,
            "num_predict": 800
        }
    }

    try:
        # Connect timeout: 5s, Read timeout: 180s (allows local Ollama on CPU to generate full MoMs without premature timeout)
        response = requests.post(ollama_url, json=payload, timeout=(5, 180))
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as err:
        print(f"[LLM Notice] Ollama call failed or timed out ({err}). Transitioning to high-speed authentic NLP MoM engine.")
        raise RuntimeError(f"Ollama execution failed: {err}")