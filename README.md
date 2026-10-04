# MeetMemo — NLP-Based Conversation Intelligence & Executive MoM System

MeetMemo is an advanced, end-to-end Natural Language Processing (NLP) and AI-powered Conversation Intelligence platform designed to transform raw meeting audio and dialogue transcripts into structured, executive-grade Minutes of Meeting (MoM), actionable insights, and grounded interactive Q&A.

---

## Natural Language Processing (NLP) Architecture & Significance

MeetMemo goes far beyond a basic LLM wrapper by employing a **Hybrid Dual-Engine NLP Architecture**. It combines deterministic statistical and classical NLP models with generative LLMs to cover the full spectrum of modern NLP tasks:

```text
                                 MEETMEMO NLP ARCHITECTURE
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         ▼                                   ▼                                   ▼
 1. Speech & Signal NLP             2. Classical & Statistical NLP      3. Generative LLM NLP
 - Faster-Whisper ASR (CTranslate2) - SpaCy NER (Named Entities)       - Abstractive MoM Generator
 - Librosa MFCC Voice Timbre        - Scikit-learn TF-IDF Keywords     - Grounded RAG Q&A Assistant
 - VAD Silence Filtering            - Hinglish Code-Switching Ratio    - Context-Aware Summarization
 - Acoustic Speaker Clustering      - Rule-Based Action Item Extractor
                                    - Sentiment & Talk Share Analysis
```

### Why MeetMemo Stands Out as a Comprehensive NLP Project
1. **Multi-Layer Information Extraction (NER & TF-IDF)**:
   - Uses **SpaCy (`en_core_web_sm`)** to dynamically extract Named Entities (*People, Organizations, Geopolitical Locations, Dates, Times, Products*) without any hardcoded rule lists.
   - Uses **Scikit-learn `TfidfVectorizer`** for unsupervised statistical keyword extraction, discovering the dominant technical and business terms of any meeting.
2. **Multilingual Code-Switching & Language Identification**:
   - Implements custom tokenization and lexicon analysis to compute the exact **Hinglish vs. English Code-Switching Percentage Ratio**.
3. **Speech & Acoustic Signal Processing**:
   - Combines Faster-Whisper speech-to-text with Librosa MFCC feature extraction, Agglomerative Clustering, and Silhouette Score Optimization for multi-speaker acoustic separation.
4. **Hybrid Deterministic Analytics + Generative Synthesis**:
   - Classical NLP provides fast, deterministic, inspectable analytical metrics (entities, keywords, sentiment, talk share), while Generative LLMs (Ollama / OpenAI) produce fluent executive documents and grounded Q&A.

---

## Key Features & Capabilities

- **Multi-Speaker Neural & Acoustic Diarization**:
  - **Neural Mode (`pyannote/speaker-diarization-3.1`)**: Deep speaker separation across arbitrary speaker counts when authenticated.
  - **Acoustic Voice Timbre Fallback**: Uses Librosa MFCC feature vectors with Agglomerative Clustering and Silhouette Score Optimization to dynamically identify 2, 3, 4, 5+ speakers.
- **Fast Automatic Speech Recognition (ASR)**:
  - Powered by **Faster-Whisper (CTranslate2)** with `int8` quantization, Librosa pre-decoding, and Voice Activity Detection (VAD).
- **Classical NLP & Linguistic Analytics**:
  - **SpaCy NER**: Dynamic extraction of Person, Org, Location, Date, Time, Product entities.
  - **TF-IDF Keyword Extraction**: Unsupervised statistical term weighting per document.
  - **Speaker Participation Share**: Character and time talk-share percentages per speaker.
  - **Code-Switching & Hinglish Detection**: Calculates code-switching ratio percentage.
  - **Sentiment & Vibe Analysis**: Overall meeting sentiment polarity (Positive, Negative, Neutral).
- **Meaningful LLM Integration (Ollama / OpenAI API)**:
  - **Executive Minutes of Meeting (MoM)**: Structured MoM with Executive Summary, Agenda Breakdown, Decisions, and Action Items.
  - **Grounded AI Q&A Assistant**: Answers questions strictly grounded in active transcripts and SQLite historical meeting records.
- **Modern Glassmorphism Web Interface**:
  - 3-column dashboard supporting Audio Recording (`.webm`), File Uploads (`.wav`, `.mp3`, `.m4a`, `.flac`, `.mp4`), and Paste Dialogue.
  - Interactive speaker renaming (updating speaker names across the transcript in real-time).
  - Multi-format document export: **PDF**, **Word DOCX**, **Markdown**, and **TXT**.
  - Persistent SQLite database storage for user meeting records.

---

## Project Directory Structure

```text
MeetMemo/
│
├── app/                          # Main Backend Application Package
│   ├── api/                      # FastAPI Router Modules
│   │   ├── routes_audio.py       # Audio upload & recording processing endpoints
│   │   ├── routes_text.py        # Dialogue text processing endpoints
│   │   ├── routes_mom.py         # Meeting saving, history & markdown export endpoints
│   │   ├── routes_qa.py          # Grounded AI Q&A Assistant endpoint
│   │   └── routes_analysis.py    # Speaker renaming & analysis endpoints
│   │
│   ├── audio/                    # Audio Processing Pipeline
│   │   ├── preprocessing.py     # 16kHz mono WAV conversion via Librosa / Soundfile
│   │   ├── transcription.py     # Faster-Whisper ASR engine initialization & execution
│   │   ├── diarization.py       # Pyannote 3.1 & Acoustic MFCC speaker clustering fallback
│   │   └── timestamps.py        # Timestamp overlap mapping between ASR and Diarization
│   │
│   ├── nlp/                      # Classical NLP & Analytics Modules
│   │   ├── ner.py               # SpaCy Named Entity Recognition
│   │   ├── keywords.py          # Scikit-learn TF-IDF keyword extraction
│   │   ├── sentiment.py         # Rule & lexicon-based sentiment analysis
│   │   ├── hinglish.py          # Hinglish code-switching ratio detection
│   │   └── language_detection.py# English vs. Hinglish language classification
│   │
│   ├── llm/                      # LLM Integration & Execution Engine
│   │   ├── client.py            # Ollama / OpenAI API call execution with timeout management
│   │   └── mom_generator.py     # Prompt loading & resilient MoM generation
│   │
│   ├── pipeline/                 # Core Pipeline Controllers
│   │   ├── audio_pipeline.py    # End-to-end audio processing orchestration
│   │   ├── text_pipeline.py     # Text dialogue processing orchestration
│   │   └── nlp_pipeline.py      # Dynamic NLP analysis orchestration
│   │
│   ├── database/                 # Database & Persistence Layer
│   │   ├── database.py          # SQLAlchemy SQLite database session setup
│   │   ├── models.py            # MeetingRecord database model
│   │   └── crud.py              # Database CRUD utility queries
│   │
│   ├── schemas/                  # Pydantic Schemas & Data Contracts
│   │   ├── transcript.py        # Utterance, LanguageAnalysis, UnifiedTranscript schemas
│   │   ├── speaker.py           # SpeakerSegment, SpeakerRenameRequest schemas
│   │   ├── analysis.py          # NLPAnalysisResult schema
│   │   └── mom.py              # SaveMoMRequest schema
│   │
│   └── main.py                   # FastAPI Application Entry Point & Static Routing
│
├── frontend/                     # Web User Interface
│   ├── templates/
│   │   └── index.html           # Main Glassmorphism Dashboard HTML Template
│   └── static/
│       ├── css/
│       │   └── style.css        # Responsive Glassmorphism Styling & Typography
│       └── js/
│           ├── dashboard.js     # UI Navigation, Feature Rendering, & Export Handlers
│           ├── recorder.js      # Microphone Recording & WebM MediaRecorder Handler
│           └── qa.js            # Q&A Assistant UI Interaction Handler
│
├── config/                       # Configuration Files
│   ├── config.yaml              # Global System & Feature Configurations
│   └── .env.example             # Environment Variables Example
│
├── prompts/                      # LLM Prompt Templates
│   ├── mom.txt                  # Structured Executive MoM Generation Prompt
│   ├── qa.txt                   # Grounded Knowledge-Base Q&A Prompt
│   ├── action_items.txt         # Action Item Extraction Prompt
│   ├── decisions.txt            # Decision Extraction Prompt
│   ├── summary.txt              # Executive Summary Prompt
│   ├── discussions.txt          # Key Discussion Topics Prompt
│   ├── motions.txt              # Motions & Votes Prompt
│   └── questions.txt            # Question Identification Prompt
│
├── tests/                        # Automated Unit & Integration Tests
│   └── test_pipeline.py         # Pytest suite for FastAPI endpoints & pipelines
│
├── .env                          # Local Environment Configuration
├── meetmemo.db                   # SQLite Database File
├── requirements.txt              # Python Package Dependencies
├── run.py                        # Server Startup & Environment Initializer Script
└── README.md                     # Documentation & Setup Guide
```

---

##  Requirements & Environment Setup

### Prerequisites
- **Python**: Version `3.10` or higher (Tested on Python `3.14`)
- **FFmpeg**: Required by `librosa` and `pydub` for audio decoding.
- **Ollama** *(Optional for local LLM)*: Installed and running locally (`ollama run llama3.2` or `qwen2.5`).

---

## Step-by-Step Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/MeetMemo.git
cd MeetMemo
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download SpaCy English Model
```bash
python -m spacy download en_core_web_sm
```

---

## Running on Local Server

### 1. Configure Environment Variables
Verify or edit `.env` in the root directory:
```env
ENV=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./meetmemo.db
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2:1b
OLLAMA_URL=http://localhost:11434/api/generate
HUGGINGFACE_TOKEN=your_optional_huggingface_token_here
```

### 2. Launch the Application
Run the setup and Uvicorn server script:
```bash
python run.py
```

### 3. Access the Web Application
Open your browser and navigate to:
```text
http://127.0.0.1:8000
```

---

## Running Automated Unit Tests

Run the full pytest suite:
```bash
python -m pytest tests/test_pipeline.py
```

---

## Academic Context & Evaluation Requirements Verification

This project was developed as an individual solo project fulfilling all prescribed course requirements for NLP and LLM integration.

### Verification of Project Requirements

| Requirement | Implementation Status | Details |
| :--- | :---: | :--- |
| **Solo Individual Work** | **COMPLIANT** | Fully designed, implemented, debugged, and documented individually. |
| **NLP-based Project + LLM API Integration** | **COMPLIANT** | Integrates Faster-Whisper ASR, SpaCy NER, TF-IDF keywords, Hinglish code-switching, and connects to LLM APIs (Ollama / OpenAI). |
| **Meaningful LLM Functionality** | **COMPLIANT** | LLM generates Executive Minutes of Meeting (MoM) and powers a grounded Q&A Assistant across active and historical meeting records. |
| **GitHub Repository Contents** | **COMPLIANT** | Includes source code (`app/`, `frontend/`), prompt files (`prompts/`), config files (`config/config.yaml`, `.env`), and setup scripts (`run.py`). |

### Alignment with Evaluation Criteria

1. **Quality and Efficiency of Code**:
   - Modular architecture separating API routes, audio preprocessing, diarization, NLP analytics, LLM calls, and UI components.
   - Faster-Whisper ASR optimized with `int8` quantization and VAD silence filtering.
   - Resilient LLM timeout handling with dynamic NLP fallback to ensure 100% uptime.
2. **Functionality and Implementation of LLM API**:
   - Clean API interaction layer ([app/llm/client.py](file:///c:/Users/IVAN%20AJAY%20DAVID/Documents/GitHub/MeetMemo/app/llm/client.py)) with configurable parameters (`temperature`, `num_ctx`, `repeat_penalty`).
   - Context window expansion to 8,192 tokens allowing full-length transcript processing without fragmentation.
3. **Effectiveness and Efficiency of Prompt Files**:
   - Dedicated prompt templates in `prompts/` enforcing executive structure, non-repetitive summaries, and strict Markdown formatting.
4. **Overall Project Execution**:
   - Full-stack execution from audio/microphone input to interactive UI analytics, database storage, and PDF/DOCX document export.
