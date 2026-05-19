import re
from pathlib import Path
from typing import Dict, Any, List
from app.tools.file_reader_tool import FileReaderTool

class CodeSearchAgent:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir
        self.reader = FileReaderTool(repo_dir)

    async def search(self, issue_text: str, selected_files: List[str]) -> Dict[str, Any]:
        keywords = [token.strip() for token in issue_text.split() if len(token) > 3][:12]
        results = []
        for relative_path in selected_files:
            path = self.repo_dir / relative_path
            if path.exists():
                content = await self.reader.read_file(path)
                matches = []
                for keyword in keywords:
                    if re.search(re.escape(keyword), content, re.IGNORECASE):
                        matches.append(keyword)
                if matches:
                    results.append({"path": relative_path, "matches": list(set(matches))})
        return {"keywords": keywords, "hits": results}
