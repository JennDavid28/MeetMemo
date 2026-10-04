import re
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def segment_sentences(text: str) -> list[str]:
    if nlp:
        doc = nlp(text)
        return [sent.text.strip() for sent in doc.sents]
    return [s.strip() for s in text.split('.') if s.strip()]

import os
import subprocess

def preprocess_audio(input_file_path: str, output_wav_path: str) -> str:
    """
    Converts input audio/video to 16kHz mono WAV format for Whisper and pyannote.
    Falls back to original file if ffmpeg is not present.
    """
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_file_path,
            "-ac", "1", "-ar", "16000",
            "-af", "loudnorm",
            output_wav_path
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return output_wav_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"[Audio Preprocessing Warning] FFmpeg error/missing ({e}). Using original file.")
        return input_file_path