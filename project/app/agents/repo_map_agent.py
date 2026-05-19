from pathlib import Path
from typing import Dict, Any
from app.tools.file_reader_tool import FileReaderTool
from app.utils.helpers import now_iso

class RepoMapAgent:
    def __init__(self, repo_dir: Path, groq_client):
        self.repo_dir = repo_dir
        self.reader = FileReaderTool(repo_dir)
        self.groq = groq_client

    async def analyze_repository(self) -> Dict[str, Any]:
        files = await self.reader.scan_files()
        summary_lines = [f"{file.relative_to(self.repo_dir)}" for file in files[:40]]
        repo_summary = {
            "total_files": len(files),
            "sample_files": summary_lines,
            "repo_dir": str(self.repo_dir),
            "generated_at": now_iso(),
        }
        return repo_summary
