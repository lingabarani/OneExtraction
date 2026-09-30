#!/usr/bin/env python3
"""
Root-level wrapper script to run People Data Labs (PDL) ingestion.
Can be executed directly from the project root:
    python run_pdl.py --limit 25
"""

import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BOTASAURUS_DIR = ROOT_DIR / "botasaurus"
SCRIPT_PATH = BOTASAURUS_DIR / "scripts" / "run_pdl_alone.py"

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    result = subprocess.run(cmd, cwd=str(BOTASAURUS_DIR))
    sys.exit(result.returncode)
