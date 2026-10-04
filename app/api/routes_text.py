import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.llm.mom_generator import generate_mom_llm
from app.pipeline.nlp_pipeline import run_nlp_pipeline

router = APIRouter(prefix="/api/text", tags=["Text Processing"])

class TextProcessRequest(BaseModel):
    raw_text: str

@router.post("/process-paste")
async def process_pasted_text(payload: TextProcessRequest):
    raw_text = payload.raw_text.strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")

    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    utterances = []
    
    current_speaker = "Speaker 1"
    
    for i, line in enumerate(lines):
        # 1. Check if line starts with an explicit speaker label (e.g. "Morgan:", "Alice -", "Speaker 2:")
        match = re.match(r'^([^:\-\n]+)[:\-]\s*(.*)$', line)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            current_speaker = speaker
        else:
            # If no colon prefix, keep current speaker unless line represents a whole new paragraph
            speaker = current_speaker
            text = line
            
        utterances.append({
            "speaker": speaker, 
            "text": text,
            "start_time": float(i * 10),
            "end_time": float((i + 1) * 10)
        })

    transcript_dict = {
        "full_original_text": raw_text,
        "utterances": utterances
    }

    # Pass structured object to NLP pipeline to accurately derive participation
    class TemporaryTranscript:
        def __init__(self, full_text, utterances_list):
            self.full_original_text = full_text
            self.utterances = [
                type('Utterance', (), u)() for u in utterances_list
            ]

    temp_obj = TemporaryTranscript(raw_text, utterances)
    nlp_results = run_nlp_pipeline(temp_obj)

    if hasattr(nlp_results, "__dict__"):
        nlp_dict = {
            "entities": [{"text": getattr(e, "text", str(e)), "label": getattr(e, "label", "ENTITY")} for e in getattr(nlp_results, "entities", [])],
            "keywords": getattr(nlp_results, "keywords", []),
            "action_items": getattr(nlp_results, "action_items", []),
            "sentiment": getattr(nlp_results, "sentiment", {"vibe": "Professional / Neutral"}),
            "participation": getattr(nlp_results, "participation", []),
            "hinglish_ratio": getattr(nlp_results, "hinglish_ratio", 0.0)
        }
    elif isinstance(nlp_results, dict):
        nlp_dict = nlp_results
    else:
        nlp_dict = {}

    nlp_summary_str = f"Keywords: {nlp_dict.get('keywords', [])}, Action Items: {nlp_dict.get('action_items', [])}"
    mom_output = generate_mom_llm(raw_text, nlp_summary_str)

    return {
        "transcript": transcript_dict,
        "nlp_analysis": nlp_dict,
        "analysis": nlp_dict,
        "summary": mom_output,
        "mom": mom_output
    }