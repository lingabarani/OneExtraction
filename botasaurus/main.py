#!/usr/bin/env python3
"""
Mexico B2B Open-Data Ingestion Pipeline CLI Entrypoint.
Supports separated API Ingestion, Public-Directory Scraping, and Combined Golden Entity Resolution.

Usage Examples:
  python main.py --source api
  python main.py --source scraping
  python main.py --source all
  python main.py --source api --sample
  python main.py --source scraping --sample
  python main.py --source all --combine
  python main.py --source denue --limit 100
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
        description="Mexico B2B Company Ingestion Pipeline (Separated API & Public-Directory Scraping Channels)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--source",
        "-s",
        type=str,
        default="all",
        help="Target channel or source: 'api', 'scraping', 'all', 'denue', 'siem', 'canacintra', 'amcham', 'cosmos', 'quiminet', 'seccion_amarilla', 'sat', 'supplier_registry', 'datos_gob'",
    )

    parser.add_argument(
        "--category",
        "-c",
        type=str,
        choices=["api", "scraping", "all"],
        default=None,
        help="Explicit channel category: 'api', 'scraping', or 'all'",
    )

    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=None,
        help="Maximum records to process per source (for sampling or testing)",
    )

    parser.add_argument(
        "--sample",
        action="store_true",
        help="Run quick sample ingestion (10-50 records) for rapid validation",
    )

    parser.add_argument(
        "--combine",
        action="store_true",
        help="Execute combined Golden Profile entity resolution stage after ingestion",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run validation and normalization without writing output files to disk",
    )

    args = parser.parse_args()

    category = args.category
    if not category:
        if args.source.lower() in ("api", "scraping", "all"):
            category = args.source.lower()
        else:
            category = "all"

    source_keys = [args.source] if args.source else ["all"]

    print("\n" + "=" * 75)
    print(" [MEXICO B2B PIPELINE - SEPARATED API & SCRAPING INGESTION]")
    print("=" * 75)
    print(f" Target Channel : {category.upper()}")
    print(f" Source(s)      : {args.source}")
    print(f" Limit / Source : {args.limit or ('Sample (50)' if args.sample else 'Unlimited')}")
    print(f" Combine Stage  : {'ENABLED' if args.combine or category == 'all' else 'DISABLED'}")
    print(f" Dry Run Mode   : {args.dry_run}")
    print(f" Contact Export : {'ENABLED' if settings.ENABLE_PERSONAL_CONTACT_FIELDS else 'MASKED (B2B Public Only)'}")
    print("=" * 75 + "\n")

    try:
        results = pipeline.run(
            source_keys=source_keys,
            category=category,
            limit=args.limit,
            dry_run=args.dry_run,
            combine=args.combine,
            sample=args.sample,
        )

        print("\n" + "-" * 75)
        print(" [INGESTION & CHANNEL EXECUTION SUMMARY]")
        print("-" * 75)

        if results.get("api"):
            api_m = results["api"]["metrics"]
            print(" [CHANNEL: API INGESTION]")
            print(f"   • Companies Ingested     : {api_m['companies']:,}")
            print(f"   • People/Leads Ingested  : {api_m['people']:,}")
            print(f"   • Validation Passed      : {api_m['records_received'] - api_m['records_rejected']:,}")
            print(f"   • Average Quality Score  : {api_m['average_quality_score']} / 100")
            print(f"   • Output Companies JSON  : {settings.API_COMPANIES_DIR / 'api_companies.json'}")
            print(f"   • Output People JSON     : {settings.API_PEOPLE_DIR / 'api_people.json'}")
            print(f"   • Ingestion Log          : {settings.API_LOGS_DIR / 'api_ingestion.log'}")
            print(f"   • Summary Report         : {settings.API_LOGS_DIR / 'api_summary.json'}")

        if results.get("scraping"):
            scr_m = results["scraping"]["metrics"]
            print("\n [CHANNEL: PUBLIC-DIRECTORY SCRAPING]")
            print(f"   • Companies Scraped      : {scr_m['companies']:,}")
            print(f"   • People/Leads Scraped   : {scr_m['people']:,}")
            print(f"   • Validation Passed      : {scr_m['records_received'] - scr_m['records_rejected']:,}")
            print(f"   • Average Quality Score  : {scr_m['average_quality_score']} / 100")
            print(f"   • Output Companies JSON  : {settings.SCRAPING_COMPANIES_DIR / 'scraped_companies.json'}")
            print(f"   • Output People JSON     : {settings.SCRAPING_PEOPLE_DIR / 'scraped_people.json'}")
            print(f"   • Ingestion Log          : {settings.SCRAPING_LOGS_DIR / 'scraping_ingestion.log'}")
            print(f"   • Summary Report         : {settings.SCRAPING_LOGS_DIR / 'scraping_summary.json'}")

        if results.get("combined"):
            comb_s = results["combined"]["summary"]
            print("\n [CHANNEL: COMBINED GOLDEN RESOLUTION]")
            print(f"   • Total API Companies    : {comb_s['total_api_companies']:,}")
            print(f"   • Total Scraped Companies: {comb_s['total_scraped_companies']:,}")
            print(f"   • Golden Profiles Created: {comb_s['golden_company_profiles']:,}")
            print(f"   • Cross-Source Duplicates: {comb_s['cross_source_duplicates']:,}")
            print(f"   • Average Quality Score  : {comb_s['average_quality_score']} / 100")
            print(f"   • Output Companies JSON  : {settings.COMBINED_COMPANIES_DIR / 'all_companies.json'}")
            print(f"   • Output People JSON     : {settings.COMBINED_PEOPLE_DIR / 'all_people.json'}")
            print(f"   • Combined Summary       : {settings.COMBINED_REPORTS_DIR / 'combined_summary.json'}")

        print("-" * 75)
        print("Pipeline execution complete.\n")

    except Exception as e:
        logger.error(f"Fatal pipeline error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
