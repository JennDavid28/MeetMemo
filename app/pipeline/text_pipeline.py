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
    Parses lines in format 'Speaker 1: Hello' or '[00:15] Speaker 1: Hello' into structured Utterance models.
    Guarantees chronological speaker order and detects conversational turns when no speaker labels exist.
    """
    import re
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    if not lines:
        return []

    parsed_lines = []
    has_any_prefix = False

    for line in lines:
        clean = re.sub(r'^[\[\(]?\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?[\]\)]?[\s\-:]*', '', line).strip()
        m = re.match(r'^([^:\-\n]{1,40})[:\-]\s*(.*)$', clean)
        if m and len(m.group(1).split()) <= 4:
            has_any_prefix = True
            parsed_lines.append((m.group(1).strip(), m.group(2).strip()))
        else:
            parsed_lines.append((None, clean))

    if not has_any_prefix:
        utterances_data = [(f"Speaker {(i % 2) + 1}", text) for i, (_, text) in enumerate(parsed_lines)]
    else:
        utterances_data = []
        curr = "Speaker 1"
        for spk, text in parsed_lines:
            if spk is not None:
                curr = spk
            utterances_data.append((curr, text))

    # If generic Speaker labels out of order, normalize chronologically
    if all(re.match(r'^Speaker\s+\d+$', spk, re.IGNORECASE) for spk, _ in utterances_data):
        spk_map = {}
        cnt = 1
        normalized = []
        for spk, text in utterances_data:
            if spk not in spk_map:
                spk_map[spk] = f"Speaker {cnt}"
                cnt += 1
            normalized.append((spk_map[spk], text))
        utterances_data = normalized

    return [Utterance(speaker=spk, text=txt) for spk, txt in utterances_data]

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