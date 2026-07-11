# AI Coding Assistant Alternatives to Cursor

A reference for tools that capture **development context** — chat history, code suggestions, agent sessions — when building MCP servers, work reports, or activity digests. This repo currently reads **Cursor** transcripts via [cursor_tools.py](cursor_tools.py); use this guide to add other assistants.

**How to use this list**

- Pick assistants your team actually uses.
- Match each tool to an [integration method](#integration-methods) below.
- Prefer read-only, local, date-scoped access first (same pattern as git + Cursor history).
- See [MCP_TOOL_IDEAS.md](MCP_TOOL_IDEAS.md) §20 (AI Usage) and [readme.md](readme.md) for the Cursor implementation.

---

## 1. AI Coding Assistants

These help understand development work — debugging threads, design discussions, and tasks that never become commit messages.

| Tool | Can be used for | Typical integration |
| ---- | --------------- | ------------------- |
| **Cursor** | Chat history, code context, agent transcripts | Local filesystem (implemented in this repo) |
| **GitHub Copilot** | Inline suggestions, Copilot Chat (where available) | IDE extension storage, GitHub API |
| **Claude Desktop** | Conversations, project context | Local app data, Anthropic API |
| **ChatGPT** | Project discussions (if integrated) | OpenAI API, desktop/mobile export |
| **Gemini CLI** | AI interactions from terminal | CLI logs, Google AI API |
| **Continue.dev** | Local AI chat inside VS Code | Local config + session files |
| **Codeium** | AI coding activity, completions | IDE extension, Codeium API |
| **Cline** | Autonomous coding sessions | VS Code workspace storage |
| **Roo Code** | Agent history, multi-mode workflows | VS Code extension storage |
| **Windsurf** | AI coding sessions (Cascade) | Local IDE data (Cursor-like layout) |

### Cursor (current default)

| Aspect | Details |
| ------ | ------- |
| **Data location** | `%USERPROFILE%\.cursor\projects\<workspace-slug>\agent-transcripts\` |
| **Format** | JSONL transcript files |
| **Integration** | Filesystem watcher / date-filtered read |
| **In this repo** | [cursor_tools.py](cursor_tools.py), [config.py](config.py) (`CURSOR_PROJECTS` slug map) |

### GitHub Copilot

| Aspect | Details |
| ------ | ------- |
| **Data location** | VS Code / JetBrains extension storage; GitHub account for Copilot metrics |
| **Format** | Extension-local SQLite/JSON; API for org usage (not full chat text) |
| **Integration** | IDE extension storage, **REST/GraphQL API** (GitHub), log parsing |
| **Notes** | Copilot Chat history is IDE-bound; org admins may use GitHub Copilot usage APIs for aggregate stats, not full transcripts. |

### Claude Desktop

| Aspect | Details |
| ------ | ------- |
| **Data location** | App data directory (OS-specific); optional MCP server connections |
| **Format** | Local conversation store; API for programmatic access |
| **Integration** | Desktop agent file read, **REST API** (Anthropic), MCP |
| **Notes** | Strong fit for MCP-style bridges; Claude Desktop can host MCP servers directly. |

### ChatGPT

| Aspect | Details |
| ------ | ------- |
| **Data location** | OpenAI cloud; optional desktop app local cache |
| **Format** | API JSON; export files (JSON) from account settings |
| **Integration** | **REST API**, export file parsing, browser extension |
| **Notes** | Best for integrated workflows via API; manual export is batch-only, not real-time. |

### Gemini CLI

| Aspect | Details |
| ------ | ------- |
| **Data location** | Terminal session logs; Google AI Studio / Vertex |
| **Format** | CLI stdout logs; API JSON |
| **Integration** | **CLI wrapper** + log parsing, **REST API** (Google AI) |
| **Notes** | Wrap `gemini` invocations or parse shell history for prompt/response pairs. |

### Continue.dev

| Aspect | Details |
| ------ | ------- |
| **Data location** | `~/.continue/` (config, sessions, dev data) |
| **Format** | JSON config; session/history files under Continue data dir |
| **Integration** | **Filesystem watcher**, IDE extension |
| **Notes** | Open-source; local-first — good candidate for transcript-style MCP tools. |

### Codeium

| Aspect | Details |
| ------ | ------- |
| **Data location** | IDE extension cache; Codeium account |
| **Format** | Extension-local storage |
| **Integration** | IDE extension storage, optional **REST API** |
| **Notes** | Windsurf (Codeium IDE) may store Cascade sessions similarly to Cursor. |

### Cline

| Aspect | Details |
| ------ | ------- |
| **Data location** | VS Code workspace / extension global storage |
| **Format** | Task history, conversation logs per workspace |
| **Integration** | **IDE extension** storage, filesystem watcher |
| **Notes** | Autonomous agent tasks produce rich session logs — high value for work reports. |

### Roo Code

| Aspect | Details |
| ------ | ------- |
| **Data location** | VS Code extension storage (`rooveterinaryinc.roo-cline` lineage) |
| **Format** | Agent mode history, chat threads |
| **Integration** | **IDE extension** storage |
| **Notes** | Fork/evolution of Cline; check extension globalStorage path on your OS. |

### Windsurf

| Aspect | Details |
| ------ | ------- |
| **Data location** | Windsurf app data (Codeium IDE; layout similar to Cursor) |
| **Format** | Local session / transcript files (paths vary by version) |
| **Integration** | **Filesystem watcher**, desktop agent |
| **Notes** | Closest Cursor alternative; inspect `%USERPROFILE%\.codeium\` or Windsurf app data for session stores. |

---

## Integration Methods

Not every tool integrates the same way. Generally, use one of these approaches when building MCP tools or work-report collectors.

| Integration method | Examples | Best for |
| ------------------ | -------- | -------- |
| **REST API** | Jira, Slack, GitHub, Zoom, Figma, OpenAI, Anthropic | Cloud-hosted chat, usage metrics, structured exports |
| **GraphQL API** | GitHub, Linear | PR activity, issue context alongside AI sessions |
| **OAuth 2.0** | Google Workspace, Microsoft 365, Slack | User-delegated access to chats, docs, calendar |
| **Webhooks** | GitHub, Stripe, Slack, Jira | Push events when sessions complete or PRs merge |
| **SDKs** | AWS SDK, Azure SDK, Google Cloud SDK | Cloud AI services, enterprise logging |
| **CLI wrappers** | Git, Docker, Kubernetes, Terraform, Gemini CLI | Terminal AI tools, scripted invocations |
| **Log parsing** | CloudTrail, build logs, application logs, shell history | Gemini CLI, custom agent runners |
| **Database queries** | PostgreSQL, MySQL, SQL Server | Teams storing AI audit logs centrally |
| **Browser extensions** | Chrome, Edge, Firefox | ChatGPT web UI, SaaS without API |
| **IDE extensions** | VS Code, IntelliJ, Cursor, Windsurf | Copilot, Continue, Cline, Roo Code |
| **Desktop agents** | Active window, app usage, local file activity | Claude Desktop, Windsurf, Cursor |
| **Filesystem watchers** | Local project and document changes | Cursor transcripts, Continue, Cline task logs |

### Choosing a method by assistant type

| Assistant category | Recommended methods | Why |
| ------------------ | ------------------- | --- |
| **IDE-embedded** (Copilot, Continue, Cline, Roo) | IDE extension storage, filesystem watcher | Sessions stay local; no cloud API for full chat |
| **Standalone IDE** (Cursor, Windsurf) | Filesystem watcher, desktop agent | Transcript folders map cleanly to projects |
| **Desktop chat** (Claude Desktop, ChatGPT app) | Desktop agent, REST API, export parsing | Mix of local cache and cloud API |
| **CLI** (Gemini CLI) | CLI wrapper, log parsing | Capture stdout/stderr or wrap invocations |
| **Cloud-only** (ChatGPT web, Gemini web) | REST API, OAuth, browser extension | No local transcript unless exported |

---

## Mapping assistants → MCP tool ideas

Use these as starting points when extending a Work Report MCP or similar server.

| MCP tool idea | Source assistants | Integration method |
| ------------- | ----------------- | ------------------ |
| `get_chat_sessions(date)` | Cursor, Windsurf, Continue | Filesystem watcher |
| `get_agent_tasks(date)` | Cline, Roo Code | IDE extension storage |
| `get_copilot_activity(date)` | GitHub Copilot | GitHub API + IDE storage |
| `get_cli_ai_log(date)` | Gemini CLI | Log parsing / shell history |
| `get_desktop_conversations(date)` | Claude Desktop, ChatGPT | Desktop agent / API |
| `summarize_ai_work_day(date)` | Any combination above | Merge with git tools (see [readme.md](readme.md)) |

---

## Implementation checklist

When adding a non-Cursor assistant to this repo (or your own MCP server):

1. **Locate data** — Find where the tool stores chats, tasks, or logs on your OS.
2. **Map projects** — Like `CURSOR_PROJECTS` in [config.py](config.py), map repo names → assistant workspace IDs.
3. **Filter by date** — Use file `mtime` or embedded timestamps (same pattern as Cursor transcripts).
4. **Normalize output** — Return a common shape: `{ date, project, user_messages[], assistant_summary }`.
5. **Merge with git** — Combine AI context with commits, diffs, and unpushed work for complete reports.
6. **Stay read-only first** — Avoid write actions until read paths are stable.

---

## Related in this repo

| File | Purpose |
| ---- | ------- |
| [readme.md](readme.md) | Work Report MCP — Cursor + git + Zoho |
| [cursor_tools.py](cursor_tools.py) | Cursor transcript reader (reference implementation) |
| [MCP_TOOL_IDEAS.md](MCP_TOOL_IDEAS.md) | Broader MCP tool brainstorm list |
| [What to include (checklist).md](What%20to%20include%20(checklist).md) | Blog / storytelling checklist |

Contributions welcome: add verified data paths, API links, or MCP server references for any assistant listed above.
