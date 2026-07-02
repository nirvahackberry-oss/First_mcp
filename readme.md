# Work Report MCP

Automate daily work reports from git activity, local changes, and Cursor chat history — then append rows to a **Zoho Sheet**.

## What it does

1. Scans configured projects for work on a given date.
2. Pulls activity from git (commits, unpushed work, uncommitted changes) and Cursor session history.
3. Generates a professional task summary.
4. Appends a new row to your Zoho Sheet (never overwrites existing rows).

Projects with **no activity are skipped** — no empty rows are added.

---

## Folder structure

```text
D:\
│
├── MCP/
|   ├── server.py              # MCP server entry point
|   ├── config.py              # Project paths and branch rules (no secrets)
|   ├── git_tools.py           # Git commits, local changes, unpushed commits
|   ├── cursor_tools.py        # Cursor chat transcript history
|   ├── report_generator.py    # Combines activity sources
|   ├── excel_tools.py         # Zoho Sheet API (append rows)
|   ├── zoho_auth.py           # OAuth token refresh and .env persistence
|   ├── get_zoho_token.py      # OAuth helper for Zoho tokens
|   ├── requirements.txt
|   ├── .env.example           # Template for secrets (commit this)
|   ├── .env                   # Your real credentials (never commit)
|   └── readme.md 
│
├── ProjectA\
│   └── .git
│
└── ProjectB\
    └── .git
```

---

## Zoho Sheet format

Column headers in `Sheet1` must match exactly:

| SR NO. | DATE | PROJECT NAME | TASK /MODULE | DESCRIPTION | SCREENSHORT | DUE DATE | STATUS |
| ------ | ---- | ------------ | ------------ | ----------- | ----------- | -------- | ------ |

---

## Configuration

### 1. Environment variables (secrets)

Copy the example file and fill in your values:

```bash
copy .env.example .env
```

Required variables in `.env`:

```env
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=
ZOHO_ACCESS_TOKEN=
ZOHO_WORKBOOK_ID=
ZOHO_SHEET_ID=0
ZOHO_ACCOUNTS_URL=https://accounts.zoho.in
ZOHO_SHEET_API_URL=https://sheet.zoho.in/api/v2
ZOHO_REDIRECT_URI=http://localhost:8080/callback
```

- `ZOHO_REFRESH_TOKEN` only needs to be set once (via `get_zoho_token.py`).
- `ZOHO_ACCESS_TOKEN` is refreshed automatically by `zoho_auth.py` and saved back to `.env`.

Never commit `.env`. It is listed in `.gitignore`.

### 2. Project paths and branches (`config.py`)

```python
PROJECTS = {
    "project_a": r"D:\ProjectA",
    "project_b": r"D:\ProjectB"
}

REPORT_BRANCHES = {
    "project_a": ["Nirva", "main"],
    "project_b": ["Nirva"],
}
```

Git activity is only counted from these branches. Local uncommitted changes are only included when you are on one of the allowed branches.

### 3. Cursor history (`config.py`)

Map each project to its **Cursor workspace slug** (folder name under `.cursor\projects\`, e.g. `C:\my-app` → `c-my-app`):

```python
CURSOR_TRANSCRIPTS_ROOT = r"C:\Users\<you>\.cursor\projects"
CURSOR_PROJECTS = {
    "project_a": "c-ProjectA",
    "project_b": "d-ProjectB",
}
```

Transcripts are read from `<CURSOR_TRANSCRIPTS_ROOT>\<slug>\agent-transcripts\`.

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Zoho OAuth setup

1. Create a Zoho API client at [Zoho API Console (India)](https://api-console.zoho.in/).
2. Add scopes: `ZohoSheet.dataAPI.READ`, `ZohoSheet.dataAPI.UPDATE`.
3. Set redirect URI to `http://localhost:8080/callback`.
4. Put `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` in `.env`.
5. Run the token helper (choose one):

**Automatic (recommended)** — opens the browser and saves tokens to `.env`:

```bash
python get_zoho_token.py --auto
```

**Manual** — print the auth URL, approve access, then pass the `code` from the redirect URL:

```bash
python get_zoho_token.py
python get_zoho_token.py <auth_code>
```

Tokens are written to `.env` automatically. After that, `zoho_auth.py` refreshes the access token when it expires and updates `.env` for you.

---

## Cursor MCP configuration

Add to Cursor MCP settings:

```json
{
  "mcpServers": {
    "work-report": {
      "command": "C:\\MCP\\.venv\\Scripts\\python.exe",
      "args": ["C:\\MCP\\server.py"]
    }
  }
}
```

Restart Cursor after saving.

---

## Available tools

| Tool | Description |
| ---- | ----------- |
| `scan_project(project_name, report_date?)` | Full activity for one project (git + Cursor). Date format: `DD/MM/YYYY`. |
| `list_active_projects(report_date?)` | Returns only projects that have activity for the date. |
| `generate_daily_report(project_name, report_date?)` | Prompt to generate TASK_MODULE and DESCRIPTION. Skips if no activity. |
| `get_project_changes(project_name, report_date?)` | Git changes on configured branches only. |
| `get_pending_changes(project_name)` | Current uncommitted changes on the active report branch. |
| `create_report(project_name, task_module, description, status?, report_date?)` | Append a row to Zoho Sheet. Skips if no activity. |

---

## Activity sources

For each project and date, the server checks:

| Source | When included |
| ------ | ------------- |
| Git commits | On configured branches for that date |
| Unpushed commits | On configured branches (today/yesterday) |
| Local changes | Uncommitted work on an allowed branch (today/yesterday) |
| Cursor sessions | Chat transcripts modified on that date |

If none of the above exist, the project is **skipped**.

---

## Recommended workflow

Ask Cursor:

```text
Generate yesterday's report for all active projects and update Zoho Sheet.
```

Cursor should:

1. Call `list_active_projects("DD/MM/YYYY")`.
2. For each active project, call `scan_project()` or `generate_daily_report()`.
3. Write a summary from commits, local changes, and Cursor sessions.
4. Call `create_report()` only for projects with activity.

### Examples

```text
Generate today's report for all projects and update Zoho Sheet.
```

---

## Notes

- Project repos do **not** need to be open in Cursor; paths are read from `config.py`.
- Use **Zoho India** endpoints (`sheet.zoho.in`, `accounts.zoho.in`) for India-region accounts.
- Zoho access tokens expire; the server refreshes them via `zoho_auth.py` and persists the new token to `.env`. If refresh fails, re-run `python get_zoho_token.py --auto`.
- Prefer running reports at end of day or next morning so uncommitted work is still captured.
- One row per project per day when activity exists.
- Spreadsheet rules: append only, never edit or overwrite existing rows.

---

## Git setup

```bash
git init
git add .
git status   # confirm .env is NOT listed
git commit -m "Add Work Report MCP server"
```

On a new machine: copy `.env.example` to `.env` and fill in credentials before running.
