import asyncio
from pathlib import Path
from typing import Dict, Any
from app.tools.repo_clone_tool import RepoCloneTool
from app.tools.file_reader_tool import FileReaderTool
from app.tools.patch_writer_tool import PatchWriterTool
from app.tools.command_executor_tool import CommandExecutorTool
from app.tools.github_tool import GitHubTool
from app.tools.web_search_tool import WebSearchTool
from app.tools.groq_client import GroqClient
from app.agents.repo_map_agent import RepoMapAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.code_search_agent import CodeSearchAgent
from app.agents.patch_agent import PatchAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.verifier_agent import VerifierAgent
from app.utils.helpers import now_iso
from app.utils.logger import get_logger

logger = get_logger("remediation_workflow")

class RemediationWorkflow:
    def __init__(
        self,
        workflow_id: str,
        clone_url: str,
        repo_name: str,
        issue_details: Dict[str, Any],
        state_manager,
        base_clone_dir: Path,
        github_token: str,
        groq_api_key: str,
        groq_model: str,
    ):
        self.workflow_id = workflow_id
        self.clone_url = clone_url
        self.repo_name = repo_name
        self.issue_details = issue_details
        self.state_manager = state_manager
        self.clone_tool = RepoCloneTool(base_clone_dir, github_token)
        self.github_tool = GitHubTool(github_token)
        self.groq_client = GroqClient(groq_api_key, groq_model)
        self.workflow_state = {}

    async def execute(self) -> Dict[str, Any]:
        self._log_step("starting workflow")
        repo_dir = self.clone_tool.clone_repository(self.clone_url, self.repo_name)
        self.state_manager.update_state(self.workflow_id, {"repo_dir": str(repo_dir), "status": "cloned", "cloned_at": now_iso()})

        repo_map = await RepoMapAgent(repo_dir, self.groq_client).analyze_repository()
        self.state_manager.update_state(self.workflow_id, {"repo_summary": repo_map})

        plan = await PlannerAgent(self.groq_client).create_plan(self.issue_details, repo_map)
        self.state_manager.update_state(self.workflow_id, {"plan": plan})

        research_task = ResearchAgent(self.groq_client, WebSearchTool()).research(plan["issue_summary"])
        code_search_task = CodeSearchAgent(repo_dir).search(self.issue_details["text"], plan["selected_files"])
        research_results, code_results = await asyncio.gather(research_task, code_search_task)
        self.state_manager.update_state(self.workflow_id, {"research": research_results, "code_search": code_results})

        patch_result = await PatchAgent(self.groq_client, repo_dir, self.issue_details).generate_and_apply(
            repo_map, plan, code_results, research_results
        )
        self.state_manager.update_state(self.workflow_id, {"patch_result": patch_result})

        validation_result = await ValidationAgent(repo_dir).validate()
        self.state_manager.update_state(self.workflow_id, {"validation": validation_result})

        verification_result = await VerifierAgent(self.groq_client).verify(
            self.issue_details, patch_result, validation_result
        )
        self.state_manager.update_state(self.workflow_id, {"verification": verification_result})

        if patch_result.get("patched") and validation_result.get("status") == "success":
            branch_name = f"autofix/{self.workflow_id}".replace("/", "-")
            self.clone_tool.create_branch(repo_dir, branch_name)
            self._commit_and_push(repo_dir, branch_name)

            owner, repo = self.repo_name.split("/")
            pr = await self.github_tool.create_pull_request(
                owner=owner,
                repo=repo,
                head=branch_name,
                base="main",
                title=f"Autonomous fix: {self.issue_details.get('title', 'issue remediation')}"[:120],
                body=self._build_pr_body(patch_result, validation_result, verification_result),
            )
            self.state_manager.update_state(self.workflow_id, {"pull_request": pr})
            issue_number = self.issue_details.get("issue_number", 0)
            if issue_number and issue_number > 0:
                await self.github_tool.create_comment(owner, repo, issue_number, verification_result.get("summary", "Fix completed."))
                self.state_manager.update_state(self.workflow_id, {"commented": True})

        result = {
            "workflow_id": self.workflow_id,
            "repo_name": self.repo_name,
            "status": "completed",
            "completed_at": now_iso(),
        }
        self.state_manager.update_state(self.workflow_id, result)
        self._log_step("workflow completed")
        await self.groq_client.close()
        return result

    def _commit_and_push(self, repo_dir: Path, branch_name: str) -> None:
        self.clone_tool.commit_changes(repo_dir, f"Autonomous remediation for {self.issue_details.get('title')}")
        self.clone_tool.push_branch(repo_dir, branch_name)

    def _build_pr_body(
        self,
        patch_result: Dict[str, Any],
        validation_result: Dict[str, Any],
        verification_result: Dict[str, Any],
    ) -> str:
        summary = patch_result.get("summary", "").strip()
        if summary:
            summary = summary.splitlines()[0]

        files_changed = sorted(patch_result.get("patches", {}).keys())
        file_notes = patch_result.get("file_notes", {}) or {}
        if files_changed:
            file_lines = []
            for path in files_changed:
                reason = file_notes.get(path)
                if not reason:
                    reason = "Applied automated remediation changes to this file."
                file_lines.append(f"- `{path}` — {reason}")
            file_section = "\n".join(file_lines)
        else:
            file_section = "- No file changes detected"

        validation_status = validation_result.get("status", "unknown")
        validation_lines = [f"- **Status:** {validation_status}"]
        for result in validation_result.get("results", [])[:3]:
            command = result.get("command") or result.get("name") or "command"
            status = result.get("status", "unknown")
            validation_lines.append(f"  - `{command}` → {status}")

        verification = verification_result.get("summary", "No verification summary available.").strip()

        return (
            f"### Summary\n"
            f"{summary or 'This patch applies an automated remediation generated by the workflow.'}\n\n"
            f"### Files changed\n"
            f"{file_section}\n\n"
            f"### Validation\n"
            f"{chr(10).join(validation_lines)}\n\n"
            f"### Verification\n"
            f"{verification}\n\n"
            f"> This pull request was generated automatically by the autonomous remediation workflow."
        )

    def _log_step(self, message: str) -> None:
        logger.info("[%s] %s", self.workflow_id, message)
