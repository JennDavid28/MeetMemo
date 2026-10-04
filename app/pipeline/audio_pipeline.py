import os
import uuid
from typing import Dict, Any
from app.audio.preprocessing import preprocess_audio
from app.audio.transcription import transcribe_audio
from app.audio.diarization import run_diarization
from app.audio.timestamps import merge_whisper_and_diarization
from app.schemas.transcript import UnifiedTranscript, Utterance
from app.pipeline.nlp_pipeline import run_nlp_pipeline
from app.nlp.language_detection import detect_language
from app.llm.mom_generator import generate_mom_llm

def run_audio_pipeline(input_audio_path: str, hf_token: str = None) -> Dict[str, Any]:
    print("\n--- [START AUDIO PIPELINE] ---")
    meeting_id = f"meet_{uuid.uuid4().hex[:8]}"
    os.makedirs("outputs/transcripts", exist_ok=True)
    processed_wav_path = f"outputs/transcripts/{meeting_id}_temp.wav"

    print("Step 1/5: Preprocessing Audio...")
    clean_audio_path = preprocess_audio(input_audio_path, processed_wav_path)

    print("Step 2/5: Transcribing Audio with Whisper...")
    whisper_result = transcribe_audio(clean_audio_path, model_name="base")
    raw_whisper_segments = whisper_result.get("segments", [])
    full_text = whisper_result.get("text", "").strip()

    print("Step 3/5: Diarizing Speakers (Multi-Speaker Detection)...")
    diarization_segments = run_diarization(clean_audio_path, hf_token=hf_token, whisper_segments=raw_whisper_segments)
    mapped_segments = merge_whisper_and_diarization(raw_whisper_segments, diarization_segments)

    # Group contiguous utterances of the same speaker
    utterances = []
    if mapped_segments:
        curr_spk = mapped_segments[0]["speaker"]
        curr_text = mapped_segments[0]["text"]
        curr_start = mapped_segments[0]["start_time"]
        curr_end = mapped_segments[0]["end_time"]

        for seg in mapped_segments[1:]:
            seg_spk = seg["speaker"]
            seg_text = seg["text"]
            seg_start = seg["start_time"]
            seg_end = seg["end_time"]

            # Merge if same speaker and pause between turns < 2.0s
            if seg_spk == curr_spk and (seg_start - curr_end) < 2.0:
                curr_text += " " + seg_text
                curr_end = seg_end
            else:
                utterances.append(Utterance(
                    speaker=curr_spk,
                    text=curr_text,
                    start_time=curr_start,
                    end_time=curr_end
                ))
                curr_spk = seg_spk
                curr_text = seg_text
                curr_start = seg_start
                curr_end = seg_end

        utterances.append(Utterance(
            speaker=curr_spk,
            text=curr_text,
            start_time=curr_start,
            end_time=curr_end
        ))
    elif full_text:
        utterances.append(Utterance(
            speaker="Speaker 1",
            text=full_text,
            start_time=0.0,
            end_time=0.0
        ))

    print(f"Constructed {len(utterances)} speaker utterances.")

    print("Step 4/5: Running Language Detection & NLP Analysis...")
    lang_info = detect_language(full_text)
    
    transcript = UnifiedTranscript(
        meeting_id=meeting_id,
        utterances=utterances,
        full_original_text=full_text,
        full_translated_text=None,
        language_info=lang_info
    )

    # Classical NLP Analysis
    nlp_results = run_nlp_pipeline(transcript)

    if hasattr(nlp_results, "__dict__"):
        entities_list = [
            {"text": getattr(e, "text", str(e)), "label": getattr(e, "label", "ENTITY")}
            for e in getattr(nlp_results, "entities", [])
        ]
        nlp_dict = {
            "entities": entities_list,
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

    entities_text = [e.get("text", "") for e in nlp_dict.get("entities", []) if isinstance(e, dict)]
    nlp_summary_str = f"Entities: {entities_text}, Keywords: {nlp_dict.get('keywords', [])}, Action Items: {nlp_dict.get('action_items', [])}"
    
    print("Step 5/5: Generating MoM with LLM...")
    
    MAX_CHUNK_SIZE = 25000
    if len(full_text) > MAX_CHUNK_SIZE:
        chunks = [full_text[i:i+MAX_CHUNK_SIZE] for i in range(0, len(full_text), MAX_CHUNK_SIZE)]
        mom_outputs = []
        for idx, chunk in enumerate(chunks):
            print(f"Generating MoM chunk {idx+1}/{len(chunks)}...")
            section_mom = generate_mom_llm(chunk, nlp_summary_str)
            mom_outputs.append(section_mom)
        raw_mom_output = "\n\n---\n\n".join(mom_outputs)
    else:
        raw_mom_output = generate_mom_llm(full_text, nlp_summary_str)

    if os.path.exists(processed_wav_path) and processed_wav_path != input_audio_path:
        try:
            os.remove(processed_wav_path)
        except Exception:
            pass

    return {
        "meeting_id": meeting_id,
        "transcript": transcript.model_dump() if hasattr(transcript, "model_dump") else transcript,
        "nlp_analysis": nlp_dict,
        "analysis": nlp_dict,
        "summary": raw_mom_output,
        "mom": raw_mom_output
    }