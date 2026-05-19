import os
from typing import Any, Dict
import httpx
from pathlib import Path
from git import Repo

class GitHubTool:
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    async def create_pull_request(self, owner: str, repo: str, head: str, base: str, title: str, body: str) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json={"title": title, "head": head, "base": base, "body": body}, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def create_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json={"body": body}, headers=self._headers())
            response.raise_for_status()
            return response.json()

    def push_changes(self, repo_dir: Path, branch_name: str) -> None:
        repo = Repo(repo_dir)
        origin = repo.remotes.origin
        origin.push(branch_name)
