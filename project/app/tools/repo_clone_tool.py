import os
from pathlib import Path
from urllib.parse import quote
from git import Repo, GitCommandError
from app.utils.helpers import ensure_dir

class RepoCloneTool:
    def __init__(self, base_dir: Path, github_token: str = ""):
        self.base_dir = base_dir
        self.github_token = github_token
        ensure_dir(self.base_dir)

    def get_repo_dir(self, repo_name: str) -> Path:
        return self.base_dir / repo_name.replace("/", "_")

    def clone_repository(self, clone_url: str, repo_name: str) -> Path:
        repo_dir = self.get_repo_dir(repo_name)
        if repo_dir.exists():
            try:
                repo = Repo(repo_dir)
                repo.remotes.origin.fetch()
                repo.git.reset("--hard", "origin/HEAD")
                return repo_dir
            except GitCommandError:
                pass
        ensure_dir(repo_dir.parent)
        Repo.clone_from(clone_url, repo_dir)
        return repo_dir

    def create_branch(self, repo_dir: Path, branch_name: str) -> None:
        repo = Repo(repo_dir)
        if branch_name in [head.name for head in repo.heads]:
            repo.git.checkout(branch_name)
            return
        repo.git.checkout("-b", branch_name)

    def commit_changes(self, repo_dir: Path, message: str) -> None:
        repo = Repo(repo_dir)
        repo.git.add(all=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(message)

    def _get_authenticated_url(self, url: str) -> str:
        if not self.github_token or not url.startswith("https://"):
            return url
        token = quote(self.github_token, safe="")
        return url.replace("https://", f"https://x-access-token:{token}@", 1)

    def push_branch(self, repo_dir: Path, branch_name: str) -> None:
        repo = Repo(repo_dir)
        origin_url = repo.remotes.origin.url
        auth_url = self._get_authenticated_url(origin_url)
        if auth_url != origin_url:
            repo.git.push(auth_url, branch_name)
        else:
            repo.remotes.origin.push(branch_name)
