from typing import Dict, Any
from app.utils.prompts import VALIDATION_PROMPT

class VerifierAgent:
    def __init__(self, groq_client):
        self.groq = groq_client

    async def verify(self, issue_details: Dict[str, Any], patch_result: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        prompt = VALIDATION_PROMPT.format(
            issue_text=issue_details.get("text", ""),
            patch_summary=patch_result.get("summary", ""),
            validation_output=str(validation_result),
        )
        summary = await self.groq.generate(prompt)
        return {"summary": summary, "passed": validation_result.get("status") == "success"}
