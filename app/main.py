import os
import warnings

# Suppress HuggingFace Windows Symlink Warning
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore", category=UserWarning, module="huggingface_hub")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.api.routes_text import router as text_router
from app.api.routes_audio import router as audio_router
from app.api.routes_analysis import router as analysis_router
from app.api.routes_mom import router as mom_router
from app.api.routes_qa import router as qa_router

app = FastAPI(
    title="MeetMemo API",
    description="NLP-Based Conversation Intelligence & Diarization System",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Assets
os.makedirs("frontend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Register API Routers
app.include_router(text_router)
app.include_router(audio_router)
app.include_router(analysis_router)
app.include_router(mom_router)
app.include_router(qa_router)

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = "frontend/templates/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>MeetMemo API Service Running</h1>"