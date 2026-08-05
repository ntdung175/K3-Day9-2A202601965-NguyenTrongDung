"""Structured trace logger for the 50-case batch run."""
import json
from pathlib import Path
from typing import Any, Dict
from src.config import LOGGING_DIR

class TraceLogger:
    def __init__(self, log_dir: Path = LOGGING_DIR):
        log_dir.mkdir(parents=True, exist_ok=True)
        self.trace_file = log_dir / "trace.jsonl"
    def clear(self) -> None:
        self.trace_file.write_text("", encoding="utf-8")
    def log_step(self, case_id: str, agent: str, action: str, details: Dict[str, Any]) -> None:
        with self.trace_file.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"case_id": case_id, "agent": agent, "action": action, "details": details}, ensure_ascii=False) + "\n")
