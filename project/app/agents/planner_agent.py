from typing import Dict, Any, List
from app.utils.prompts import ISSUE_SUMMARY_PROMPT

class PlannerAgent:
    def __init__(self, groq_client):
        self.groq = groq_client

    async def create_plan(self, issue_details: Dict[str, Any], repo_summary: Dict[str, Any]) -> Dict[str, Any]:
        issue_text = issue_details.get("text", "")
        prompt = ISSUE_SUMMARY_PROMPT.format(title=issue_details.get("title", ""), body=issue_text)
        plan_text = await self.groq.generate(prompt)
        selected_files = repo_summary.get("sample_files", [])[:8]
        return {
            "issue_summary": plan_text,
            "selected_files": selected_files,
            "strategy": "inspect selected files and gather references",
        }
