import asyncio
import os
from pathlib import Path
from fastapi import APIRouter, Header, HTTPException, Request
from app.utils.helpers import verify_github_signature, now_iso
from app.state.workflow_manager import WorkflowManager
from app.agents.supervisor_agent import SupervisorAgent
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("github_webhook")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATE_DIR = BASE_DIR / "workflow_state"
CLONE_DIR = Path(os.getenv("BASE_CLONE_DIR", "./repos")).resolve()
workflow_manager = WorkflowManager(STATE_DIR)

@router.post("/webhook/github")
async def github_webhook(request: Request, x_hub_signature_256: str = Header(None), x_github_event: str = Header(None)):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")

    body = await request.body()
    if GITHUB_WEBHOOK_SECRET:
        if not verify_github_signature(GITHUB_WEBHOOK_SECRET, body, x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")
    else:
        logger.warning("No GITHUB_WEBHOOK_SECRET configured; accepting webhook without signature validation")

    payload = await request.json()
    event = x_github_event or payload.get("action")
    repository = payload.get("repository", {})
    repo_name = repository.get("full_name")
    clone_url = repository.get("clone_url")
    if not repo_name or not clone_url:
        raise HTTPException(status_code=400, detail="Missing repository metadata")

    issue_details = {
        "title": "",
        "body": "",
        "text": "",
        "issue_number": 0,
        "event": event,
    }

    if event in {"issues", "issue_labeled", "opened", "labeled"}:
        issue = payload.get("issue", {})
        issue_details.update({
            "title": issue.get("title", ""),
            "body": issue.get("body", ""),
            "text": f"{issue.get('title', '')}\n{issue.get('body', '')}",
            "issue_number": issue.get("number", 0),
        })
    elif event in {"pull_request", "pull_request_review"}:
        pr = payload.get("pull_request", {})
        issue_details.update({
            "title": pr.get("title", ""),
            "body": pr.get("body", ""),
            "text": f"{pr.get('title', '')}\n{pr.get('body', '')}",
            "issue_number": pr.get("number", 0),
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported event {event}")

    supervisor = SupervisorAgent(
        clone_url=clone_url,
        repo_name=repo_name,
        issue_details=issue_details,
        state_manager=workflow_manager,
        base_clone_dir=CLONE_DIR,
        github_token=GITHUB_TOKEN,
        groq_api_key=GROQ_API_KEY,
        groq_model=MODEL_NAME,
    )

    asyncio.create_task(supervisor.start())
    logger.info("Queued workflow %s for repository %s at %s", supervisor.workflow_id, repo_name, now_iso())
    return {"status": "accepted", "workflow_id": supervisor.workflow_id}
