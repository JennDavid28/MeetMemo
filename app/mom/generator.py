from app.schemas.transcript import UnifiedTranscript
from app.schemas.analysis import NLPAnalysisResult
from app.schemas.mom import MinutesOfMeeting
from app.mom.meeting_details import create_default_details
from app.mom.attendance import extract_attendance
from app.llm.mom_generator import generate_mom_llm

def build_full_mom_package(transcript: UnifiedTranscript, nlp_result: NLPAnalysisResult) -> dict:
    attendance_list = extract_attendance(transcript.utterances)
    details = create_default_details()

    nlp_summary_str = f"Entities: {[e.text for e in nlp_result.entities]}, Keywords: {nlp_result.keywords}, Sentiment: {nlp_result.sentiment.overall}"
    
    mom_text = generate_mom_llm(
        transcript.full_translated_text or transcript.full_original_text,
        nlp_summary_str
    )

    return {
        "details": details.model_dump(),
        "attendance": attendance_list,
        "raw_mom_markdown": mom_text
    }