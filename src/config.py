import os
from pathlib import Path

# Base Directory Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
LOGGING_DIR = BASE_DIR / "logging"

# Model & Lab Specs
COHORT = "K3"
POLICY_VERSION = "EC_POLICY_V1"
MODEL_NAME = "gemma-2-9b-it"
PARAMETER_SIZE = "9B"

# Ensure output and logging directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGGING_DIR.mkdir(parents=True, exist_ok=True)

# Load API key from .env if present
ENV_PATH = BASE_DIR / ".env"
API_KEY = None
if ENV_PATH.exists():
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("API_KEY="):
                API_KEY = line.split("=", 1)[1].strip()
                break

if not API_KEY:
    API_KEY = os.getenv("API_KEY", "")
