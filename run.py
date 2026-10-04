import os
import sys
import subprocess
from pathlib import Path

# Required directory structure definition
DIRECTORIES = [
    "app/api",
    "app/audio",
    "app/nlp",
    "app/llm",
    "app/mom",
    "app/pipeline",
    "app/schemas",
    "app/database",
    "app/utils",
    "frontend/templates",
    "frontend/static/css",
    "frontend/static/js",
    "frontend/static/assets",
    "prompts",
    "models",
    "config",
    "data/sample_audio",
    "data/sample_transcripts",
    "data/annotations",
    "evaluation/ground_truth/transcripts",
    "evaluation/ground_truth/speakers",
    "evaluation/ground_truth/entities",
    "evaluation/ground_truth/actions",
    "tests",
    "outputs/transcripts",
    "outputs/translations",
    "outputs/reports",
    "outputs/mom",
]

DEFAULT_CONFIG_YAML = """project:
  name: MeetMemo
  supported_languages:
    - English
    - Hinglish

audio:
  supported_formats:
    - wav
    - mp3
    - m4a
    - flac
    - mp4

speech:
  model: base

diarization:
  enabled: true

nlp:
  ner: true
  keywords: true
  topics: true
  sentiment: true
  emotion: true
  intent: true
  actions: true
  decisions: true
  motions: true

llm:
  provider: openai
  model: gpt-3.5-turbo
  temperature: 0.2

mom:
  enabled: true
"""

DEFAULT_ENV_EXAMPLE = """# MeetMemo Configuration
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=gpt-3.5-turbo
HUGGINGFACE_TOKEN=your_huggingface_token_for_pyannote
DATABASE_URL=sqlite:///./meetmemo.db
"""

DEFAULT_MAIN_PY = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from app.api.routes_text import router as text_router
from app.api.routes_audio import router as audio_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_mom import router as mom_router
from app.api.routes_qa import router as qa_router

app = FastAPI(
    title="MeetMemo API",
    description="NLP-Based Conversation Intelligence System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("frontend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(text_router)
app.include_router(audio_router)
app.include_router(analysis_router)
app.include_router(mom_router)
app.include_router(qa_router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("frontend/templates/index.html"):
        with open("frontend/templates/index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MeetMemo API Service Running</h1>"
"""


def setup_environment():
    """Build project directory structure and generate default configs."""
    print("Initializing MeetMemo environment setup...")

    # Create directories
    for directory in DIRECTORIES:
        p = Path(directory)
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            print(f"  [+] Created directory: {directory}")

    # Create default config.yaml
    config_yaml = Path("config/config.yaml")
    if not config_yaml.exists():
        config_yaml.write_text(DEFAULT_CONFIG_YAML, encoding="utf-8")
        print("  [+] Generated default config/config.yaml")

    # Create default .env.example
    env_example = Path("config/.env.example")
    if not env_example.exists():
        env_example.write_text(DEFAULT_ENV_EXAMPLE, encoding="utf-8")
        print("  [+] Generated default config/.env.example")

    # Create default .env if missing
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(DEFAULT_ENV_EXAMPLE, encoding="utf-8")
        print("  [+] Generated initial .env file")

    # Create default app/main.py if missing
    main_py = Path("app/main.py")
    if not main_py.exists():
        main_py.write_text(DEFAULT_MAIN_PY, encoding="utf-8")
        print("  [+] Generated default app/main.py")

    print("System directory setup completed.\n")


def init_db():
    """Initialize SQLite database tables on startup."""
    try:
        from app.database.database import Base, engine
        from app.database.models import MeetingRecord

        print("Initializing database tables...")
        Base.metadata.create_all(bind=engine)
        print("  [+] Database tables verified/created successfully.\n")
    except Exception as e:
        print(f"  [!] Database initialization skipped or warning: {e}\n")


def start_server():
    """Launch the FastAPI server using Uvicorn."""
    print("Starting MeetMemo API Server...")
    try:
        import uvicorn

        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except ImportError:
        print("Error: uvicorn is not installed in your current environment.")
        print("Run: pip install uvicorn")
    except Exception as e:
        print(f"Failed to start server: {e}")


if __name__ == "__main__":
    setup_environment()
    init_db()
    start_server()