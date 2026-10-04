import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "MeetMemo" in response.text or "message" in response.json()

def test_process_pasted_text():
    payload = {
        "raw_text": "Alice: Welcome to the project sync.\nBob: Thanks Alice, I finished the backend setup.\nCharlie: Great! I will test the API endpoints tomorrow."
    }
    response = client.post("/api/text/process-paste", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "transcript" in data
    assert "utterances" in data["transcript"]
    assert len(data["transcript"]["utterances"]) >= 3
    speakers = set(u["speaker"] for u in data["transcript"]["utterances"])
    assert "Alice" in speakers
    assert "Bob" in speakers
    assert "Charlie" in speakers

def test_qa_endpoint():
    payload = {
        "question": "Who will test the API endpoints?",
        "transcript": "Charlie: I will test the API endpoints tomorrow."
    }
    response = client.post("/api/qa/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
