import subprocess
from datetime import date, datetime, timedelta

from config import PROJECTS, REPORT_BRANCHES


def _repo_path(project_name: str) -> str | None:
    return PROJECTS.get(project_name)


def _report_branches(project_name: str, repo_path: str) -> list[str]:
    allowed = REPORT_BRANCHES.get(project_name, [])
    if not allowed:
        return []

    local_branches = {
        line.strip()
        for line in _run_git(repo_path, "branch", "--list", "--format=%(refname:short)").splitlines()
        if line.strip()
    }
    return [branch for branch in allowed if branch in local_branches]


def _current_branch(repo_path: str) -> str:
    return _run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")


def _run_git(repo_path: str, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 and not result.stdout.strip():
        return result.stderr.strip()
    return result.stdout.strip()


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


def _day_range(day: date) -> tuple[str, str]:
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    return start.isoformat(sep=" "), end.isoformat(sep=" ")


def _parse_commit_log(output: str) -> list[dict]:
    if not output or output.startswith("fatal:"):
        return []

    commits: list[dict] = []
    current: dict | None = None

    for line in output.splitlines():
        parts = line.split("|", 2)
        if len(parts) == 3 and len(parts[0]) == 40:
            if current:
                commits.append(current)
            current = {
                "hash": parts[0][:8],
                "date": parts[1],
                "subject": parts[2],
                "files": [],
            }
            continue

        if current and line and line[0] in "AMDRTUC":
            current["files"].append(line)

    if current:
        commits.append(current)

    return [
        commit
        for commit in commits
        if not commit["subject"].startswith("index on ")
        and not commit["subject"].startswith("untracked files on ")
        and not commit["subject"].startswith("On ")
        and not commit["subject"].endswith(": ec")
    ]


def get_commits_for_date(project_name: str, report_date: str | date | None = None) -> list[dict]:
    repo_path = _repo_path(project_name)
    if not repo_path:
        return []

    branches = _report_branches(project_name, repo_path)
    if not branches:
        return []

    day = _parse_report_date(report_date)
    since, until = _day_range(day)
    output = _run_git(
        repo_path,
        "log",
        *branches,
        f"--since={since}",
        f"--until={until}",
        "--no-merges",
        '--pretty=format:%H|%ad|%s',
        "--date=format:%Y-%m-%d %H:%M",
        "--name-status",
    )
    return _parse_commit_log(output)


def get_unpushed_commits(project_name: str, report_date: str | date | None = None) -> list[dict]:
    repo_path = _repo_path(project_name)
    if not repo_path:
        return []

    branches = _report_branches(project_name, repo_path)
    if not branches:
        return []

    day = _parse_report_date(report_date)
    since, until = _day_range(day)
    commits: list[dict] = []
    seen_hashes: set[str] = set()

    for branch in branches:
        remote_ref = f"origin/{branch}"
        if _run_git(repo_path, "rev-parse", "--verify", remote_ref).startswith("fatal:"):
            continue

        output = _run_git(
            repo_path,
            "log",
            f"{remote_ref}..{branch}",
            f"--since={since}",
            f"--until={until}",
            '--pretty=format:%h|%ad|%s',
            "--date=format:%Y-%m-%d %H:%M",
        )
        if not output or output.startswith("fatal:"):
            continue

        for line in output.splitlines():
            parts = line.split("|", 2)
            if len(parts) != 3 or parts[0] in seen_hashes:
                continue
            seen_hashes.add(parts[0])
            commits.append({"hash": parts[0], "date": parts[1], "subject": parts[2], "branch": branch})

    commits.sort(key=lambda item: item["date"])
    return commits


def get_local_changes(project_name: str) -> dict:
    repo_path = _repo_path(project_name)
    if not repo_path:
        return {"error": "Project not found", "has_changes": False}

    branches = _report_branches(project_name, repo_path)
    current = _current_branch(repo_path)
    if current not in branches:
        return {
            "status": "",
            "unstaged_diff_stat": "",
            "staged_diff_stat": "",
            "untracked_files": [],
            "has_changes": False,
            "skipped_branch": current,
            "allowed_branches": branches,
        }

    status = _run_git(repo_path, "status", "--short")
    unstaged = _run_git(repo_path, "diff", "--stat")
    staged = _run_git(repo_path, "diff", "--cached", "--stat")
    untracked = _run_git(repo_path, "ls-files", "--others", "--exclude-standard")

    return {
        "status": status,
        "unstaged_diff_stat": unstaged,
        "staged_diff_stat": staged,
        "untracked_files": untracked.splitlines() if untracked else [],
        "has_changes": bool(status or untracked),
        "branch": current,
        "allowed_branches": branches,
    }


def format_commits(commits: list[dict], title: str) -> str:
    if not commits:
        return ""

    lines = [title]
    for commit in commits:
        branch = f" [{commit['branch']}]" if commit.get("branch") else ""
        lines.append(f"- [{commit['hash']}] {commit['subject']} ({commit['date']}){branch}")
        for file_line in commit.get("files", [])[:15]:
            lines.append(f"  {file_line}")
        if len(commit.get("files", [])) > 15:
            lines.append(f"  ... and {len(commit['files']) - 15} more files")
    return "\n".join(lines)


def format_local_changes(changes: dict) -> str:
    if changes.get("error"):
        return changes["error"]
    if changes.get("skipped_branch"):
        return ""
    if not changes.get("has_changes"):
        return ""

    lines = [f"Local changes on {changes.get('branch')} (not committed yet):"]
    if changes.get("status"):
        lines.append("Status:")
        lines.append(changes["status"])
    if changes.get("staged_diff_stat"):
        lines.append("Staged:")
        lines.append(changes["staged_diff_stat"])
    if changes.get("unstaged_diff_stat"):
        lines.append("Unstaged:")
        lines.append(changes["unstaged_diff_stat"])
    if changes.get("untracked_files"):
        lines.append("Untracked files:")
        for path in changes["untracked_files"][:20]:
            lines.append(f"- {path}")
        if len(changes["untracked_files"]) > 20:
            lines.append(f"... and {len(changes['untracked_files']) - 20} more")
    return "\n".join(lines)


def get_project_activity(project_name: str, report_date: str | date | None = None) -> dict:
    day = _parse_report_date(report_date)
    repo_path = _repo_path(project_name)
    branches = _report_branches(project_name, repo_path) if repo_path else []
    commits = get_commits_for_date(project_name, day)
    unpushed = get_unpushed_commits(project_name, day)
    local = get_local_changes(project_name)

    include_working_tree = day >= date.today() - timedelta(days=1)

    sections = []
    branch_note = f"Branches: {', '.join(branches)}" if branches else "Branches: none configured"
    commit_text = format_commits(commits, f"Commits on {day.strftime('%d/%m/%Y')} ({branch_note}):")
    if commit_text:
        sections.append(commit_text)

    if include_working_tree:
        local_text = format_local_changes(local)
        if local_text:
            sections.append(local_text)

        unpushed_text = format_commits(
            unpushed if commits or local.get("has_changes") else unpushed,
            "Unpushed commits:",
        )
        if unpushed_text:
            sections.append(unpushed_text)

    has_git_activity = bool(commits or unpushed or local.get("has_changes"))

    return {
        "project": project_name,
        "date": day.strftime("%d/%m/%Y"),
        "branches": branches,
        "commits": commits,
        "unpushed": unpushed,
        "local_changes": local,
        "has_git_activity": has_git_activity,
        "summary": "\n\n".join(sections) if sections else "",
    }


def get_diff(project_name: str, report_date: str | date | None = None) -> str:
    activity = get_project_activity(project_name, report_date)
    return activity["summary"] or "No git activity found for this date on configured branches."


def get_today_commits(project_name: str) -> str:
    activity = get_project_activity(project_name)
    return activity["summary"] or "No commits or local changes found today on configured branches."
