import asyncio
from pathlib import Path
from typing import List
import aiofiles

class FileReaderTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir

    async def scan_files(self, extensions: List[str] = None) -> List[Path]:
        extensions = extensions or [".py", ".js", ".ts", ".md", ".yml", ".yaml", ".json"]
        files = []
        for path in self.repo_dir.rglob("*"):
            if path.is_file() and path.suffix in extensions:
                files.append(path)
        return files

    async def read_file(self, path: Path) -> str:
        async with aiofiles.open(path, mode="r", encoding="utf-8", errors="ignore") as handle:
            return await handle.read()
