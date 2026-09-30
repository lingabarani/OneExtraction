#!/usr/bin/env python3
"""
Wrapper to execute scripts/run_pdl_alone.py from within the botasaurus directory.
Usage:
    python run_pdl.py --limit 1000
"""

import sys
import subprocess
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent / "scripts" / "run_pdl_alone.py"

if __name__ == "__main__":
    args = sys.argv[1:]
    cmd = [sys.executable, str(SCRIPT_PATH)] + args
    result = subprocess.run(cmd, cwd=str(Path(__file__).resolve().parent))
    sys.exit(result.returncode)
