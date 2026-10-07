import pytest
from app.nlp.hinglish import detect_hinglish_ratio
from app.nlp.language_detection import detect_language
from app.pipeline.nlp_pipeline import run_nlp_pipeline
from app.pipeline.text_pipeline import parse_pasted_text_to_utterances
from app.llm.mom_generator import generate_fallback_mom

SAMPLE_ENGLISH_CONVERSATION = """Riya: Good morning everyone. Let's start the project review. Today I want to discuss the current progress of DocIntellect, the issues we are facing, and what we need to complete before the final demo.

Arjun: Good morning. From the backend side, authentication and document upload are working. Users can register, log in, create folders, and upload PDF and text files. The RAG API is also connected with Elasticsearch.

Neha: On the ML side, the document chunking and embedding pipeline is working. We are currently using the all-MiniLM-L6-v2 model for embeddings. The retrieval results are generally good, but sometimes the system retrieves similar but irrelevant chunks.

Riya: How frequently is that happening?

Neha: Around 10 to 15 percent of the test questions. It is more noticeable when the document contains similar terminology across multiple sections.

Arjun: I think we can improve that by adding metadata filtering before the vector search. We can filter based on the user, folder, and document ID.

Neha: Yes, that should help. I also want to experiment with increasing the top-k retrieval from 3 to 5 and then reranking the retrieved chunks.

Karan: From the frontend side, the main dashboard is almost complete. The recording interface is working, and users can upload audio or paste a conversation. I am still working on the loading state while the audio is being processed.

Priya: I tested the upload flow yesterday. PDF uploads are working, but I found an issue when the user uploads a very large file. The interface does not show any progress, so it looks like the application has stopped responding.

Karan: I can add an upload progress indicator and a processing status message.

Riya: Good. What about the transcript?

Neha: The transcript generation is working for clear audio. However, when two people speak at the same time, the speaker labels are sometimes incorrect.

Priya: I also noticed that punctuation is missing in some transcripts. That makes the summary less readable.

Riya: Can we fix that before the final demo?

Neha: Yes. I can add a post-processing step for punctuation and improve speaker segmentation. I should have an improved version by Wednesday.

Arjun: I also found another issue. The API sometimes takes more than 15 seconds when processing a large document because the complete document is being processed synchronously.

Riya: Can we make that asynchronous?

Arjun: Yes. I can move the document processing to a background task so the user does not have to wait on the upload screen.

Riya: Good. Please prioritize that.

Karan: I have one UI suggestion. After the recording is saved, we currently show only the audio file. I think we should immediately show three options: Play Recording, Process Recording, and Delete.

Riya: I agree. Also, once processing is complete, the user should be able to open Transcript, NLP Analysis, Summary, and Minutes of Meeting directly from the left navigation.

Priya: For testing, I will prepare 20 questions based on different meeting transcripts. We should check whether the AI gives answers only from the uploaded meeting and does not invent information.

Neha: That's important. We should also display citations or the relevant transcript section whenever possible.

Riya: Yes. The main goal is grounded answers. If the answer is not present in the meeting, the assistant should clearly say that the information was not found instead of guessing.

Arjun: For the final demo, I suggest we use one complete meeting recording instead of multiple short recordings.

Karan: Agreed. I can prepare the recording interface for that.

Riya: Let's finalize the responsibilities. Arjun will handle asynchronous document processing and metadata filtering. Neha will improve retrieval, reranking, punctuation, and speaker segmentation. Karan will finish the recording UI, upload progress, and processing states. Priya will prepare the test cases and validate the AI answers.

Priya: What is the deadline for all of this?

Riya: Wednesday evening. On Thursday morning, we will run the complete test and fix any critical issues. The final demo will be on Friday at 3 PM.

Arjun: Sounds good.

Neha: Works for me.

Karan: Same here.

Priya: I'll have the test cases ready by Wednesday afternoon.

Riya: Great. Before we close, is there anything else?

Karan: One small thing. Should we add a meeting title automatically based on the transcript?

Riya: Yes, but keep it editable. The AI can suggest a title, but the user should be able to change it.

Neha: We could also automatically extract action items and deadlines into a separate section.

Riya: Definitely. That should be part of the Minutes of Meeting.

Priya: Then I think we're good.

Riya: Perfect. Thanks everyone. Let's meet Thursday morning for the final testing session."""

def test_hinglish_ratio_english_text():
    ratio = detect_hinglish_ratio(SAMPLE_ENGLISH_CONVERSATION)
    assert ratio == 0.0, f"Expected 0.0% Hinglish ratio for pure English text, got {ratio}%"

def test_language_detection_english():
    lang = detect_language(SAMPLE_ENGLISH_CONVERSATION)
    assert lang.detected_language == "English"
    assert lang.hindi_ratio == 0.0
    assert lang.code_switching is False

def test_hinglish_ratio_with_actual_hinglish():
    text = "Haan team kal hum sab milkar meeting karenge aur final demo ready karenge."
    ratio = detect_hinglish_ratio(text)
    assert ratio > 0.0
    lang = detect_language(text)
    assert lang.detected_language == "Hinglish"
    assert lang.code_switching is True

def test_chronological_speaker_normalization():
    # Transcript with out-of-order generic speaker labels
    raw = """Speaker 2: Good morning team.
Speaker 1: Hi, what are the updates?
Speaker 2: Everything is on track."""
    utterances = parse_pasted_text_to_utterances(raw)
    assert utterances[0].speaker == "Speaker 1"
    assert utterances[1].speaker == "Speaker 2"
    assert utterances[2].speaker == "Speaker 1"

def test_multi_speaker_turn_detection_no_labels():
    raw = """Welcome to the sprint sync.
Thanks, I completed the backend tasks.
I will review the PRs this afternoon."""
    utterances = parse_pasted_text_to_utterances(raw)
    assert len(utterances) == 3
    # Multiple speakers must be detected
    unique_speakers = set(u.speaker for u in utterances)
    assert len(unique_speakers) >= 2
    assert utterances[0].speaker == "Speaker 1"
    assert utterances[1].speaker == "Speaker 2"

def test_action_item_extraction_cleanliness():
    class DummyTranscript:
        full_original_text = SAMPLE_ENGLISH_CONVERSATION
        utterances = parse_pasted_text_to_utterances(SAMPLE_ENGLISH_CONVERSATION)

    results = run_nlp_pipeline(DummyTranscript())
    assert results.hinglish_ratio == 0.0
    # Ensure action items do not include introductory greetings
    for item in results.action_items:
        assert not item.lower().startswith("riya: good morning everyone")
        assert not item.lower().startswith("arjun: good morning")

def test_authentic_mom_generation():
    mom = generate_fallback_mom(SAMPLE_ENGLISH_CONVERSATION)
    assert "docintellect" in mom.lower()
    assert "Riya" in mom and "Arjun" in mom and "Neha" in mom and "Karan" in mom and "Priya" in mom
    assert "Wednesday" in mom or "Friday" in mom
    # Ensure no hardcoded workshop/blog/apprentice artifacts
    assert "Inclusive Leadership" not in mom
    assert "Assertiveness" not in mom
    assert "Excel Introduction" not in mom
    assert "blog posts" not in mom
    assert "charity committee" not in mom
