#!/usr/bin/env python3
"""
ContextIQ - AI-Powered Meeting Assistant
Extracts action items, assigns owners, and drafts follow-up emails using GPT-4.
Built for HackIllinois 2026.
"""

import os
import json
import argparse
from typing import List, Optional

import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ---- OpenAI Setup ----
openai.api_key = os.getenv("OPENAI_API_KEY", "")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# ---- FastAPI App ----
app = FastAPI(
    title="ContextIQ - AI Meeting Assistant",
    description="Extract action items, assign owners, and draft follow-up emails from meeting transcripts.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---- Pydantic Models ----
class MeetingRequest(BaseModel):
    transcript: str
    participants: Optional[List[str]] = []
    meeting_title: Optional[str] = "Meeting"


class ActionItem(BaseModel):
    task: str
    owner: str
    deadline: str


class MeetingAnalysis(BaseModel):
    summary: str
    action_items: List[ActionItem]
    follow_up_email: dict


class SummaryResponse(BaseModel):
    summary: str


class ActionItemsResponse(BaseModel):
    action_items: List[ActionItem]


class EmailResponse(BaseModel):
    subject: str
    body: str


# ---- Core AI Functions ----

def call_gpt(system_prompt: str, user_prompt: str) -> str:
    """Call GPT-4 with a system and user prompt, return the response text."""
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def summarize_meeting(transcript: str, meeting_title: str) -> str:
    """Generate a concise meeting summary."""
    system_prompt = (
        "You are an expert meeting analyst. Summarize the following meeting transcript "
        "into 3-5 concise bullet points capturing the key decisions and discussions. "
        "Be specific and professional."
    )
    user_prompt = f"Meeting Title: {meeting_title}\n\nTranscript:\n{transcript}"
    return call_gpt(system_prompt, user_prompt)


def extract_action_items(transcript: str, participants: List[str]) -> List[ActionItem]:
    """Extract action items with owners and deadlines from transcript."""
    participant_list = ", ".join(participants) if participants else "unknown participants"
    system_prompt = (
        "You are an expert at extracting action items from meeting transcripts. "
        "Return a JSON array of action items. Each item must have: "
        "'task' (string), 'owner' (string - name of responsible person), "
        "'deadline' (string - deadline mentioned or 'Not specified'). "
        "Only return valid JSON, no explanation."
    )
    user_prompt = (
        f"Participants: {participant_list}\n\n"
        f"Transcript:\n{transcript}\n\n"
        "Extract all action items as a JSON array."
    )
    raw = call_gpt(system_prompt, user_prompt)
    # Strip markdown code fences if present
    raw = raw.strip().strip("```json").strip("```").strip()
    try:
        items = json.loads(raw)
        return [ActionItem(**item) for item in items]
    except Exception:
        return [ActionItem(task="Review meeting transcript manually", owner="Team", deadline="ASAP")]


def draft_follow_up_email(
    meeting_title: str,
    summary: str,
    action_items: List[ActionItem],
    participants: List[str],
) -> dict:
    """Draft a professional follow-up email for the meeting."""
    action_items_text = "\n".join(
        [f"- {item.task} (Owner: {item.owner}, Deadline: {item.deadline})" for item in action_items]
    )
    system_prompt = (
        "You are a professional business writer. Draft a concise, friendly follow-up email "
        "after a meeting. Return JSON with two fields: 'subject' and 'body'. "
        "The body should be plain text, professional, and end with a call to action. "
        "Only return valid JSON."
    )
    user_prompt = (
        f"Meeting Title: {meeting_title}\n"
        f"Participants: {', '.join(participants) if participants else 'Team'}\n\n"
        f"Summary:\n{summary}\n\n"
        f"Action Items:\n{action_items_text}\n\n"
        "Draft a follow-up email."
    )
    raw = call_gpt(system_prompt, user_prompt)
    raw = raw.strip().strip("```json").strip("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        return {
            "subject": f"Follow-up: {meeting_title}",
            "body": f"Hi team,\n\nPlease find the action items from our meeting below:\n\n{action_items_text}\n\nBest regards",
        }


def analyze_meeting(transcript: str, participants: List[str], meeting_title: str) -> MeetingAnalysis:
    """Full pipeline: summarize, extract action items, and draft email."""
    summary = summarize_meeting(transcript, meeting_title)
    action_items = extract_action_items(transcript, participants)
    follow_up_email = draft_follow_up_email(meeting_title, summary, action_items, participants)
    return MeetingAnalysis(
        summary=summary,
        action_items=action_items,
        follow_up_email=follow_up_email,
    )


# ---- FastAPI Routes ----

@app.get("/health")
def health_check():
    return {"status": "ok", "model": MODEL}


@app.post("/analyze", response_model=MeetingAnalysis)
def analyze_endpoint(request: MeetingRequest):
    """Full analysis: summary + action items + follow-up email."""
    try:
        result = analyze_meeting(request.transcript, request.participants, request.meeting_title)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/summarize", response_model=SummaryResponse)
def summarize_endpoint(request: MeetingRequest):
    """Summarize the meeting transcript only."""
    try:
        summary = summarize_meeting(request.transcript, request.meeting_title)
        return SummaryResponse(summary=summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


@app.post("/action-items", response_model=ActionItemsResponse)
def action_items_endpoint(request: MeetingRequest):
    """Extract action items from the meeting transcript."""
    try:
        items = extract_action_items(request.transcript, request.participants)
        return ActionItemsResponse(action_items=items)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@app.post("/draft-email", response_model=EmailResponse)
def draft_email_endpoint(request: MeetingRequest):
    """Draft a follow-up email from the meeting transcript."""
    try:
        summary = summarize_meeting(request.transcript, request.meeting_title)
        action_items = extract_action_items(request.transcript, request.participants)
        email = draft_follow_up_email(request.meeting_title, summary, action_items, request.participants)
        return EmailResponse(subject=email.get("subject", ""), body=email.get("body", ""))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email drafting failed: {str(e)}")


# ---- CLI Mode ----

def run_cli():
    parser = argparse.ArgumentParser(description="ContextIQ - AI Meeting Assistant (CLI)")
    parser.add_argument("--transcript", required=True, help="Path to transcript text file")
    parser.add_argument("--participants", default="", help="Comma-separated list of participant names")
    parser.add_argument("--title", default="Meeting", help="Meeting title")
    args = parser.parse_args()

    with open(args.transcript, "r") as f:
        transcript = f.read()

    participants = [p.strip() for p in args.participants.split(",") if p.strip()]

    print(f"\nAnalyzing '{args.title}'...\n")
    result = analyze_meeting(transcript, participants, args.title)

    print("=" * 60)
    print("MEETING SUMMARY")
    print("=" * 60)
    print(result.summary)

    print("\n" + "=" * 60)
    print("ACTION ITEMS")
    print("=" * 60)
    for i, item in enumerate(result.action_items, 1):
        print(f"{i}. {item.task}")
        print(f"   Owner: {item.owner} | Deadline: {item.deadline}")

    print("\n" + "=" * 60)
    print("FOLLOW-UP EMAIL")
    print("=" * 60)
    print(f"Subject: {result.follow_up_email.get('subject', '')}")
    print(f"\n{result.follow_up_email.get('body', '')}")
    print("=" * 60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_cli()
    else:
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
