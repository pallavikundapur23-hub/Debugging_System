from pathlib import Path
from typing import Dict, Any
from app.tools.command_executor_tool import CommandExecutorTool

class ValidationAgent:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.executor = CommandExecutorTool()

    async def validate(self) -> Dict[str, Any]:
        commands = [
            ["python", "-m", "compileall", "."],
        ]
        if (self.repo_dir / "tests").exists():
            commands.append(["python", "-m", "pytest", "-q"])
        results = []
        for command in commands:
            result = await self.executor.run_command(command, self.repo_dir, timeout=90)
            results.append({"command": " ".join(command), **result})
            if result["status"] != "success":
                return {"status": "failed", "results": results}
        return {"status": "success", "results": results}
