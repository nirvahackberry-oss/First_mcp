# Work Report MCP — Blog Content (Ready to Publish)

Use this file for Medium and LinkedIn. Replace `[GITHUB_REPO_URL]` and `[README_URL]` before publishing.

---

## Publishing checklist

- [ ] Add GitHub repo link
- [ ] Add 3 screenshots (Cursor prompt, MCP tools, Zoho Sheet row)
- [ ] Redact any sensitive project paths or sheet data
- [ ] Confirm `.env` is not visible in screenshots
- [ ] Post Medium first, then LinkedIn with link in first comment

**Suggested Medium tags:** `Cursor`, `MCP`, `Developer Tools`, `Productivity`, `Python`, `Automation`, `Git`, `Zoho`

**Suggested posting time:** Tuesday–Thursday, 8–10 AM IST

---

# MEDIUM POST

## Title options (pick one)

1. **I Stopped Writing Daily Work Reports Manually — Here's My Cursor MCP Setup** *(recommended)*
2. From Git Commits to Zoho Sheet: Automating Daily Reports with MCP
3. Building a Work Report MCP: When Cursor Becomes Your Reporting Assistant

## Subtitle

How I combined git activity, Cursor chat history, and Zoho Sheets into a one-prompt daily workflow.

---

## The problem: end-of-day reporting is harder than the work itself

Every evening, the same question comes up: *What did I actually work on today?*

When you juggle multiple repositories, the answer is never in one place. Some work is committed. Some is still sitting locally. Some only exists in Cursor chat threads. And then you still have to open a spreadsheet and write it up in the format your team expects.

I got tired of that loop — so I built a **Work Report MCP** that turns daily reporting into a one-sentence task inside Cursor.

---

## The real problem isn't writing — it's collecting evidence

Most "daily report automation" fails because it only looks at git commits.

But real developer work often looks like this:

- Commits on a feature branch that isn't pushed yet
- Uncommitted changes you'll commit tomorrow
- Debugging and design discussions inside Cursor that never become a commit message

If your tool ignores those signals, your report is incomplete — or worse, inaccurate.

---

## What MCP does (and doesn't do)

Before the build details, one important clarification:

**MCP is not a scheduler.** It doesn't run in the background or watch your repositories.

**MCP is a toolkit Cursor can call.**

| Component | Role |
| --------- | ---- |
| MCP server | Hands — fetch git data, read transcripts, append a sheet row |
| Cursor (LLM) | Brain — summarize work in professional language |
| You | Trigger — one natural-language prompt |

That separation is what makes this practical. MCP provides **data and actions**. Cursor does the thinking. You decide when to run a report.

---

## What Work Report MCP does

For any given date, the server:

1. Scans configured projects for activity
2. Collects evidence from **git** and **Cursor chat history**
3. Lets Cursor generate `TASK / MODULE` and `DESCRIPTION`
4. Appends a new row to **Zoho Sheet** (append-only — never overwrites existing rows)

Projects with **no activity are skipped**. No empty rows. No fake productivity.

---

## Architecture

```text
You (in Cursor)
    ↓  natural language prompt
Cursor LLM
    ↓  MCP tool calls
Work Report MCP
    ├── git_tools.py       → commits, diffs, unpushed work
    ├── cursor_tools.py    → chat transcripts
    ├── report_generator.py → combines activity sources
    └── excel_tools.py     → Zoho Sheet API (append row)
    ↓
Zoho Sheet (daily task log)
```

Stack: **Python**, **FastMCP**, **requests**, **python-dotenv**, **Zoho Sheet API**.

---

## Where the data comes from

| Source | When included | Why it matters |
| ------ | ------------- | -------------- |
| Git commits | On configured branches for that date | What actually landed in version control |
| Unpushed commits | On configured branches (today/yesterday) | Work done but not on remote yet |
| Local changes | Uncommitted work on an allowed branch (today/yesterday) | WIP that commit history won't show |
| Cursor sessions | Chat transcripts modified on that date | Context, debugging, and decisions that never became a commit |

Git activity is limited to **report branches per project** (for example `Nirva`, `main`, or `dev_nirva`). That keeps unrelated branch noise out of your daily log.

Cursor transcripts are read from your local workspace folder under `.cursor/projects/<workspace-slug>/agent-transcripts/`.

---

## The workflow in one prompt

At the end of the day (or the next morning), I ask Cursor:

```text
Generate yesterday's report for all active projects and update Zoho Sheet.
```

Behind the scenes, Cursor calls MCP tools in sequence:

1. **`list_active_projects`** — returns only projects with real activity for the date
2. **`scan_project`** or **`generate_daily_report`** — gathers git + Cursor evidence and builds a summary prompt
3. **`create_report`** — appends the final row to Zoho Sheet

From my side, it feels like one command.

### Other useful tools

| Tool | Purpose |
| ---- | ------- |
| `get_project_changes` | Git changes on configured branches only |
| `get_pending_changes` | Current uncommitted work on the active report branch |

---

## Zoho Sheet integration

Reports append to a fixed Zoho Sheet template. Column headers in `Sheet1` must match exactly:

| SR NO. | DATE | PROJECT NAME | TASK /MODULE | DESCRIPTION | SCREENSHORT | DUE DATE | STATUS |
| ------ | ---- | ------------ | ------------ | ----------- | ----------- | -------- | ------ |

### Spreadsheet rules (built into the tool)

- Never modify workbook layout or formatting
- Never overwrite or edit existing report rows
- Always append a new row at the end
- Only write the provided values into the new row

### OAuth and token handling

Zoho setup is a one-time process:

```bash
python get_zoho_token.py --auto
```

This opens the browser, captures the OAuth callback, and saves tokens to `.env` automatically.

After that, `zoho_auth.py` refreshes the access token when it expires and persists the new token back to `.env`. No manual copy-paste every hour.

---

## Example outcome

**Before:** 20–30 minutes reconstructing the day from git logs, IDE tabs, and memory.

**After:** ~2 minutes reviewing AI-generated summaries and confirming sheet updates.

The summary is still human-readable and professional — because Cursor writes it from actual activity, not guesswork.

### Sample prompt output (illustrative)

**Project:** vlab  
**TASK / MODULE:** Enhanced DBMS lab support and Docker configuration  
**DESCRIPTION:** Updated MySQL/Postgres init scripts, DBMS Dockerfile and start flow, shared lab_server changes, deploy workflow, and Terraform variables. Improved Big Data lab with Hadoop core/hdfs config, sample sales data, and frontend compute Editor changes.

*(Redact or replace with your own real examples before publishing.)*

---

## What I learned building this

1. **MCP shines when it exposes domain actions**, not generic wrappers. Specific tools like `list_active_projects` and `create_report` are more useful than one vague "do everything" function.

2. **Reporting quality depends on input quality.** Git + Cursor history beats commits alone.

3. **Guardrails matter.** Branch filters, skip-no-activity logic, and append-only sheet rules prevent bad data from entering your log.

4. **Developer ergonomics matter.** One prompt beats a six-step script you'll stop using after a week.

5. **MCP doesn't replace judgment.** I still review summaries before treating them as final — the server handles evidence collection and sheet updates, not blind trust.

---

## Limitations (on purpose)

- You still trigger reports manually — by design. MCP is not a cron job.
- Initial setup takes time: project paths, branch rules, Cursor workspace slug mapping, Zoho OAuth.
- LLM wording can vary; review before finalizing important reports.
- Zoho India endpoints (`sheet.zoho.in`, `accounts.zoho.in`) are configured for India-region accounts.

---

## Quick setup summary

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python get_zoho_token.py --auto
```

Configure `config.py` with your project paths, report branches, and Cursor workspace slugs. Add the MCP server to Cursor settings:

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

Full setup guide: [README_URL]  
Source code: [GITHUB_REPO_URL]

---

## What's next

Possible extensions I'm considering:

- Google Sheets support alongside Zoho
- A weekly rollup report across all projects
- Optional screenshot attachment column automation

---

## Closing

If you use Cursor daily and maintain a work log spreadsheet, this pattern is very reusable. MCP doesn't need to be a demo — it can remove real friction from your day.

**What's your daily reporting workflow?** Do you log by project, by task, or in a weekly batch? I'd love to compare approaches in the comments.

---

# LINKEDIN POST (short version)

Copy-paste and adapt. Put the Medium link in the **first comment**, not the main post body.

---

I used to spend 20–30 minutes every evening trying to remember what I worked on across multiple repos.

Commits told part of the story.
Unpushed work told another.
Cursor chats had the rest.

So I built a **Work Report MCP** in Cursor.

One prompt:
> "Generate yesterday's report for all active projects and update Zoho Sheet."

What happens behind the scenes:
→ MCP scans git activity (commits, local changes, unpushed work)
→ Reads Cursor chat transcripts for that day
→ Cursor writes a professional TASK + DESCRIPTION summary
→ Appends a row to Zoho Sheet (append-only, no overwrite)
→ Skips projects with zero activity

Key idea: **MCP doesn't think — it gives Cursor real evidence.**
Cursor does the writing. I just trigger it.

Built with Python + FastMCP + Zoho Sheet API.

If you're experimenting with MCP beyond toy demos, this is the kind of workflow that actually saves time.

Full breakdown (architecture, setup, lessons learned): [link in first comment]

#Cursor #MCP #DeveloperProductivity #Python #Automation #Git #BuildInPublic #Zoho

---

## LINKEDIN FIRST COMMENT (template)

Full article with architecture diagram, setup steps, and lessons learned:
[Medium article URL]

GitHub repo:
[GITHUB_REPO_URL]

---

# LINKEDIN CAROUSEL (optional — 6 slides)

**Slide 1 — Hook**
Daily work reports are painful.
Not because writing is hard — because remembering is hard.

**Slide 2 — The gap**
Commits ≠ full story.
Unpushed code and Cursor chats hold the rest.

**Slide 3 — Architecture**
You → Cursor → MCP → Zoho Sheet
MCP = hands. Cursor = brain.

**Slide 4 — Data sources**
✓ Git commits (branch-filtered)
✓ Unpushed commits
✓ Local uncommitted changes
✓ Cursor chat transcripts

**Slide 5 — One prompt**
"Generate yesterday's report for all active projects and update Zoho Sheet."

**Slide 6 — CTA**
Built with Python + FastMCP.
Repo in comments. Full write-up on Medium.

---

# VISUAL ASSETS TO CREATE

| # | Screenshot | Purpose |
| - | ---------- | ------- |
| 1 | Cursor chat with the one-line prompt | Hero image for Medium + LinkedIn |
| 2 | MCP tools list in Cursor settings | Shows real integration |
| 3 | Zoho Sheet with a new appended row | Proves end-to-end result |
| 4 | Architecture diagram | Optional; use the ASCII diagram above as a starting point |

**Screenshot rules:** Redact paths, tokens, client names, and any sensitive sheet data.

---

# POSTING STRATEGY

**Medium**
- Publish Tuesday–Thursday morning (IST 8–10 AM)
- Add hero image + 2 in-article screenshots
- Pin repo link near the top and bottom of the article

**LinkedIn**
- Post the short version natively (don't only drop a Medium link)
- Put Medium link in the first comment
- Reply to early comments quickly to boost reach
- Tag sparingly; 5–7 relevant hashtags is enough

**Credibility boosters**
- Include one real (redacted) before/after report row
- Mention one problem you solved (token refresh, branch noise, empty rows)
- State time saved as a concrete number (e.g. 20–30 min → ~2 min)
