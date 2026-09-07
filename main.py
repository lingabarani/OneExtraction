#!/usr/bin/env python3
"""
Root entrypoint forwarder for OneExtraction / Mexico B2B Ingestion Pipeline.
Allows running `python main.py` directly from the repository root.
"""

import sys
import os
from pathlib import Path

root_dir = Path(__file__).resolve().parent
botasaurus_dir = root_dir / "botasaurus"
src_dir = botasaurus_dir / "src"

for p in (str(src_dir), str(botasaurus_dir), str(root_dir)):
    if p not in sys.path:
        sys.path.insert(0, p)

os.chdir(str(botasaurus_dir))

if __name__ == "__main__":
    from main import main
    main()
