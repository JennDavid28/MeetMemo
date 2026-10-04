from typing import List, Dict, Any

def merge_whisper_and_diarization(whisper_segments: List[Dict[str, Any]], diarization_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Maps Whisper transcript segments to diarized speakers based on timestamp overlap.
    """
    if not whisper_segments:
        return []

    if not diarization_segments:
        return [
            {
                "speaker": "Speaker 1",
                "text": seg.get("text", "").strip(),
                "start_time": round(seg.get("start", 0.0), 2),
                "end_time": round(seg.get("end", 0.0), 2)
            }
            for seg in whisper_segments if seg.get("text", "").strip()
        ]

    result = []
    
    for seg in whisper_segments:
        seg_start = seg.get("start", 0.0)
        seg_end = seg.get("end", 0.0)
        text = seg.get("text", "").strip()
        if not text:
            continue

        assigned_speaker = None
        max_overlap = -1.0

        for d_seg in diarization_segments:
            d_start = d_seg.get("start", 0.0)
            d_end = d_seg.get("end", 0.0)
            overlap = max(0.0, min(seg_end, d_end) - max(seg_start, d_start))
            if overlap > max_overlap:
                max_overlap = overlap
                assigned_speaker = d_seg.get("speaker")

        if not assigned_speaker or max_overlap <= 0:
            # Fallback: find nearest diarized segment by time center
            seg_center = (seg_start + seg_end) / 2.0
            min_dist = float("inf")
            for d_seg in diarization_segments:
                d_center = (d_seg.get("start", 0.0) + d_seg.get("end", 0.0)) / 2.0
                dist = abs(seg_center - d_center)
                if dist < min_dist:
                    min_dist = dist
                    assigned_speaker = d_seg.get("speaker")

        if not assigned_speaker:
            assigned_speaker = "Speaker 1"

        result.append({
            "speaker": assigned_speaker,
            "text": text,
            "start_time": round(seg_start, 2),
            "end_time": round(seg_end, 2)
        })

    return result