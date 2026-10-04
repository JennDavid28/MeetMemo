document.getElementById("btnAskQA").addEventListener("click", async () => {
    const question = document.getElementById("qaInput").value;
    if (!question.trim()) return alert("Please type a question.");

    if (!currentMeetingPayload) {
        return alert("Process a meeting transcript or audio recording first.");
    }

    const meetingId = currentMeetingPayload.meeting_id;
    const fullTranscript = currentMeetingPayload.transcript.full_translated_text || currentMeetingPayload.transcript.full_original_text;

    const answerContainer = document.getElementById("qaAnswerContainer");
    const answerText = document.getElementById("qaAnswerText");

    answerText.textContent = "Asking MeetMemo LLM...";
    answerContainer.classList.remove("d-none");

    try {
        const res = await fetch("/api/qa/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                meeting_id: meetingId,
                transcript_text: fullTranscript,
                question: question
            })
        });
        const data = await res.json();
        answerText.textContent = data.answer;
    } catch (err) {
        answerText.textContent = "Error getting answer: " + err.message;
    }
});