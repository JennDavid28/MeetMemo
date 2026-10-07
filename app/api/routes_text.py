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
    parsed_lines = []
    
    # Check if lines have explicit speaker labels
    has_any_speaker_prefix = False
    for line in lines:
        clean = re.sub(r'^[\[\(]?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?[\]\)]?[\s\-:]*', '', line).strip()
        m = re.match(r'^([^:\-\n]{1,40})[:\-]\s*(.*)$', clean)
        if m and len(m.group(1).split()) <= 4:
            has_any_speaker_prefix = True
            parsed_lines.append((m.group(1).strip(), m.group(2).strip()))
        else:
            parsed_lines.append((None, clean))

    # If no speaker labels detected at all, detect conversational turns across paragraphs/lines
    if not has_any_speaker_prefix:
        utterances_data = []
        turn_counter = 1
        for i, (_, text) in enumerate(parsed_lines):
            spk = f"Speaker {(i % 2) + 1}"  # Alternate Speaker 1 and Speaker 2 for dialogue turns
            utterances_data.append((spk, text))
    else:
        # Fill forward current speaker when lines are continuation of dialogue
        utterances_data = []
        curr_spk = "Speaker 1"
        for spk, text in parsed_lines:
            if spk is not None:
                curr_spk = spk
            utterances_data.append((curr_spk, text))

    # If generic Speaker labels (e.g. "Speaker 2", "Speaker 1") are used out of order,
    # normalize them in strict chronological order of first appearance
    all_generic = all(re.match(r'^Speaker\s+\d+$', spk, re.IGNORECASE) for spk, _ in utterances_data)
    if all_generic:
        speaker_map = {}
        counter = 1
        normalized_data = []
        for spk, text in utterances_data:
            if spk not in speaker_map:
                speaker_map[spk] = f"Speaker {counter}"
                counter += 1
            normalized_data.append((speaker_map[spk], text))
        utterances_data = normalized_data

    utterances = []
    for i, (speaker, text) in enumerate(utterances_data):
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