import shutil
from pathlib import Path
from typing import Dict
from app.utils.helpers import ensure_dir

class PatchWriterTool:
    def __init__(self, repo_dir: Path):
        self.repo_dir = repo_dir

    def backup_file(self, target: Path) -> None:
        backup_dir = self.repo_dir / ".patch_backups"
        ensure_dir(backup_dir)
        if target.exists():
            shutil.copy2(target, backup_dir / target.name)

    def apply_patches(self, patches: Dict[str, str]) -> None:
        for relative_path, content in patches.items():
            target = self.repo_dir / relative_path
            ensure_dir(target.parent)
            self.backup_file(target)
            target.write_text(content, encoding="utf-8")
