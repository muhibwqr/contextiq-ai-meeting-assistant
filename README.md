# ContextIQ — AI-Powered Meeting Assistant

> Extract action items, assign owners, and draft follow-up emails from any meeting transcript — powered by GPT-4.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## What is ContextIQ?

ContextIQ is a context-aware meeting summarizer that takes raw meeting transcripts (or audio) and automatically:

- **Summarizes** the meeting into concise bullet points
- **Extracts action items** with clear task descriptions
- **Assigns owners** by matching action items to speakers/participants
- **Sets deadlines** by parsing temporal references ("by Friday", "next week", etc.)
- **Drafts follow-up emails** ready to send to all participants

Built for HackIllinois 2026.

---

## Features

| Feature | Description |
|---|---|
| GPT-4 Summarization | Intelligent meeting summary with context preservation |
| Action Item Extraction | Automatically identifies tasks, owners, and deadlines |
| Owner Assignment | Maps action items to specific participants |
| Follow-up Email Draft | Generates professional follow-up email HTML |
| REST API | FastAPI endpoints for easy integration |
| CLI Mode | Run directly from terminal with a transcript file |

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/muhibwqr/contextiq-ai-meeting-assistant.git
cd contextiq-ai-meeting-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key

```bash
export OPENAI_API_KEY=sk-...
```

### 4. Run via CLI

```bash
python app.py --transcript transcript.txt --participants "Alice, Bob, Carol"
```

### 5. Run as API server

```bash
uvicorn app:app --reload
# API available at http://localhost:8000
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze` | Analyze a meeting transcript |
| POST | `/summarize` | Get meeting summary only |
| POST | `/action-items` | Extract action items only |
| POST | `/draft-email` | Generate follow-up email |
| GET | `/health` | Health check |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Alice: We need to finish the landing page by Friday. Bob: I can handle the backend API by next Monday.",
    "participants": ["Alice", "Bob"],
    "meeting_title": "Sprint Planning"
  }'
```

### Example Response

```json
{
  "summary": "Sprint planning meeting covering landing page and backend API tasks.",
  "action_items": [
    {"task": "Finish landing page", "owner": "Alice", "deadline": "Friday"},
    {"task": "Complete backend API", "owner": "Bob", "deadline": "Next Monday"}
  ],
  "follow_up_email": {
    "subject": "Sprint Planning — Action Items & Next Steps",
    "body": "Hi team, here's a summary of today's sprint planning meeting..."
  }
}
```

---

## Project Structure

```
contextiq-ai-meeting-assistant/
├── app.py              # Main application (FastAPI + CLI)
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── transcript.txt      # Sample transcript (optional)
```

---

## Built With

- [OpenAI GPT-4](https://openai.com) — Core AI engine for summarization and extraction
- [FastAPI](https://fastapi.tiangolo.com) — High-performance REST API framework
- [Uvicorn](https://www.uvicorn.org) — ASGI server
- [Pydantic](https://docs.pydantic.dev) — Data validation and serialization
- [python-dotenv](https://pypi.org/project/python-dotenv/) — Environment variable management

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `OPENAI_MODEL` | No | Model to use (default: `gpt-4`) |
| `PORT` | No | API server port (default: `8000`) |

---

## Hackathon Submission

Built at **HackIllinois 2026** (Feb 28 — Mar 01, 2026)

**Team:** Muhib Waqar
**Track:** Machine Learning / AI

---

## License

MIT License — see [LICENSE](LICENSE) for details.
