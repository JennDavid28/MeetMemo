import uuid
from typing import Dict, Any, List
from app.schemas.transcript import UnifiedTranscript, Utterance, LanguageAnalysis
from app.schemas.analysis import NLPAnalysisResult
from app.schemas.mom import MinutesOfMeeting
from app.pipeline.nlp_pipeline import run_nlp_pipeline
from app.nlp.language_detection import detect_language
from app.llm.client import call_llm
from app.llm.mom_generator import generate_mom_llm

def parse_pasted_text_to_utterances(raw_text: str) -> List[Utterance]:
    """
    Parses lines in format 'Speaker 1: Hello' into structured Utterance models.
    """
    utterances = []
    lines = raw_text.strip().split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            parts = line.split(":", 1)
            speaker = parts[0].strip()
            text = parts[1].strip()
        else:
            speaker = "Speaker 1"
            text = line
            
        utterances.append(Utterance(speaker=speaker, text=text))
    return utterances

def run_text_pipeline(raw_text: str, meeting_id: str = None) -> Dict[str, Any]:
    """
    End-to-end pipeline for text inputs.
    """
    meeting_id = meeting_id or f"meet_{uuid.uuid4().hex[:8]}"

    # 1. Structure Utterances
    utterances = parse_pasted_text_to_utterances(raw_text)

    # 2. Language Detection
    lang_info = detect_language(raw_text)

    # 3. Handle Hinglish Translation via LLM if code-switching detected
    translated_text = None
    if lang_info.code_switching or lang_info.detected_language == "Hinglish":
        translation_prompt = f"Translate the following Hinglish conversation into clear English while preserving original meanings and speaker intent:\n\n{raw_text}"
        translated_text = call_llm(translation_prompt, temperature=0.1)

    # 4. Construct Unified Transcript Schema
    transcript = UnifiedTranscript(
        meeting_id=meeting_id,
        utterances=utterances,
        full_original_text=raw_text,
        full_translated_text=translated_text,
        language_info=lang_info
    )

    # 5. Run Classical NLP Analysis
    nlp_results = run_nlp_pipeline(transcript)

    # 6. Generate Formal Minutes of Meeting (MoM) via LLM
    nlp_summary_str = f"Entities: {[e.text for e in nlp_results.entities]}, Keywords: {nlp_results.keywords}"
    raw_mom_output = generate_mom_llm(translated_text or raw_text, nlp_summary_str)

    return {
        "meeting_id": meeting_id,
        "transcript": transcript,
        "nlp_analysis": nlp_results,
        "mom": raw_mom_output
    }