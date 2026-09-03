#!/usr/bin/env python3
"""
Mexico B2B Open-Data Ingestion Pipeline CLI Entrypoint.

Usage:
  python main.py --dry-run
  python main.py --source denue --limit 100 --dry-run
  python main.py --source siem --limit 100
  python main.py --source all --limit 1000
  python main.py --source all
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles where supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure src is in python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from mexico_b2b.pipeline.ingestion import pipeline
from mexico_b2b.utils.logging import logger
from mexico_b2b.config.settings import settings


def main():
    parser = argparse.ArgumentParser(
        description="Mexico B2B Company Open-Data Ingestion Pipeline (INEGI DENUE, SIEM, datos.gob.mx, SAT, Suppliers)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default="all",
        help="Source to ingest: 'denue', 'siem', 'supplier', 'sat', 'datos_gob', or 'all'",
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Maximum records to process per source (for sampling or testing)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation and normalization without writing output files to disk",
    )

    args = parser.parse_args()

    source_keys = [args.source] if args.source else ["all"]
    
    print("\n" + "=" * 70)
    print(" [MEXICO B2B OPEN-DATA COMPANY INGESTION PIPELINE]")
    print("=" * 70)
    print(f" Source(s)      : {args.source}")
    print(f" Limit / Source : {args.limit or 'Unlimited'}")
    print(f" Dry Run Mode   : {args.dry_run}")
    print(f" Contact Export : {'ENABLED' if settings.ENABLE_PERSONAL_CONTACT_FIELDS else 'MASKED (B2B Public Only)'}")
    print("=" * 70 + "\n")

    try:
        results = pipeline.run(
            source_keys=source_keys,
            limit=args.limit,
            dry_run=args.dry_run,
        )

        metrics = results["metrics"]
        print("\n" + "-" * 70)
        print(" [INGESTION & EXECUTIVE LEADS SUMMARY REPORT]")
        print("-" * 70)
        print(f" Total Raw Records Ingested   : {metrics['total_raw_records']}")
        print(f" Structurally Valid Records   : {metrics['valid_records']}")
        print(f" Invalid Records Filtered     : {metrics['invalid_records']}")
        print(f" Duplicates Resolved          : {metrics['duplicates']}")
        print(f" Canonical Companies Produced : {metrics['merged_records']}")
        print(f" Average Data Quality Score   : {metrics['average_quality_score']} / 100")
        print(f" Total Decision-Makers (Leads): {metrics.get('total_decision_makers', 0)}")
        print(f"   - C-Suite Executives (CEO/CTO/CFO/CLO) : {metrics.get('c_suite_executives', 0)}")
        print(f"   - Founders & Owners                    : {metrics.get('founders_and_owners', 0)}")
        print(f"   - HR & People Operations Leads         : {metrics.get('hr_and_people_leads', 0)}")
        print(f"   - Deliverable Work Emails (Permutations): {metrics.get('deliverable_work_emails', 0)}")
        print(f" Records with RFC             : {metrics['records_with_rfc']}")
        print(f" Records with Phone           : {metrics['records_with_phone']}")
        print(f" Records with Email           : {metrics['records_with_email']}")
        print(f" Records with Website/Domain  : {metrics['records_with_website']}")
        print(f" Records with Coordinates     : {metrics['records_with_coordinates']}")
        print(f" Total Duration               : {metrics['total_duration_seconds']}s")
        print("-" * 70)

        if not args.dry_run:
            print(f"\n[OK] Production Output Files Generated:")
            print(f" [Companies Master Data]")
            print(f"   - JSON   : {settings.OUTPUT_DIR / 'mexico_companies.json'}")
            print(f"   - CSV    : {settings.OUTPUT_DIR / 'mexico_companies.csv'}")
            print(f"   - Excel  : {settings.OUTPUT_DIR / 'mexico_companies.xlsx'}")
            print(f" [Decision-Makers & Executive Leads]")
            print(f"   - JSON   : {settings.OUTPUT_DIR / 'mexico_people.json'}")
            print(f"   - CSV    : {settings.OUTPUT_DIR / 'mexico_people.csv'}")
            print(f"   - Excel  : {settings.OUTPUT_DIR / 'mexico_people.xlsx'}")
            print(f" [Auditing & Reports]")
            print(f"   - Report : {settings.OUTPUT_DIR / 'validation_report.json'}")
            print(f"   - Status : {settings.OUTPUT_DIR / 'source_status.json'}")
        print("\nPipeline execution complete.\n")

    except Exception as e:
        logger.error(f"Fatal pipeline error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
