import json
from pathlib import Path
from typing import Any

from app.utils.helpers import ensure_dir, now_iso

class WorkflowManager:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        ensure_dir(self.state_dir)

    def workflow_path(self, workflow_id: str) -> Path:
        return self.state_dir / f"{workflow_id}.json"

    def create_state(self, workflow_id: str, initial_state: dict) -> None:
        path = self.workflow_path(workflow_id)
        self.save_state(path, initial_state)

    def save_state(self, path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def update_state(self, workflow_id: str, data: dict) -> None:
        path = self.workflow_path(workflow_id)
        state = self.load_state(workflow_id)
        state.update(data)
        state["updated_at"] = now_iso()
        self.save_state(path, state)

    def load_state(self, workflow_id: str) -> dict:
        path = self.workflow_path(workflow_id)
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
