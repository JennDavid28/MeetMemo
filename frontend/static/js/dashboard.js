window.currentUser = null;
window.currentPayload = null;

// HELPER: FORMAT SECONDS TO MM:SS
function formatTime(seconds) {
    if (seconds === undefined || seconds === null) return "00:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

document.addEventListener("DOMContentLoaded", () => {

    function hideAllPanes() {
        document.querySelectorAll(".stage-pane").forEach(p => p.classList.add("d-none"));
    }

    function showDefaultPane() {
        hideAllPanes();
        const recordPane = document.getElementById("pane-record");
        if (recordPane) recordPane.classList.remove("d-none");

        document.querySelectorAll(".sidebar-nav-btn").forEach(b => b.classList.remove("active"));
        const recordBtn = document.querySelector('[data-pane="pane-record"]');
        if (recordBtn) recordBtn.classList.add("active");
    }

    // LOGIN OVERLAY FORM HANDLER
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const name = document.getElementById("loginName")?.value.trim() || "User";
            const email = document.getElementById("loginEmail")?.value.trim().toLowerCase() || "user@example.com";
            const role = document.getElementById("loginRole")?.value.trim() || "Team Member";
            const password = document.getElementById("loginPassword")?.value || "";

            // Ensure email is always trimmed and lowercase before generating the ID
            const cleanEmail = document.getElementById("loginEmail")?.value.trim().toLowerCase() || "user@example.com";
            const persistentUserId = "usr_" + btoa(cleanEmail).replace(/[^a-zA-Z0-9]/g, "").substring(0, 16);

            window.currentUser = { id: persistentUserId, name: name, email: email, role: role, password: password };

            const firstName = name.split(" ")[0];
            const initials = name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2);

            if (document.getElementById("greetingHeader")) document.getElementById("greetingHeader").textContent = `Welcome, ${firstName} !`;
            if (document.getElementById("profileDisplayName")) document.getElementById("profileDisplayName").textContent = name;
            if (document.getElementById("profileDisplayEmail")) document.getElementById("profileDisplayEmail").textContent = email;
            if (document.getElementById("avatarInitials")) document.getElementById("avatarInitials").textContent = initials || "U";

            document.getElementById("loginOverlay")?.classList.add("d-none");
            showDefaultPane();

            if (typeof loadSavedMeetings === "function") await loadSavedMeetings();
        });
    }

    // USER PROFILE MODAL CLICK HANDLER
    const userProfileBadge = document.getElementById("userProfileBadge");
    if (userProfileBadge) {
        userProfileBadge.addEventListener("click", async () => {
            if (!window.currentUser) return;

            const initials = window.currentUser.name.split(" ").map(n => n[0]).join("").toUpperCase().substring(0, 2);
            if (document.getElementById("modalUserAvatar")) document.getElementById("modalUserAvatar").textContent = initials || "U";
            if (document.getElementById("modalUserName")) document.getElementById("modalUserName").textContent = window.currentUser.name;
            if (document.getElementById("modalUserEmail")) document.getElementById("modalUserEmail").textContent = window.currentUser.email;
            if (document.getElementById("modalUserRole")) document.getElementById("modalUserRole").textContent = window.currentUser.role || "Team Member";

            try {
                const res = await fetch(`/api/mom/user/${window.currentUser.id}`);
                const list = await res.json();

                if (document.getElementById("modalTotalMeetings")) document.getElementById("modalTotalMeetings").textContent = list.length;
                if (document.getElementById("modalTotalDuration")) document.getElementById("modalTotalDuration").textContent = `${list.length} Records`;

                const historyList = document.getElementById("modalMeetingHistoryList");
                if (historyList) {
                    if (list.length === 0) {
                        historyList.innerHTML = `<div class="text-muted extra-small italic text-center py-2">No meeting records found.</div>`;
                    } else {
                        historyList.innerHTML = list.map(item => `
                            <div class="d-flex justify-content-between align-items-center p-1.5 bg-light rounded border extra-small mb-1">
                                <div>
                                    <span class="fw-bold text-dark">${item.title}</span>
                                    <div class="text-secondary" style="font-size:0.7rem;">Created: ${item.created_at}</div>
                                </div>
                                <span class="badge bg-secondary-subtle text-secondary border">Processed</span>
                            </div>
                        `).join("");
                    }
                }
            } catch (err) {
                console.warn("Could not fetch profile meeting log:", err);
            }

            const modalElem = document.getElementById("userProfileModal");
            if (modalElem && typeof bootstrap !== "undefined") {
                const modal = bootstrap.Modal.getOrCreateInstance(modalElem);
                modal.show();
            }
        });
    }

    // LOG OUT HANDLER
    const btnLogout = document.getElementById("btnLogout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            window.currentUser = null;
            window.currentPayload = null;

            const modalElem = document.getElementById("userProfileModal");
            if (modalElem && typeof bootstrap !== "undefined") {
                const modal = bootstrap.Modal.getInstance(modalElem);
                if (modal) modal.hide();
            }

            document.getElementById("loginForm")?.reset();
            document.getElementById("loginOverlay")?.classList.remove("d-none");
        });
    }

    // LEFT SIDEBAR NAVIGATION TABS
    document.querySelectorAll(".sidebar-nav-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const paneId = btn.getAttribute("data-pane");
            const featureKey = btn.getAttribute("data-feature");

            document.querySelectorAll(".sidebar-nav-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            hideAllPanes();

            if (paneId) {
                const activePane = document.getElementById(paneId);
                if (activePane) activePane.classList.remove("d-none");
            } else if (featureKey) {
                renderFeaturePane(featureKey);
            }
        });
    });

    // SAVED FILES STORAGE BUTTON
    const btnOpenSavedDrive = document.getElementById("btnOpenSavedDrive");
    if (btnOpenSavedDrive) {
        btnOpenSavedDrive.addEventListener("click", () => {
            document.querySelectorAll(".sidebar-nav-btn").forEach(b => b.classList.remove("active"));
            btnOpenSavedDrive.classList.add("active");

            hideAllPanes();

            const pane = document.getElementById("pane-feature");
            const title = document.getElementById("featureTitle");
            const featureActions = document.getElementById("featureActions");

            if (pane) pane.classList.remove("d-none");
            if (featureActions) featureActions.classList.add("d-none");
            if (title) title.textContent = "Saved Meetings Storage";

            loadSavedMeetingsInCanvas();
        });
    }

    // PROCESS PASTED DIALOGUE TEXT
    const btnProcessPaste = document.getElementById("btnProcessPaste");
    if (btnProcessPaste) {
        btnProcessPaste.addEventListener("click", async () => {
            const pasteInput = document.getElementById("pasteTextInput");
            if (!pasteInput) return;

            const text = pasteInput.value.trim();
            if (!text) return alert("Please paste conversation dialogue first.");

            btnProcessPaste.disabled = true;
            btnProcessPaste.textContent = "Processing with Ollama...";

            try {
                const res = await fetch("/api/text/process-paste", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ raw_text: text })
                });

                if (!res.ok) throw new Error(`HTTP error ${res.status}`);

                const data = await res.json();
                window.currentPayload = data;

                document.querySelectorAll(".sidebar-nav-btn").forEach(b => b.classList.remove("active"));
                const momBtn = document.querySelector('[data-feature="mom"]');
                if (momBtn) momBtn.classList.add("active");

                renderFeaturePane("mom");

            } catch (err) {
                alert("Processing Error: " + err.message + "\nEnsure local Ollama service is running.");
            } finally {
                btnProcessPaste.disabled = false;
                btnProcessPaste.textContent = "Process Text";
            }
        });
    }

    // PROCESS UPLOADED AUDIO FILE HANDLER
    const btnProcessUpload = document.getElementById("btnProcessUpload");
    if (btnProcessUpload) {
        btnProcessUpload.addEventListener("click", async () => {
            const fileInput = document.getElementById("fileInput");
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                return alert("Please select an audio file first.");
            }

            const formData = new FormData();
            formData.append("file", fileInput.files[0]);

            btnProcessUpload.disabled = true;
            btnProcessUpload.textContent = "Transcribing & Generating MoM...";

            try {
                const res = await fetch("/api/audio/upload", {
                    method: "POST",
                    body: formData
                });

                if (!res.ok) {
                    const errData = await res.json();
                    throw new Error(errData.detail || "Upload failed");
                }

                const data = await res.json();
                window.currentPayload = data;

                document.querySelectorAll(".sidebar-nav-btn").forEach(b => b.classList.remove("active"));
                const momBtn = document.querySelector('[data-feature="mom"]');
                if (momBtn) momBtn.classList.add("active");

                if (typeof renderFeaturePane === "function") {
                    renderFeaturePane("mom");
                }

                alert("Audio processed and MoM generated successfully!");

            } catch (err) {
                console.error(err);
                alert("Error: " + err.message);
            } finally {
                btnProcessUpload.disabled = false;
                btnProcessUpload.textContent = "Upload & Analyze";
            }
        });
    }

    // SAVE MEETING HANDLER
    const btnSaveMoM = document.getElementById("btnSaveMoM");
    if (btnSaveMoM) {
        btnSaveMoM.addEventListener("click", async () => {
            if (!window.currentPayload || !window.currentUser) {
                return alert("No active processed meeting available to save.");
            }

            const titleInput = document.getElementById("saveMeetingNameInput");
            const meetingTitle = titleInput ? titleInput.value.trim() : "";
            if (!meetingTitle) return alert("Please specify a title for this meeting.");

            try {
                const res = await fetch("/api/mom/save", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_id: window.currentUser.id,
                        title: meetingTitle,
                        transcript_text: window.currentPayload.transcript ? window.currentPayload.transcript.full_original_text : "",
                        mom_content: typeof window.currentPayload.mom === "string" ? window.currentPayload.mom : JSON.stringify(window.currentPayload.mom)
                    })
                });

                const data = await res.json();
                alert(data.message || "Meeting saved successfully!");
                if (titleInput) titleInput.value = "";
                loadSavedMeetings();
            } catch (err) {
                alert("Save Error: " + err.message);
            }
        });
    }

    // EXPORTS HANDLERS
    const btnExportPDF = document.getElementById("btnExportPDF");
    if (btnExportPDF) {
        btnExportPDF.addEventListener("click", () => {
            const element = document.getElementById("featureContent");
            if (!element || !element.innerText.trim()) return alert("No MoM content available to export.");

            const title = (document.getElementById("featureTitle")?.textContent || "Meeting_Minutes").replace(/[^a-zA-Z0-9]/g, "_");
            const opt = {
                margin: 0.5,
                filename: `${title}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
            };

            html2pdf().set(opt).from(element).save();
        });
    }

    const btnExportDOCX = document.getElementById("btnExportDOCX");
    if (btnExportDOCX) {
        btnExportDOCX.addEventListener("click", () => {
            const content = document.getElementById("featureContent")?.innerText;
            if (!content) return alert("No content available to export.");

            const title = (document.getElementById("featureTitle")?.textContent || "Meeting_Minutes").replace(/[^a-zA-Z0-9]/g, "_");

            const paragraphs = content.split("\n").map(line => {
                return new docx.Paragraph({
                    children: [new docx.TextRun({ text: line, size: 22 })],
                    space: { after: 120 }
                });
            });

            const doc = new docx.Document({
                sections: [{ properties: {}, children: paragraphs }]
            });

            docx.Packer.toBlob(doc).then(blob => {
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${title}.docx`;
                a.click();
                URL.revokeObjectURL(url);
            });
        });
    }

    const btnExportTXT = document.getElementById("btnExportTXT");
    if (btnExportTXT) {
        btnExportTXT.addEventListener("click", () => {
            const content = document.getElementById("featureContent")?.innerText;
            if (!content) return alert("No content available to export.");

            const title = (document.getElementById("featureTitle")?.textContent || "Meeting_Minutes").replace(/[^a-zA-Z0-9]/g, "_");
            const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `${title}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        });
    }

    // GROUNDED AI Q&A ASSISTANT HANDLER
    const btnAskQA = document.getElementById("btnAskQA");
    const qaInput = document.getElementById("qaQuestionInput");

    async function handleQASubmission() {
        const question = qaInput ? qaInput.value.trim() : "";
        if (!question) return;

        let textToQuery = "";
        if (window.currentPayload) {
            if (window.currentPayload.transcript && window.currentPayload.transcript.full_original_text) {
                textToQuery = window.currentPayload.transcript.full_original_text;
            } else if (typeof window.currentPayload.transcript === "string") {
                textToQuery = window.currentPayload.transcript;
            } else if (window.currentPayload.mom) {
                textToQuery = typeof window.currentPayload.mom === "string" 
                    ? window.currentPayload.mom 
                    : JSON.stringify(window.currentPayload.mom);
            }
        }

        if (!textToQuery) {
            const featureBox = document.getElementById("featureContent");
            if (featureBox && featureBox.innerText.trim().length > 10) {
                textToQuery = featureBox.innerText.trim();
            }
        }

        if (!textToQuery) {
            alert("Please upload an audio file or paste text first so the assistant has context to answer from.");
            return;
        }

        const answersContainer = document.getElementById("qaAnswersContainer");
        if (!answersContainer) return;

        const qDiv = document.createElement("div");
        qDiv.className = "fw-bold mt-1 text-primary extra-small";
        qDiv.textContent = `Q: ${question}`;

        const aDiv = document.createElement("div");
        aDiv.className = "text-secondary mb-2 extra-small";
        aDiv.textContent = "A: Thinking...";

        answersContainer.appendChild(qDiv);
        answersContainer.appendChild(aDiv);
        if (qaInput) qaInput.value = "";
        answersContainer.scrollTop = answersContainer.scrollHeight;

        try {
            const res = await fetch("/api/qa/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    question: question,
                    context: textToQuery,
                    transcript_text: textToQuery
                })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || `HTTP error ${res.status}`);
            }

            const data = await res.json();
            aDiv.textContent = "A: " + (data.answer || "No response generated.");
        } catch (err) {
            aDiv.textContent = "A: Error: " + err.message;
        }
        answersContainer.scrollTop = answersContainer.scrollHeight;
    }

    if (btnAskQA) {
        btnAskQA.addEventListener("click", (e) => {
            e.preventDefault();
            handleQASubmission();
        });
    }

    if (qaInput) {
        qaInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                handleQASubmission();
            }
        });
    }

    showDefaultPane();
});

// RENDER FEATURE VIEWS ON MAIN CANVAS STAGE
function renderFeaturePane(featureKey) {
    const pane = document.getElementById("pane-feature");
    const title = document.getElementById("featureTitle");
    const content = document.getElementById("featureContent");
    const featureActions = document.getElementById("featureActions");

    document.querySelectorAll(".stage-pane").forEach(p => p.classList.add("d-none"));

    if (pane) pane.classList.remove("d-none");
    if (featureActions) featureActions.classList.add("d-none");

    if (!window.currentPayload) {
        if (title) title.textContent = "No Data Loaded";
        if (content) content.innerHTML = "<p class='text-secondary extra-small'>Please record audio or paste text first to unlock feature insights.</p>";
        return;
    }

    // 1. DIARIZED TRANSCRIPT VIEW WITH TIMESTAMPS & REASSIGNABLE SPEAKERS
    if (featureKey === "transcript") {
        if (title) title.textContent = "Diarized Speaker Transcript";
        const utterances = window.currentPayload.transcript ? window.currentPayload.transcript.utterances : [];

        if (content) {
            if (utterances && utterances.length > 0) {
                content.innerHTML = `
                    <div class="mb-3 p-2 bg-light border rounded d-flex justify-content-between align-items-center">
                        <small class="text-secondary fw-semibold">Click on any speaker badge to rename across the transcript.</small>
                    </div>
                    <div id="transcriptUtterancesList">
                        ${utterances.map((u, idx) => {
                    const startTime = formatTime(u.start_time);
                    const endTime = formatTime(u.end_time);
                    const timeSpan = (u.start_time !== undefined && u.end_time !== undefined)
                        ? `<span class="badge bg-secondary-subtle text-dark border me-1" style="font-size:0.75rem;">${startTime} -${endTime}</span>`
                        : '';

                    return `
                                <div class="p-2.5 mb-2 bg-light rounded border border-secondary-subtle d-flex align-items-center gap-2">
                                    ${timeSpan}
                                    <span class="badge bg-primary clickable-speaker-badge" 
                                          data-speaker="${u.speaker}" 
                                          style="cursor: pointer; min-width: 95px; text-align: center;" 
                                          title="Click to rename speaker">
                                        ${u.speaker}
                                    </span>
                                    <span class="text-dark fw-medium flex-grow-1 ms-1">${u.text}</span>
                                </div>
                            `;
                }).join("")}
                    </div>
                `;

                document.querySelectorAll(".clickable-speaker-badge").forEach(badge => {
                    badge.addEventListener("click", (e) => {
                        const currentSpeaker = e.currentTarget.getAttribute("data-speaker");
                        const newName = prompt(`Rename speaker "${currentSpeaker}" to:`, currentSpeaker);

                        if (newName && newName.trim() && newName.trim() !== currentSpeaker) {
                            const updatedName = newName.trim();
                            window.currentPayload.transcript.utterances.forEach(u => {
                                if (u.speaker === currentSpeaker) u.speaker = updatedName;
                            });
                            renderFeaturePane("transcript");
                        }
                    });
                });

            } else {
                const rawText = window.currentPayload.transcript ? window.currentPayload.transcript.full_original_text : 'N/A';
                content.innerHTML = `<div class="p-3 bg-light rounded border"><p class="mb-0 text-dark">${rawText}</p></div>`;
            }
        }

    // 2. ADVANCED NLP ANALYSIS VIEW
    } else if (featureKey === "nlp") {
        if (title) title.textContent = "Meeting Intelligence & Analytics";
        const analysis = window.currentPayload.nlp_analysis || window.currentPayload.analysis || {};

        let sentimentStr = "Professional / Neutral";
        if (typeof analysis.sentiment === "string") sentimentStr = analysis.sentiment;
        else if (analysis.sentiment && analysis.sentiment.vibe) sentimentStr = analysis.sentiment.vibe;

        const entitiesList = (analysis.entities || []).length > 0
            ? analysis.entities.map(e => `<span class="badge bg-light text-dark border me-1 mb-1">${e.text || e} <small class="text-muted">(${e.label || 'ENTITY'})</small></span>`).join("")
            : '<span class="text-muted extra-small">No specific people, places, or dates detected.</span>';

        const keywordsList = (analysis.keywords || []).length > 0
            ? analysis.keywords.map(k => `<span class="badge bg-primary-subtle text-primary border me-1 mb-1">#${k}</span>`).join("")
            : '<span class="text-muted extra-small">No key topics identified.</span>';

        const actionsList = (analysis.action_items || []).length > 0
            ? analysis.action_items.map(a => `<li class="mb-1 text-dark extra-small">${a}</li>`).join("")
            : '<li class="text-muted extra-small">No explicit action items identified.</li>';

        const participationList = (analysis.participation || []).length > 0
            ? analysis.participation.map(p => `
                <div class="mb-1.5">
                    <div class="d-flex justify-content-between extra-small fw-semibold mb-0.5">
                        <span>${p.speaker}</span>
                        <span>${p.percentage}%</span>
                    </div>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar bg-primary" style="width: ${p.percentage}%"></div>
                    </div>
                </div>
            `).join("")
            : '<span class="text-muted extra-small">Single speaker context.</span>';

        if (content) {
            content.innerHTML = `
                <div class="vstack gap-3">
                    <div class="row g-2">
                        <div class="col-6">
                            <div class="p-3 bg-light rounded border h-100">
                                <div class="text-secondary extra-small fw-semibold text-uppercase mb-1">Meeting Tone & Vibe</div>
                                <h6 class="fw-bold text-dark mb-0">${sentimentStr}</h6>
                            </div>
                        </div>
                        <div class="col-6">
                            <div class="p-3 bg-light rounded border h-100">
                                <div class="text-secondary extra-small fw-semibold text-uppercase mb-1">Hinglish Language Ratio</div>
                                <h6 class="fw-bold text-dark mb-0">${analysis.hinglish_ratio || 0}% <small class="text-muted fw-normal" style="font-size:0.7rem;">Code-Switched</small></h6>
                            </div>
                        </div>
                    </div>

                    <div class="p-3 bg-light rounded border">
                        <div class="text-secondary extra-small fw-semibold text-uppercase mb-2">Speaker Discussion Share</div>
                        <div>${participationList}</div>
                    </div>

                    <div class="p-3 bg-light rounded border">
                        <div class="text-secondary extra-small fw-semibold text-uppercase mb-2">Detected Action Items</div>
                        <ul class="list-unstyled mb-0">${actionsList}</ul>
                    </div>

                    <div class="p-3 bg-light rounded border">
                        <div class="text-secondary extra-small fw-semibold text-uppercase mb-2">Core Discussion Topics</div>
                        <div>${keywordsList}</div>
                    </div>

                    <div class="p-3 bg-light rounded border">
                        <div class="text-secondary extra-small fw-semibold text-uppercase mb-2">Key References & Mentioned Details</div>
                        <div>${entitiesList}</div>
                    </div>
                </div>
            `;
        }

    // 3. EXECUTIVE SUMMARY VIEW
    } else if (featureKey === "summary") {
        if (title) title.textContent = "Detailed Executive Summary";
        const summaryText = window.currentPayload.summary || "Summary generated successfully.";
        if (content) content.innerHTML = `<div class="p-3.5 bg-light rounded border"><p class="text-dark mb-0" style="font-size:0.88rem; line-height:1.6;">${summaryText}</p></div>`;

    // 4. MINUTES OF MEETING (MOM) VIEW
    } else if (featureKey === "mom") {
        if (title) title.textContent = "Minutes of Meeting (MoM)";
        if (featureActions) featureActions.classList.remove("d-none");
        const rawMom = typeof window.currentPayload.mom === "string" ? window.currentPayload.mom : JSON.stringify(window.currentPayload.mom);
        if (content) content.innerHTML = typeof marked !== "undefined" ? marked.parse(rawMom) : rawMom;
    }
}

// FETCH SAVED MEETINGS IN RIGHT SIDEBAR
async function loadSavedMeetings() {
    if (!window.currentUser) return;
    const container = document.getElementById("savedMeetingsList");
    if (!container) return;

    try {
        const res = await fetch(`/api/mom/user/${window.currentUser.id}`);
        const list = await res.json();
        container.innerHTML = "";

        if (list.length === 0) {
            container.innerHTML = "<div class='text-secondary extra-small italic py-1'>No meetings saved yet.</div>";
            return;
        }

        list.forEach(item => {
            const div = document.createElement("div");
            div.className = "meeting-item d-flex justify-content-between align-items-center";
            div.innerHTML = `
                <div class="d-flex align-items-center gap-2 overflow-hidden item-click-target" style="cursor: pointer;">
                    <div class="overflow-hidden">
                        <div class="fw-semibold extra-small text-dark text-truncate">${item.title}</div>
                        <div class="extra-small text-secondary">${item.created_at}</div>
                    </div>
                </div>
                <button class="btn btn-sm text-danger p-0 border-0 btn-delete-item" data-id="${item.id}">Delete</button>
            `;

            div.querySelector(".item-click-target").addEventListener("click", () => {
                openSavedMeetingInCanvas(item);
            });

            div.querySelector(".btn-delete-item").addEventListener("click", async (e) => {
                e.stopPropagation();
                if (confirm(`Delete "${item.title}"?`)) {
                    await fetch(`/api/mom/delete/${item.id}`, { method: "DELETE" });
                    loadSavedMeetings();
                }
            });

            container.appendChild(div);
        });
    } catch (err) {
        container.innerHTML = "<div class='text-danger extra-small'>Failed to load saved items.</div>";
    }
}

// RENDER SAVED MEETINGS MATRIX IN MAIN STAGE CANVAS
async function loadSavedMeetingsInCanvas() {
    if (!window.currentUser) return;
    const content = document.getElementById("featureContent");
    if (!content) return;

    try {
        const res = await fetch(`/api/mom/user/${window.currentUser.id}`);
        const list = await res.json();

        if (list.length === 0) {
            content.innerHTML = "<p class='text-secondary extra-small'>No saved meetings found in storage.</p>";
            return;
        }

        content.innerHTML = list.map(item => `
            <div class="p-3 bg-light rounded border mb-2 d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="fw-bold text-dark mb-1">${item.title}</h6>
                    <div class="extra-small text-secondary">Created: ${item.created_at}</div>
                </div>
                <button class="btn btn-primary btn-sm btn-view-file" data-id="${item.id}">View MoM</button>
            </div>
        `).join("");

        content.querySelectorAll(".btn-view-file").forEach((btn, idx) => {
            btn.addEventListener("click", () => openSavedMeetingInCanvas(list[idx]));
        });

    } catch (err) {
        content.innerHTML = "<p class='text-danger extra-small'>Failed to load storage files.</p>";
    }
}

// OPEN SAVED MEETING DIRECTLY ON CANVAS
function openSavedMeetingInCanvas(item) {
    document.querySelectorAll(".stage-pane").forEach(p => p.classList.add("d-none"));

    const pane = document.getElementById("pane-feature");
    const title = document.getElementById("featureTitle");
    const content = document.getElementById("featureContent");
    const featureActions = document.getElementById("featureActions");

    if (pane) pane.classList.remove("d-none");
    if (featureActions) featureActions.classList.remove("d-none");

    if (title) title.textContent = `${item.title}`;
    if (content) content.innerHTML = typeof marked !== "undefined" ? marked.parse(item.mom_output) : item.mom_output;

    window.currentPayload = {
        transcript: { full_original_text: item.transcript || item.mom_output },
        mom: item.mom_output
    };
}