"""
Trace Logger Module for Recording Multi-Agent Execution Trajectories
"""

import json
from pathlib import Path
from typing import Dict, Any
from src.config import LOGGING_DIR

class TraceLogger:
    def __init__(self, log_dir: Path = LOGGING_DIR):
        log_dir.mkdir(parents=True, exist_ok=True)
        self.trace_file = log_dir / "trace.jsonl"
        
    def clear(self):
        """Reset trace.jsonl for a fresh run."""
        self.trace_file.write_text("", encoding="utf-8")

    def log_step(self, case_id: str, agent_name: str, action: str, details: Dict[str, Any]):
        entry = {
            "case_id": case_id,
            "agent": agent_name,
            "action": action,
            "details": details
        }
        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
