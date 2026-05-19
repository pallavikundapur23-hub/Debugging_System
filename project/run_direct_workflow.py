import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from app.state.workflow_manager import WorkflowManager
from app.agents.supervisor_agent import SupervisorAgent

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
BASE_CLONE_DIR = Path(os.getenv("BASE_CLONE_DIR", "./repos")).resolve()

if not GITHUB_TOKEN or not GROQ_API_KEY:
    raise SystemExit("GITHUB_TOKEN and GROQ_API_KEY must be set in .env")

workflow_manager = WorkflowManager(BASE_DIR / "workflow_state")

issue_details = {
    "title": "Automated remediation test",
    "body": "Analyze the repository and generate a fix if necessary.",
    "text": "Analyze the repository and generate a fix if necessary.",
    "issue_number": 1,
    "event": "issues",
}

supervisor = SupervisorAgent(
    clone_url="https://github.com/charishmap3/buggy-todo-api.git",
    repo_name="charishmap3/buggy-todo-api",
    issue_details=issue_details,
    state_manager=workflow_manager,
    base_clone_dir=BASE_CLONE_DIR,
    github_token=GITHUB_TOKEN,
    groq_api_key=GROQ_API_KEY,
    groq_model=MODEL_NAME,
)

async def main():
    await supervisor.start()
    print("Workflow completed", supervisor.workflow_id)

if __name__ == "__main__":
    asyncio.run(main())
