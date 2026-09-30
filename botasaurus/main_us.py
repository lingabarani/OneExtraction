import sys
import argparse
from pathlib import Path
import logging

# Ensure src is in python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from us_b2b.pipeline.ingestion import pipeline

logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="US B2B Data Pipeline")
    parser.add_argument("--limit", "-l", type=int, default=100, help="Number of records to retrieve per API")
    args = parser.parse_args()

    print("\n" + "=" * 50)
    print(" [US B2B DATA PIPELINE]")
    print("=" * 50)
    print(f" Retrieving data from all 7 US directories with Limit: {args.limit}")
    pipeline.run_ingestion(limit=args.limit)
    print("=" * 50 + "\n")

if __name__ == "__main__":
    main()
