What to include (checklist)

1\. Hook — the pain everyone recognizes

Start with the daily reporting problem, not the tech:

* End-of-day scramble to remember what you did
* Work spread across multiple repos
* Uncommitted / unpushed work that never shows up in commit history
* Copy-pasting into a spreadsheet manually
* 

2\. The insight — MCP is not automation, it’s a bridge

This is your differentiator. Many people misunderstand MCP. Explain clearly:



Role		|What it does

MCP server	|Provides data + actions (git, Cursor history, Zoho append)

Cursor (LLM)	|Reads activity, writes the human summary

You		|One sentence in chat: “Generate yesterday’s report…”



MCP does not schedule jobs or watch folders. You trigger it when you want.



3\. What you built — outcome first, then how

Lead with the result:



“I built a Work Report MCP that scans my projects, pulls real work evidence, and appends a row to Zoho Sheet — only when there was actual activity.”



Then the 4-step flow:

1. Scan configured projects for a date
2. Pull git + Cursor chat activity
3. Let Cursor write TASK / MODULE + DESCRIPTION
4. Append to Zoho Sheet (never overwrite)



4\. Why this approach is smarter than “just ask ChatGPT”

* Evidence-based: commits, diffs, unpushed work, Cursor transcripts
* Branch-aware: only counts work on configured branches
* Skips empty days: no fake rows
* Safe spreadsheet rules: append-only, preserves formatting
* Multi-project: one command for all active repos



5\. Architecture (simple diagram)

Use a mermaid or simple ASCII in Medium:



You (in Cursor)

&#x20;   ↓ natural language

Cursor LLM

&#x20;   ↓ MCP tool calls

Work Report MCP

&#x20;   ├── git\_tools.py      → commits, diffs, unpushed

&#x20;   ├── cursor\_tools.py   → chat transcripts

&#x20;   └── excel\_tools.py    → Zoho Sheet API

&#x20;   ↓

Zoho Sheet (daily task log)



6\. Demo moment — the “wow” section

Show one real prompt and what happens:



Generate yesterday's report for all active projects and update Zoho Sheet.

Walk through:

1. list\_active\_projects → only projects with activity
2. scan\_project / generate\_daily\_report per project
3. Cursor writes professional summary
4. create\_report appends row

This is the most shareable part — make it concrete.



7\. Technical highlights (for dev audience)

Pick 3–4, not everything:

* Python + FastMCP — lightweight MCP server
* Git intelligence — branch filtering, local changes, unpushed commits
* Cursor transcript parsing — reads agent-transcripts by workspace slug
* Zoho OAuth — get\_zoho\_token.py --auto, auto token refresh via zoho\_auth.py
* Config-driven — config.py for paths/branches, .env for secrets



8\. Limitations (builds trust)

Be honest:

* Not a cron job — you still trigger it
* Needs one-time Zoho + MCP setup
* Cursor slug mapping must match your workspace folders
* Summary quality depends on the LLM (MCP only supplies data)



9\. Who this is for

* Developers on multiple projects
* Teams that log daily work in spreadsheets
* Cursor users who want practical MCP, not toy demos



10\. CTA

* Link to GitHub repo (if public)
* “Comment if you want a Google Sheets version”
* “Follow for more Cursor + MCP builds”





**Medium post structure (recommended)**

Title options (pick one):

1. I Stopped Writing Daily Work Reports Manually — Here’s My Cursor MCP Setup
2. From Git Commits to Zoho Sheet: Automating Daily Reports with MCP
3. Building a Work Report MCP: When Cursor Becomes Your Reporting Assistant



Subtitle:

How I combined git activity, Cursor chat history, and Zoho Sheets into a one-prompt daily workflow.



Sections (\~8–12 min read):

1. The problem (short story)
2. What MCP actually is (1 minute clarity)
3. My solution overview
4. Data sources (git + Cursor + why both matter)
5. How a report run works (step by step)
6. Zoho integration + token handling
7. Sample output (before/after)
8. What I’d improve next
9. Try it yourself (setup summary + repo link)



Medium tags: Cursor, MCP, Developer Tools, Productivity, Python, Automation, Git, Zoho

Visuals to add (high impact):

* Screenshot: Cursor chat with the one-liner prompt
* Screenshot: Zoho Sheet row after append
* Screenshot: MCP tools list in Cursor
* Optional: simple architecture diagram



**Medium draft (copy and personalize)**



##### **I Stopped Writing Daily Work Reports Manually — Here’s My Cursor MCP Setup**

Every evening, the same question: What did I actually work on today?



When you juggle multiple repos, the answer is never in one place. Some work is committed. Some is still local. Some only exists in Cursor chat threads. And then you still have to open a spreadsheet and write it up in a format your team expects.



I got tired of that loop — so I built a Work Report MCP that turns daily reporting into a one-sentence task inside Cursor.



##### **The real problem isn’t writing — it’s collecting evidence**

Most “daily report automation” fails because it only looks at git commits.



But real developer work often looks like this:

* commits on a feature branch that isn’t pushed yet
* uncommitted changes you’ll commit tomorrow
* debugging and design discussions inside Cursor

If your tool ignores those signals, your report is incomplete — or worse, inaccurate.



##### **What MCP does (and doesn’t do)**

Before the build details, one important clarification:



**MCP is not a scheduler.**

It doesn’t run in the background or watch your repos.



**MCP is a toolkit Cursor can call.**

* MCP server = hands (fetch git data, read transcripts, append sheet row)
* Cursor = brain (summarize work in professional language)
* You = trigger (“generate yesterday’s report for all active projects”)

That separation is what makes this practical.



##### **What my Work Report MCP does**

For any given date, it:

1. Scans configured projects
2. Collects activity from git and Cursor chat history
3. Lets Cursor generate TASK / MODULE and DESCRIPTION
4. Appends a new row to Zoho Sheet (append-only — never overwrites existing rows)

Projects with no activity are skipped. No empty rows. No fake productivity.



##### **Where the data comes from**

Source				Why it matters

Git commits			What shipped on report branches

Unpushed commits		Work done but not on remote yet

Local uncommitted changes	Today/yesterday WIP on allowed branches

Cursor transcripts		Context that never made it to a commit message

I also configured branch rules per project, so noise from unrelated branches doesn’t pollute the report.



##### **The workflow in one prompt**

At the end of the day (or next morning), I ask Cursor:



***Generate yesterday's report for all active projects and update Zoho Sheet.***

Behind the scenes, Cursor uses MCP tools like:

* list\_active\_projects — only projects with real activity
* scan\_project / generate\_daily\_report — gather evidence + build summary prompt
* create\_report — append the final row to Zoho Sheet

From my side, it feels like one command.



##### Zoho Sheet integration (with sane auth)



Reports go to a fixed Zoho Sheet template with columns like:

SR NO. | DATE | PROJECT NAME | TASK /MODULE | DESCRIPTION | SCREENSHORT | DUE DATE | STATUS

The integration includes:

* OAuth setup via get\_zoho\_token.py --auto
* automatic access-token refresh (zoho\_auth.py)
* safe append behavior (new row only)

So I’m not manually editing tokens or risking overwrite of old records.

###### 

###### **Example outcome**

**Before**: 20–30 minutes reconstructing the day from git logs, tabs, and memory.

**After**: \~2 minutes reviewing AI-generated summaries and confirming sheet updates.



The summary is still human-readable and professional — because Cursor writes it from actual activity, not guesswork.



##### **What I learned building this**

1. MCP shines when it exposes domain actions, not generic wrappers.
2. Reporting quality depends on input quality — git + Cursor history beats commits alone.
3. Guardrails matter (branch filters, skip-no-activity, append-only sheet rules).
4. Developer ergonomics matter — one prompt beats a 6-step script.



##### **Limitations (on purpose)**

* You still trigger reports manually (by design).
* Initial setup takes time: project paths, Cursor slug mapping, Zoho OAuth.
* LLM wording can vary; I review before finalizing.



##### **Try it yourself**

If you use Cursor daily and maintain a work log spreadsheet, this pattern is very reusable.



Stack:

* Python + FastMCP
* Git + Cursor transcript readers
* Zoho Sheet API

Repo: \[add your GitHub link]

Setup guide: \[link to readme]

If you want, I can share a Google Sheets variant or a team template in a follow-up post.



**What’s your daily reporting workflow?**

Do you log by project, by task, or end-of-week batch? I’d love to compare approaches.



##### **LinkedIn post (short version)**

Use this as the post itself; link Medium in the first comment if you want reach + readability.



I used to spend 20–30 minutes every evening trying to remember what I worked on across multiple repos.

Commits told part of the story.

Unpushed work told another.

Cursor chats had the rest.

So I built a Work Report MCP in Cursor.



One prompt:



***“Generate yesterday’s report for all active projects and update Zoho Sheet.”***



What happens behind the scenes:

* MCP scans git activity (commits, local changes, unpushed work)
* Reads Cursor chat transcripts for that day
* Cursor writes a professional TASK + DESCRIPTION summary
* Appends a row to Zoho Sheet (append-only, no overwrite)
* Skips projects with zero activity



Key idea: **MCP doesn’t think — it gives Cursor real evidence.**

Cursor does the writing. I just trigger it.



Built with Python + FastMCP + Zoho API.



If you’re experimenting with MCP beyond toy demos, this is the kind of workflow that actually saves time.



Full breakdown (architecture, setup, lessons): \[Medium link]

\#Cursor #MCP #DeveloperProductivity #Python #Automation #Git #BuildInPublic



**LinkedIn carousel idea (optional, 6 slides)**

1. Problem: “Daily reports are painful”
2. Insight: “Commits ≠ full story”
3. Architecture: You → Cursor → MCP → Zoho
4. Data sources: Git + Cursor transcripts
5. One prompt workflow
6. Result + CTA: “Repo in comments”



**Posting strategy**



**Medium**

* Publish on Tuesday–Thursday morning (IST 8–10 AM works well for tech audience)
* Add 1 hero image + 2 in-article screenshots
* Pin the GitHub/readme link near the top and bottom



**LinkedIn**

* Post the short version natively (don’t only drop a Medium link)
* Put Medium link in first comment
* Reply to early comments quickly (boosts reach)
* Tag sparingly: #Cursor #MCP #Python #BuildInPublic



**Credibility boosters**

* Include 1 real (redacted) report row before/after
* Mention one failure you solved (e.g., token refresh, branch noise)
* Add “time saved” as a concrete number



**What to avoid**

* Don’t open with “MCP stands for Model Context Protocol…” — hook with the pain
* Don’t dump full setup steps in LinkedIn — save that for Medium
* Don’t oversell as “fully automated” — you trigger it manually
* Don’t post secrets/screenshots with .env values

