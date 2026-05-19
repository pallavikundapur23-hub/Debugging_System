from typing import Dict, Any, List
from app.utils.prompts import RESEARCH_PROMPT
from app.tools.web_search_tool import WebSearchTool

class ResearchAgent:
    def __init__(self, groq_client, search_tool: WebSearchTool):
        self.groq = groq_client
        self.search_tool = search_tool

    async def research(self, issue_summary: str) -> Dict[str, Any]:
        references = await self.search_tool.search(issue_summary)
        prompt = RESEARCH_PROMPT.format(summary=issue_summary)
        notes = await self.groq.generate(prompt)
        return {"references": references, "notes": notes}
