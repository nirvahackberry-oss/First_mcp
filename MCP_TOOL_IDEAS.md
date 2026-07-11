# MCP Tool Ideas

A reference list of data sources and actions you can expose as [Model Context Protocol (MCP)](https://modelcontextprotocol.io) tools. Use it to brainstorm your own servers — each bullet is a potential tool, resource, or prompt surface for an AI assistant.

**How to use this list**

- Pick a category that matches your workflow or team.
- Start with 2–3 high-value tools (read-only first, then actions).
- Combine related signals (e.g. git diff + PR status + CI result) into one “activity summary” tool.
- See this repo’s [Work Report MCP](readme.md) for a real example: git activity + Cursor history → structured report.

---

## 1. Software Development

### IDE

- Get opened files
- Get recently edited files
- Get Cursor chat history
- Get VS Code history
- Get code changes
- Get uncommitted changes
- Get Git diff
- Get recent commits
- Get branch history
- Detect active project
- Detect programming language
- Detect TODO comments

### Git

- Commit history
- Pull requests
- Merged PRs
- Reviews
- Repository activity
- Branches
- Releases
- Tags

### Terminal

- Command history
- Build commands
- Test commands
- Docker commands
- Kubernetes commands
- Terraform commands
- SSH history

### CI/CD

- GitHub Actions
- Jenkins
- Azure DevOps
- GitLab Pipelines
- CircleCI
- Build failures
- Deployment history

### Package managers

- npm
- pip
- Maven
- Gradle
- NuGet
- Cargo

---

## 2. DevOps / Cloud Engineering

### AWS

- CloudTrail activity
- ECS deployments
- EC2 lifecycle
- Lambda updates
- CloudFormation stacks
- Terraform changes
- IAM modifications
- S3 uploads
- RDS modifications
- Route53 updates
- Auto Scaling changes
- CloudWatch alarms

### Azure

- Resource deployments
- AKS activity
- Azure Monitor
- Azure DevOps

### Google Cloud

- Cloud Build
- GKE
- Cloud Run
- IAM
- Storage

### Kubernetes

- Pod logs
- Deployment history
- Scaling
- Events
- ConfigMaps
- Secrets
- Services
- Helm releases

### Docker

- Images built
- Containers started
- Registry pushes
- Compose history

---

## 3. QA / Testing

- TestRail
- Playwright
- Cypress
- Selenium
- Postman
- Newman
- JMeter
- BrowserStack
- Bug reports
- Failed tests
- Passed tests

---

## 4. Project Management

### Jira

- Issues worked
- Comments
- Worklogs
- Sprint changes
- Status changes
- Boards
- Epics

### Azure Boards

- Tasks
- Bugs
- Stories

### ClickUp

- Tasks
- Comments
- Time entries

### Asana

- Assigned work
- Completed work

### Trello

- Card movements

---

## 5. Meetings

### Google Calendar

- Events
- Attendees
- Duration

### Google Meet

- Recording
- Transcript
- Chat
- Attendance

### Zoom

- Transcript
- Participants
- Recording
- Summary

### Microsoft Teams

- Meeting
- Recording
- Transcript
- Attendance

---

## 6. Communication

### Slack

- Messages
- Threads
- Mentions
- Calls
- Huddles
- Channels

### Microsoft Teams Chat

- Chats
- Files

### Discord

- Messages
- Threads

### Email

- Gmail
- Outlook

---

## 7. Documentation

### Notion

- Edited pages
- Created pages
- Comments

### Confluence

- Page edits
- New documents

### Google Docs

- Changes
- Comments

### Microsoft Word

- Recent edits

---

## 8. UI/UX

### Figma

- Edited files
- Comments
- Components
- Prototypes

### Adobe

- Photoshop
- Illustrator
- XD

---

## 9. Data Engineering

- Airflow
- dbt
- Snowflake
- BigQuery
- Databricks
- Spark
- Kafka
- Redshift

---

## 10. Data Science / AI

- Jupyter
- MLflow
- Weights & Biases
- Hugging Face
- OpenAI
- Bedrock
- SageMaker
- Vertex AI

---

## 11. Security

- Splunk
- CrowdStrike
- Defender
- SIEM
- WAF
- GuardDuty
- Security Hub

---

## 12. Sales

- Salesforce
- HubSpot
- Zoho CRM
- Calls
- Emails
- Meetings
- LinkedIn

---

## 13. HR

- BambooHR
- Workday
- Leave requests
- Attendance
- Recruitment

---

## 14. Finance

- QuickBooks
- Xero
- SAP
- Oracle Finance

---

## 15. Customer Support

- Zendesk
- Freshdesk
- Intercom
- ServiceNow

---

## 16. Browser Activity

- Active tab
- URL history
- Downloads
- Uploads
- Time spent

---

## 17. Operating System

- Active applications
- Window titles
- File edits
- Clipboard history
- Notifications

---

## 18. Productivity

- Pomodoro
- RescueTime
- Clockify
- Toggl

---

## 19. Knowledge Search

- Google Drive
- OneDrive
- Dropbox
- SharePoint
- Local files

---

## 20. AI Usage

- Cursor chats
- Claude
- ChatGPT
- GitHub Copilot
- Gemini
- Perplexity

---

## Quick-start patterns

| Pattern | Example | Why it works |
| ------- | ------- | ------------ |
| **Activity digest** | “What did I ship yesterday?” across git, Jira, and Slack | One natural-language question, many backends |
| **Evidence bundle** | Commits + diff + PR + CI status for a branch | LLM writes accurate summaries from facts |
| **Append-only write** | Add row to sheet/CRM, never overwrite | Safe for production automations |
| **Date-scoped scan** | Filter all tools by `YYYY-MM-DD` | Matches daily standups and reports |
| **Project detection** | Infer repo from cwd or open files | Less config for the user |

---

## Related in this repo

| File | Purpose |
| ---- | ------- |
| [readme.md](readme.md) | Work Report MCP — git, Cursor, Zoho Sheet |
| [What to include (checklist).md](What%20to%20include%20(checklist).md) | Blog / storytelling checklist for MCP projects |
| [BLOG.md](BLOG.md) | Draft blog content |

Contributions welcome: add categories, link to existing MCP servers, or note APIs that make each idea practical.
