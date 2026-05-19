import asyncio
from pathlib import Path
from typing import List, Dict

class CommandExecutorTool:
    async def run_command(self, command: List[str], cwd: Path, timeout: int = 90) -> Dict[str, str]:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            process.kill()
            return {"status": "timeout", "stdout": "", "stderr": "Command timed out"}
        return {
            "status": "success" if process.returncode == 0 else "failed",
            "returncode": str(process.returncode),
            "stdout": stdout.decode("utf-8", errors="ignore"),
            "stderr": stderr.decode("utf-8", errors="ignore"),
        }
