#!/usr/bin/env python3
"""
US B2B Apollo.io-Style Data Pipeline — Bulk Ingestion Script.
Mirrors Mexico's bulk_ingest.py exactly in interface and behaviour.

Usage:
    python us_bulk_ingest.py                            # 5,000 records, all sources
    python us_bulk_ingest.py --records 50000            # 50k records
    python us_bulk_ingest.py --records 1000 --dry-run   # Dry run, no export
    python us_bulk_ingest.py --sources SAM_GOV SEC_EDGAR --format xlsx json
    python us_bulk_ingest.py --records 50000 --format xlsx json csv

Sources available:
    SAM_GOV          SAM.gov federal vendor registry (company + POC contacts)
    SEC_EDGAR        SEC EDGAR public company filings (company + executives)
    PROPUBLICA_990   IRS 990 nonprofit data (company + officers)
    USASPENDING      USASpending.gov federal award recipients
    OPENCORPORATES   50-state business registrations + officers
"""

import sys
import os
import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Path setup ───────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))



def parse_args():
    parser = argparse.ArgumentParser(
        description="US B2B Apollo.io-Style Bulk Data Ingestion Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--records", "-r",
        type=int,
        default=5000,
        help="Target number of company records to collect (default: 5000, max tested: 50000)",
    )
    parser.add_argument(
        "--sources", "-s",
        nargs="+",
        default=["SEC_EDGAR", "PROPUBLICA_990", "USASPENDING", "CMS_NPI"],
        choices=["SAM_GOV", "SEC_EDGAR", "PROPUBLICA_990", "USASPENDING", "OPENCORPORATES", "CMS_NPI", "FCC_ULS", "OPENDIRECTORIES"],
        help="Data sources to include (default: all 8 sources)",
    )


    parser.add_argument(
        "--format", "-f",
        nargs="+",
        default=["json"],
        choices=["json", "xlsx", "csv"],
        help="Export formats (default: json)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Run pipeline without exporting files",
    )
    parser.add_argument(
        "--no-people",
        action="store_true",
        default=False,
        help="Skip executive/decision-maker enrichment",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory (default: output/us/api/)",
    )
    parser.add_argument(
        "--real-data-only",
        action="store_true",
        default=False,
        help="Skip enhancement layer and export only real scraped data (no synthetic records)",
    )
    return parser.parse_args()


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║         🇺🇸  US B2B APOLLO.IO-STYLE INTELLIGENCE PIPELINE  🇺🇸              ║
║                    OneExtraction — Research POC                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Sources: SEC EDGAR · SAM.gov · USASpending · OpenCorporates · IRS 990     ║
║  Output:  Companies + C-Suite Executives + Emails + Industry Classification ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_section(title: str, char: str = "─", width: int = 78):
    print(f"\n{char * 3} {title} {char * (width - len(title) - 5)}")


def format_number(n: int) -> str:
    return f"{n:,}"


def main():
    args = parse_args()
    print_banner()

    print_section("CONFIGURATION")
    print(f"  Target records    : {format_number(args.records)}")
    print(f"  Sources           : {', '.join(args.sources)}")
    print(f"  Export formats    : {', '.join(args.format)}")
    print(f"  Dry run           : {args.dry_run}")
    print(f"  Skip people       : {args.no_people}")
    print(f"  Real data only    : {args.real_data_only}")
    print(f"  Start time        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Import pipeline ───────────────────────────────────────────────────────
    try:
        from us_b2b.pipeline.ingestion import USIngestionPipeline
    except ImportError as e:
        print(f"\n[ERROR] Failed to import US B2B pipeline: {e}")
        print("        Make sure you are running from the botasaurus/ directory")
        print("        and all dependencies are installed.")
        sys.exit(1)

    pipeline = USIngestionPipeline()

    # ── Custom output dir ─────────────────────────────────────────────────────
    if args.output_dir:
        from us_b2b.config.settings import settings
        settings.API_COMPANIES_DIR = Path(args.output_dir) / "companies"
        settings.API_PEOPLE_DIR = Path(args.output_dir) / "people"
        settings.API_REPORTS_DIR = Path(args.output_dir) / "reports"
        for d in [settings.API_COMPANIES_DIR, settings.API_PEOPLE_DIR, settings.API_REPORTS_DIR]:
            d.mkdir(parents=True, exist_ok=True)

    # ── Run pipeline ──────────────────────────────────────────────────────────
    print_section("INGESTION STARTING")
    print(f"  Ingesting up to {format_number(args.records)} records from {len(args.sources)} source(s)...")
    print("  (This may take several minutes depending on API rate limits)\n")

    wall_start = time.time()

    try:
        metrics = pipeline.run(
            target_records=args.records,
            sources=args.sources,
            dry_run=args.dry_run,
            export_formats=args.format,
            real_data_only=args.real_data_only,
        )
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    wall_elapsed = time.time() - wall_start

    # ── Print results ─────────────────────────────────────────────────────────
    print_section("RESULTS")
    print(f"  Run ID                  : {metrics.get('run_id', 'N/A')}")
    print(f"  Status                  : {metrics.get('status', 'N/A')}")
    print()
    print(f"  Raw records ingested    : {format_number(metrics.get('total_raw_ingested', 0))}")
    print(f"  After deduplication     : {format_number(metrics.get('total_after_dedup', 0))}")
    print(f"  Valid companies         : {format_number(metrics.get('total_valid_companies', 0))}")
    print(f"  Exported companies      : {format_number(metrics.get('total_exported_companies', 0))}")
    print(f"  Decision makers (people): {format_number(metrics.get('total_decision_makers', 0))}")
    print(f"  Duplicates removed      : {format_number(metrics.get('duplicate_records_removed', 0))}")
    print(f"  Avg quality score       : {metrics.get('avg_quality_score', 0):.1f}/100")
    print()
    print(f"  Pipeline elapsed        : {metrics.get('elapsed_seconds', 0):.1f}s")
    print(f"  Total wall time         : {wall_elapsed:.1f}s")

    if not args.dry_run:
        print_section("OUTPUT FILES")
        from us_b2b.config.settings import settings
        output_dirs = {
            "Companies": settings.API_COMPANIES_DIR,
            "Executives": settings.API_PEOPLE_DIR,
            "Industry Report": settings.API_REPORTS_DIR,
        }
        for label, d in output_dirs.items():
            if d.exists():
                files = list(d.iterdir())
                for f in files:
                    size_kb = f.stat().st_size / 1024
                    print(f"  [{label}]  {f.name}  ({size_kb:.1f} KB)")

    print_section("FIELD REFERENCE")
    print("  Companies: company_id, legal_name, trade_name, ein, entity_type,")
    print("             cik, cage_code, uei, naics_code, sic_code, industry,")
    print("             employee_count_min/max, phone, email, website, domain,")
    print("             street, city, state, state_code, zip_code, lat/long,")
    print("             data_quality_score, source_count, last_verified_at")
    print()
    print("  Executives: person_id, company_id, company_name, full_name,")
    print("              first_name, last_name, title, standardized_title,")
    print("              seniority_level, department, work_email, email_status,")
    print("              email_confidence_score, mail_provider, direct_phone")

    print("\n⚠️  NOTE: This is a POC/research build. Data accuracy requires verification.")
    print(f"\n✅  US B2B pipeline complete. {format_number(metrics.get('total_exported_companies', 0))} companies, "
          f"{format_number(metrics.get('total_decision_makers', 0))} executives.\n")

    # Save metrics
    if not args.dry_run:
        from us_b2b.config.settings import settings
        metrics_path = settings.API_REPORTS_DIR / f"us_run_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        print(f"  Metrics saved → {metrics_path}\n")


if __name__ == "__main__":
    main()
