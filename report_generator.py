from config import PROJECTS

from cursor_tools import get_cursor_activity
from git_tools import get_project_activity


def gather_project_activity(project_name: str, report_date: str | None = None) -> dict:
    git_activity = get_project_activity(project_name, report_date)
    cursor_activity = get_cursor_activity(project_name, report_date)

    sections = []
    if git_activity["summary"]:
        sections.append(git_activity["summary"])
    if cursor_activity["summary"]:
        sections.append(cursor_activity["summary"])

    has_activity = bool(
        git_activity["has_git_activity"] or cursor_activity["sessions"]
    )

    return {
        "project": project_name,
        "date": git_activity["date"],
        "branches": git_activity["branches"],
        "git": git_activity,
        "cursor": cursor_activity,
        "has_activity": has_activity,
        "combined_summary": "\n\n".join(sections) if has_activity else "",
    }


def get_active_projects(report_date: str | None = None) -> list[str]:
    return [
        project_name
        for project_name in PROJECTS
        if gather_project_activity(project_name, report_date)["has_activity"]
    ]


def build_prompt(project_name: str, activity_text: str, report_date: str | None = None) -> str:
    date_line = f"\nReport date: {report_date}\n" if report_date else ""

    return f"""
You are generating a daily work report.
{date_line}
Project:
{project_name}

Activity sources below may include:
- Git commits on the report date (only configured report branches)
- Local uncommitted changes on the current report branch
- Unpushed commits on configured report branches
- Cursor chat sessions from that day (tasks you worked on in the IDE)

Activity:
{activity_text}

Generate:

1. TASK_MODULE
2. DESCRIPTION

Keep professional.
Max 2 lines for DESCRIPTION.
Prefer real work from Cursor sessions and local changes when there are no commits.
"""
