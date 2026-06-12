from mcp.server.fastmcp import FastMCP

from config import PROJECTS
from excel_tools import add_report_row
from git_tools import get_diff, get_local_changes
from report_generator import build_prompt, gather_project_activity, get_active_projects

mcp = FastMCP("WorkReport")


@mcp.tool()
def scan_project(project_name: str, report_date: str | None = None):
    """
    Get project activity for a date.

    Git activity is limited to configured report branches:
    - vlab: Nirva, main
    - laajavaab: Nirva

    Includes commits, local uncommitted changes, unpushed commits,
    and Cursor chat session history for that day.
    report_date format: DD/MM/YYYY (e.g. 11/06/2026). Defaults to today.
    """
    return gather_project_activity(project_name, report_date)


@mcp.tool()
def list_active_projects(report_date: str | None = None):
    """
    Return project names that have activity for the given date.
    Projects with no commits, local changes, or Cursor sessions are omitted.
    """
    sample = gather_project_activity(next(iter(PROJECTS)), report_date) if PROJECTS else None
    return {
        "date": sample["date"] if sample else None,
        "active_projects": get_active_projects(report_date),
    }


@mcp.tool()
def generate_daily_report(project_name: str, report_date: str | None = None):
    """
    Build a prompt to generate a daily work report from all activity sources.
    Returns a skip message if the project has no activity for that date.
    """
    activity = gather_project_activity(project_name, report_date)
    if not activity["has_activity"]:
        return {
            "skipped": True,
            "project": project_name,
            "date": activity["date"],
            "message": "No activity found on configured branches or in Cursor history. Report not needed.",
        }

    return build_prompt(
        project_name,
        activity["combined_summary"],
        report_date=activity["date"],
    )


@mcp.tool()
def get_project_changes(project_name: str, report_date: str | None = None):
    """
    Return git changes for the given project and date.
    Only includes configured report branches.
    For today/yesterday, also includes uncommitted and unpushed work.
    """
    return get_diff(project_name, report_date)


@mcp.tool()
def get_pending_changes(project_name: str):
    """
    Return current local git status on the active report branch.
    Useful when work was done but not committed yet.
    """
    return get_local_changes(project_name)


@mcp.tool()
def create_report(
    project_name: str,
    task_module: str,
    description: str,
    status: str = "Completed",
    report_date: str | None = None,
):
    """
    Create a new daily work report entry.

    Spreadsheet Update Rules:
    - NEVER modify the workbook layout or formatting.
    - NEVER overwrite or edit existing report rows.
    - ALWAYS append a NEW row at the end of the report table.
    - Preserve the existing formatting by copying the previous row's
      styles, text wrapping, borders, fonts, colors, dropdowns,
      formulas, and date formats.
    - Do NOT change column widths, row heights, filters,
      merged cells, or worksheet properties.
    - Only write the provided values into the new row.
    - Treat the workbook as a fixed template and only append data.

    Only call this for projects that have activity for the date.
    Use list_active_projects() first to see which projects qualify.

    Parameters:
    - project_name: Name of the project.
    - task_module: Task title or module name.
    - description: Detailed work description.
    - status: Work status (default: Completed).
    - report_date: Date for the row in DD/MM/YYYY format. Defaults to today.
    """
    activity = gather_project_activity(project_name, report_date)
    if not activity["has_activity"]:
        return {
            "skipped": True,
            "project": project_name,
            "date": activity["date"],
            "message": "No activity found. Row was not added.",
        }

    return add_report_row(
        project_name=project_name,
        task_module=task_module,
        description=description,
        status=status,
        report_date=activity["date"],
    )


if __name__ == "__main__":
    mcp.run()
