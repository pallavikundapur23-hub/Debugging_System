import asyncio
from pathlib import Path
from typing import Dict, Any
from uuid import uuid4
from app.workflows.remediation_workflow import RemediationWorkflow
from app.utils.logger import get_logger
from app.utils.helpers import now_iso

logger = get_logger("supervisor_agent")

class SupervisorAgent:
    def __init__(
        self,
        clone_url: str,
        repo_name: str,
        issue_details: Dict[str, Any],
        state_manager,
        base_clone_dir: Path,
        github_token: str,
        groq_api_key: str,
        groq_model: str,
    ):
        self.workflow_id = f"wf-{uuid4().hex[:10]}"
        self.clone_url = clone_url
        self.repo_name = repo_name
        self.issue_details = issue_details
        self.state_manager = state_manager
        self.base_clone_dir = base_clone_dir
        self.github_token = github_token
        self.groq_api_key = groq_api_key
        self.groq_model = groq_model
        self.retry_count = 0
        self.max_retries = 2

    async def start(self) -> None:
        self._initialize_state()
        await self._run_workflow()

    def _initialize_state(self) -> None:
        self.state_manager.create_state(self.workflow_id, {
            "workflow_id": self.workflow_id,
            "repo_name": self.repo_name,
            "issue_details": self.issue_details,
            "agent_outputs": {},
            "logs": [],
            "retry_counts": 0,
            "workflow_status": "started",
            "created_at": now_iso(),
            "updated_at": now_iso(),
        })

    async def _run_workflow(self) -> None:
        while self.retry_count <= self.max_retries:
            try:
                workflow = RemediationWorkflow(
                    workflow_id=self.workflow_id,
                    clone_url=self.clone_url,
                    repo_name=self.repo_name,
                    issue_details=self.issue_details,
                    state_manager=self.state_manager,
                    base_clone_dir=self.base_clone_dir,
                    github_token=self.github_token,
                    groq_api_key=self.groq_api_key,
                    groq_model=self.groq_model,
                )
                result = await workflow.execute()
                self.state_manager.update_state(self.workflow_id, {"workflow_status": "completed", "result": result})
                return
            except Exception as exc:
                self.retry_count += 1
                self.state_manager.update_state(self.workflow_id, {
                    "workflow_status": "retrying",
                    "retry_counts": self.retry_count,
                    "last_error": str(exc),
                })
                logger.error("Workflow %s failed on attempt %s: %s", self.workflow_id, self.retry_count, exc)
                if self.retry_count > self.max_retries:
                    self.state_manager.update_state(self.workflow_id, {"workflow_status": "failed"})
                    return
                await asyncio.sleep(2 ** self.retry_count)
