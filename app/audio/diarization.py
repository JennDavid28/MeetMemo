import os
import numpy as np
import librosa
from typing import List, Dict, Any
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

def run_diarization(audio_path: str, hf_token: str = None, whisper_segments: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Runs speaker diarization using pyannote.audio if available/authenticated.
    Falls back to robust acoustic voice timbre clustering on audio segments for multi-speaker detection.
    Guarantees strict chronological speaker numbering (Speaker 1 speaks first, Speaker 2 second, etc.).
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
            
            # Sort turns strictly chronologically by start time
            tracks = sorted(diarization.itertracks(yield_label=True), key=lambda x: x[0].start)
            for turn, _, speaker in tracks:
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

    # 2. Smart Fallback: Acoustic Voice Timbre Clustering
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

            # Extract 13 MFCCs mean and standard deviation
            mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
            feat = np.hstack([np.mean(mfcc, axis=1), np.std(mfcc, axis=1)])
            features.append(feat)
            valid_indices.append(idx)

        if len(features) < 2:
            return [{"speaker": "Speaker 1", "start": seg.get("start", 0.0), "end": seg.get("end", 0.0)} for seg in whisper_segments]

        # Standardize features so loudness does not bias acoustic timbre clustering
        X_raw = np.array(features)
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)

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

        # If significant clustering detected or multiple distinct turns, apply optimal k
        if best_k > 1 and best_score > 0.01:
            labels = AgglomerativeClustering(n_clusters=best_k).fit_predict(X)
        else:
            labels = [0] * len(features)

        # STRICT CHRONOLOGICAL SPEAKER MAPPING
        # Map clusters to Speaker 1, Speaker 2, ... in order of their FIRST time appearance
        sorted_indices = sorted(range(len(valid_indices)), key=lambda i: whisper_segments[valid_indices[i]].get("start", 0.0))
        cluster_to_speaker = {}
        speaker_counter = 1

        for idx in sorted_indices:
            cid = labels[idx]
            if cid not in cluster_to_speaker:
                cluster_to_speaker[cid] = f"Speaker {speaker_counter}"
                speaker_counter += 1

        result_segments = []
        for feat_idx, seg_idx in enumerate(valid_indices):
            seg = whisper_segments[seg_idx]
            assigned_speaker = cluster_to_speaker.get(labels[feat_idx], "Speaker 1")
            result_segments.append({
                "speaker": assigned_speaker,
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
        print(f"[Acoustic Diarization Warning] {err}. Defaulting to chronological Speaker 1.")
        return [{"speaker": "Speaker 1", "start": seg.get("start", 0.0), "end": seg.get("end", 0.0)} for seg in whisper_segments]