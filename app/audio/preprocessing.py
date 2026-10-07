import os
import subprocess
from pathlib import Path

def preprocess_audio(input_file_path: str, output_wav_path: str) -> str:
    """
    Converts input audio/video to 16kHz mono WAV format for Whisper and pyannote.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_file_path,
        "-ac", "1", "-ar", "16000",
        output_wav_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_wav_path