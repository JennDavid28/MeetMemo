document.addEventListener("DOMContentLoaded", () => {
    let mediaRecorder = null;
    let audioChunks = [];
    let recordedBlob = null;
    let timerInterval = null;
    let secondsRecorded = 0;

    const micButton = document.getElementById("micCircleBtn");
    const recordStatusTitle = document.getElementById("recordStatusTitle");
    const recordStatusSubtitle = document.getElementById("recordStatusSubtitle");
    const recordTimer = document.getElementById("recordTimer");
    const recentRecordingDock = document.getElementById("recentRecordingDock");
    const audioPreview = document.getElementById("audioPreview");
    const btnProcessRecord = document.getElementById("btnProcessRecord");

    if (!micButton) return;

    micButton.addEventListener("click", async () => {
        // Stop Recording
        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
            if (mediaRecorder.stream) {
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
            }
            clearInterval(timerInterval);

            micButton.classList.remove("recording");
            if (recordStatusTitle) recordStatusTitle.textContent = "Recording Captured!";
            if (recordStatusSubtitle) recordStatusSubtitle.textContent = "Listen to preview below and click Process Recording.";

            return;
        }

        // Start Recording
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/webm' };
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                options = { mimeType: 'audio/mp4' };
            }

            mediaRecorder = new MediaRecorder(stream, options);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) audioChunks.push(event.data);
            };

            mediaRecorder.onstop = () => {
                const mimeType = mediaRecorder.mimeType || 'audio/webm';
                recordedBlob = new Blob(audioChunks, { type: mimeType });

                const audioUrl = URL.createObjectURL(recordedBlob);
                if (audioPreview) audioPreview.src = audioUrl;

                const activePane = document.querySelector('.sidebar-nav-btn.active');
                if (activePane && activePane.getAttribute('data-pane') === 'pane-record') {
                    if (recentRecordingDock) recentRecordingDock.classList.remove("d-none");
                }
            };

            mediaRecorder.start(1000);
            micButton.classList.add("recording");

            if (recordStatusTitle) recordStatusTitle.textContent = "Listening...";
            if (recordStatusSubtitle) recordStatusSubtitle.textContent = "Click microphone again to stop recording.";

            secondsRecorded = 0;
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                secondsRecorded++;
                const mins = String(Math.floor(secondsRecorded / 60)).padStart(2, '0');
                const secs = String(secondsRecorded % 60).padStart(2, '0');
                if (recordTimer) recordTimer.textContent = `Recording: ${mins}:${secs}`;
            }, 1000);

        } catch (err) {
            alert("Microphone Error: " + err.message);
        }
    });

    if (btnProcessRecord) {
        btnProcessRecord.addEventListener("click", async () => {
            if (!recordedBlob) return alert("Please record audio first.");

            const formData = new FormData();
            formData.append("file", recordedBlob, "recording.webm");

            btnProcessRecord.disabled = true;
            btnProcessRecord.textContent = "Processing...";

            try {
                const res = await fetch("/api/audio/record", { method: "POST", body: formData });
                if (!res.ok) throw new Error("Server error " + res.status);
                
                const data = await res.json();
                window.currentPayload = data;

                const momBtn = document.querySelector('[data-feature="mom"]');
                if (momBtn) momBtn.click();

            } catch (err) {
                alert("Audio Processing Error: " + err.message);
            } finally {
                btnProcessRecord.disabled = false;
                btnProcessRecord.textContent = "Process Recording";
            }
        });
    }
});