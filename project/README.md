# Autonomous GitHub Issue Remediation System

A lightweight Python-based autonomous multi-agent workflow for GitHub issue remediation.

## Overview

This project receives GitHub webhook events, clones repositories, analyzes code, performs research, generates fixes, validates them, and creates PRs/comments automatically.

## Architecture

- `app/main.py` — FastAPI entrypoint
- `app/webhook/github_webhook.py` — GitHub webhook listener
- `app/agents/` — specialized agents orchestrating tasks
- `app/tools/` — reusable integrations for Groq, GitHub, repo cloning, file scanning, web search, patch writing, command execution
- `app/workflows/remediation_workflow.py` — workflow orchestration
- `app/state/workflow_manager.py` — local JSON workflow persistence
- `workflow_state/` — stored workflow reports
- `repos/` — cloned repositories
- `logs/` — workflow logs

## Setup

1. Clone this repository.
2. Create a Python 3.11 virtual environment.
3. Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and set your secrets.

## Environment Variables

```text
GROQ_API_KEY=
MODEL_NAME=llama-3.1-8b-instant
GITHUB_TOKEN=
GITHUB_WEBHOOK_SECRET=
TAVILY_API_KEY=
BASE_CLONE_DIR=./repos
```

## Run Locally

```bash
cd project
uvicorn app.main:app --reload
```

## GitHub Webhook Setup

- Configure your repository webhook to POST to `/webhook/github`
- Use `application/json`
- Set the secret to match `GITHUB_WEBHOOK_SECRET`
- Subscribe to `issues` and `pull_request` events

## Example Workflow

1. GitHub issue opened or labeled
2. FastAPI receives webhook
3. Background workflow starts
4. Repository clones into `repos/`
5. Agents analyze files and issue text
6. Patch is generated and written to disk
7. PR/comment created on GitHub
8. Workflow state saved under `workflow_state/`

## Agents

- `SupervisorAgent` — workflow control and retries
- `RepoMapAgent` — repository structure analysis
- `PlannerAgent` — remediation strategy and file selection
- `ResearchAgent` — live web search references
- `CodeSearchAgent` — local code search for relevant paths
- `PatchAgent` — generate and apply fixes
- `ValidationAgent` — execute tests or linting
- `VerifierAgent` — confirm patch quality and issue match

## Notes

- No database used
- No Docker Compose, Redis, or vector database
- Uses local JSON workflow state
- Uses Groq LLM via API only
- Uses GitHub REST API for PRs and comments

## Demo Tips

- Open a new issue in a repository configured with this webhook
- Confirm the FastAPI server accepts the event immediately
- Watch `workflow_state/` for generated JSON summaries
- Inspect `logs/workflow.log` for agent progress
