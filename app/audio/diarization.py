import os
import numpy as np
import librosa
from typing import List, Dict, Any
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

def run_diarization(audio_path: str, hf_token: str = None, whisper_segments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Runs speaker diarization using pyannote.audio if available/authenticated.
    Falls back to MFCC feature clustering on audio segments for fast multi-speaker detection.
    """
    token = hf_token or os.getenv("HUGGINGFACE_TOKEN")
    
    # 1. Attempt Pyannote.audio if valid token provided
    if token and token.strip() and not token.startswith("your_huggingface_token"):
        try:
            from pyannote.audio import Pipeline
            print("[INFO] Running Neural Speaker Diarization with pyannote.audio...")
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
            diarization = pipeline(audio_path)
            
            segments = []
            speaker_map = {}
            speaker_count = 1
            
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                if speaker not in speaker_map:
                    speaker_map[speaker] = f"Speaker {speaker_count}"
                    speaker_count += 1
                clean_speaker = speaker_map[speaker]
                
                segments.append({
                    "speaker": clean_speaker,
                    "start": turn.start,
                    "end": turn.end
                })
            if segments:
                return segments
        except Exception as e:
            print(f"[Notice] Pyannote Diarization Warning: {e}. Falling back to acoustic feature clustering.")

    # 2. Smart Fallback: Acoustic Voice Timbre (MFCC) Clustering
    print("[INFO] Running Acoustic Voice Timbre Diarization (Multi-Speaker Detection)...")
    if whisper_segments:
        return run_acoustic_diarization(audio_path, whisper_segments)
    else:
        try:
            duration = librosa.get_duration(path=audio_path)
            dummy_segs = [{"start": float(i), "end": min(float(i + 4.0), duration), "text": ""} for i in range(0, int(duration), 4)]
            return run_acoustic_diarization(audio_path, dummy_segs)
        except Exception:
            return [{"speaker": "Speaker 1", "start": 0.0, "end": 60.0}]


def run_acoustic_diarization(audio_path: str, whisper_segments: List[Dict[str, Any]], max_speakers: int = 6) -> List[Dict[str, Any]]:
    if not whisper_segments:
        return [{"speaker": "Speaker 1", "start": 0.0, "end": 60.0}]

    try:
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        features = []
        valid_indices = []

        for idx, seg in enumerate(whisper_segments):
            start_sec = seg.get("start", 0.0)
            end_sec = seg.get("end", 0.0)
            start_sample = max(0, int(start_sec * sr))
            end_sample = min(len(y), int(end_sec * sr))
            chunk = y[start_sample:end_sample]

            if len(chunk) < 1600:  # less than 0.1s audio
                continue

            mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            feat = np.hstack([np.mean(mfcc, axis=1), np.std(mfcc, axis=1)])
            features.append(feat)
            valid_indices.append(idx)

        if len(features) < 2:
            return [{"speaker": "Speaker 1", "start": seg.get("start", 0.0), "end": seg.get("end", 0.0)} for seg in whisper_segments]

        X = np.array(features)
        best_k = 1
        best_score = -1.0

        upper_k = min(max_speakers + 1, len(features))
        for k in range(2, upper_k):
            clustering = AgglomerativeClustering(n_clusters=k).fit(X)
            if len(set(clustering.labels_)) > 1:
                score = silhouette_score(X, clustering.labels_)
                if score > best_score:
                    best_score = score
                    best_k = k

        if best_k > 1 and best_score > 0.02:
            labels = AgglomerativeClustering(n_clusters=best_k).fit_predict(X)
        else:
            labels = [0] * len(features)

        result_segments = []
        for feat_idx, seg_idx in enumerate(valid_indices):
            seg = whisper_segments[seg_idx]
            spk_num = labels[feat_idx] + 1
            result_segments.append({
                "speaker": f"Speaker {spk_num}",
                "start": seg.get("start", 0.0),
                "end": seg.get("end", 0.0)
            })

        for seg in whisper_segments:
            if not any(r["start"] == seg.get("start") and r["end"] == seg.get("end") for r in result_segments):
                result_segments.append({
                    "speaker": "Speaker 1",
                    "start": seg.get("start", 0.0),
                    "end": seg.get("end", 0.0)
                })

        result_segments.sort(key=lambda x: x["start"])
        return result_segments

    except Exception as err:
        print(f"[Acoustic Diarization Warning] {err}. Defaulting to Speaker 1.")
        return [{"speaker": "Speaker 1", "start": seg.get("start", 0.0), "end": seg.get("end", 0.0)} for seg in whisper_segments]