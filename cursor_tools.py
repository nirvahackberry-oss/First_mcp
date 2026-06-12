import json
import os
import re
from datetime import date, datetime, timedelta
from pathlib import Path

from config import CURSOR_PROJECTS, CURSOR_TRANSCRIPTS_ROOT


def _parse_report_date(report_date: str | date | None) -> date:
    if report_date is None:
        return date.today()
    if isinstance(report_date, date):
        return report_date

    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(report_date, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {report_date}")


def _transcript_dir(project_name: str) -> Path | None:
    cursor_slug = CURSOR_PROJECTS.get(project_name)
    if not cursor_slug:
        return None
    return Path(CURSOR_TRANSCRIPTS_ROOT) / cursor_slug / "agent-transcripts"


def _clean_user_text(text: str) -> str:
    text = re.sub(r"\[Image\].*?</image_files>", "", text, flags=re.DOTALL)
    match = re.search(r"<user_query>\s*(.*?)\s*</user_query>", text, re.DOTALL)
    if match:
        text = match.group(1)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def _clean_assistant_text(text: str) -> str:
    text = re.sub(r"\[REDACTED\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]


def _extract_message_text(message: dict) -> str:
    parts = []
    for item in message.get("content", []):
        if item.get("type") == "text":
            parts.append(item.get("text", ""))
    return "\n".join(parts)


def _parse_transcript(path: Path) -> dict:
    user_queries: list[str] = []
    assistant_summaries: list[str] = []

    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            role = entry.get("role")
            text = _extract_message_text(entry.get("message", {}))
            if not text:
                continue

            if role == "user":
                cleaned = _clean_user_text(text)
                if cleaned:
                    user_queries.append(cleaned)
            elif role == "assistant":
                cleaned = _clean_assistant_text(text)
                if cleaned and len(cleaned) > 30:
                    assistant_summaries.append(cleaned)

    return {
        "session_id": path.parent.name,
        "file": str(path),
        "user_queries": user_queries,
        "assistant_summaries": assistant_summaries,
    }


def get_cursor_sessions_for_date(project_name: str, report_date: str | date | None = None) -> list[dict]:
    transcript_dir = _transcript_dir(project_name)
    if not transcript_dir or not transcript_dir.exists():
        return []

    day = _parse_report_date(report_date)
    sessions: list[dict] = []

    for path in transcript_dir.rglob("*.jsonl"):
        if "subagents" in path.parts:
            continue

        modified = datetime.fromtimestamp(path.stat().st_mtime).date()
        if modified != day:
            continue

        parsed = _parse_transcript(path)
        if parsed["user_queries"] or parsed["assistant_summaries"]:
            parsed["date"] = day.strftime("%d/%m/%Y")
            parsed["modified_at"] = datetime.fromtimestamp(path.stat().st_mtime).isoformat(sep=" ", timespec="minutes")
            sessions.append(parsed)

    sessions.sort(key=lambda item: item["modified_at"])
    return sessions


def format_cursor_sessions(sessions: list[dict]) -> str:
    if not sessions:
        return ""

    lines = [f"Cursor sessions ({len(sessions)}):"]
    for index, session in enumerate(sessions, start=1):
        lines.append(f"{index}. Session {session['session_id'][:8]} at {session['modified_at']}")
        for query in session["user_queries"][:3]:
            lines.append(f"   Task: {query}")
        if session["assistant_summaries"]:
            lines.append(f"   Work done: {session['assistant_summaries'][0]}")
    return "\n".join(lines)


def get_cursor_activity(project_name: str, report_date: str | date | None = None) -> dict:
    sessions = get_cursor_sessions_for_date(project_name, report_date)
    return {
        "sessions": sessions,
        "summary": format_cursor_sessions(sessions),
    }
