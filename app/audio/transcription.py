import os
import librosa
import numpy as np
from faster_whisper import WhisperModel

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        print("[INFO] Initializing CTranslate2 Whisper Engine (base, int8)...")
        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8",
            cpu_threads=4,
            download_root="models/whisper"
        )
    return _model

def transcribe_audio(audio_path: str, model_name: str = "base") -> dict:
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")

    model = get_whisper_model()

    # Pre-decode to 16kHz float32 mono (bypasses PyAV metadata_errors incompatibility)
    try:
        audio_data, _ = librosa.load(audio_path, sr=16000, mono=True)
        input_data = audio_data.astype(np.float32)
    except Exception as err:
        print(f"[Warning] Librosa pre-decode fallback: {err}")
        input_data = audio_path

    # Transcribe audio file with robust VAD padding to ensure the full recording is transcribed
    segments_generator, info = model.transcribe(
        input_data,
        language="en",
        beam_size=1,
        best_of=1,
        vad_filter=True,
        vad_parameters=dict(
            min_silence_duration_ms=1500,
            speech_pad_ms=300
        )
    )

    segments = list(segments_generator)

    raw_segments = []
    text_chunks = []

    for seg in segments:
        text_clean = seg.text.strip()
        if text_clean:
            text_chunks.append(text_clean)
            raw_segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": text_clean
            })

    full_text = " ".join(text_chunks)

    return {
        "text": full_text,
        "segments": raw_segments,
        "language": info.language,
        "language_probability": round(info.language_probability, 2)
    }