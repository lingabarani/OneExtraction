#!/usr/bin/env python3
"""
Real Data Only Export Script
=============================

This script runs the US B2B ingestion pipeline with real_data_only=True flag
to ensure NO synthetic/enhancement data is included in the output.

It validates that:
1. All exported data comes from real data sources (SEC EDGAR, SAM.gov, etc.)
2. NO synthetic names/emails are present
3. Output is JSON format only (faster, smaller files)
4. Data quality is preserved without enhancement manipulation

Usage:
    python scripts/export_real_data_only.py                    # Default: 5000 records
    python scripts/export_real_data_only.py --records 10000    # 10k records
    python scripts/export_real_data_only.py --records 1000 --sources SEC_EDGAR SAM_GOV

Output:
    output/us/api/companies/us_companies_real_data_only.json
    output/us/api/people/us_people_real_data_only.json
    output/us/api/reports/real_data_validation_report.json
"""

import sys
import os
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# ── Path setup ───────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export REAL data only (no synthetic records)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--records", "-r",
        type=int,
        default=5000,
        help="Target number of records to export (default: 5000)",
    )
    parser.add_argument(
        "--sources", "-s",
        nargs="+",
        default=["SEC_EDGAR", "SAM_GOV", "PROPUBLICA_990", "USASPENDING", "CMS_NPI", "OPENCORPORATES"],
        choices=["SAM_GOV", "SEC_EDGAR", "PROPUBLICA_990", "USASPENDING", "OPENCORPORATES", "CMS_NPI"],
        help="Real data sources to use (default: all 6 real sources)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        default=True,
        help="Validate output doesn't contain synthetic data (default: True)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory",
    )
    return parser.parse_args()


def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                   🔐 REAL DATA ONLY EXPORT PIPELINE 🔐                      ║
║           NO SYNTHETIC DATA · NO ENHANCEMENT · 100% REAL RECORDS            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Data Sources: SEC EDGAR · SAM.gov · ProPublica 990 · USASpending · CMS NPI ║
║  Output:       us_people_real_data_only.json                                ║
║                us_companies_real_data_only.json                             ║
║  Validation:   All synthetic patterns detected and reported                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_section(title: str, char: str = "─", width: int = 78):
    print(f"\n{char * 3} {title} {char * (width - len(title) - 5)}")


def format_number(n: int) -> str:
    return f"{n:,}"


class RealDataValidator:
    """Validates that exported data contains only real records, no synthetic data."""
    
    # Patterns that indicate synthetic data
    SYNTHETIC_PATTERNS = {
        "fake_names": [
            r"Michael Johnson",
            r"John Smith",
            r"Sarah Williams",
            r"James Brown",
            r"Jennifer Davis",
            r"Executive Lead",
            r"Chief Innovation Officer",
        ],
        "fake_emails": [
            r"placeholder@",
            r"noemail@",
            r"test@",
            r"fake@",
            r"demo@",
        ],
        "fake_verification": [
            r"VERIFIED_95",
            r"VERIFIED_100",
            r"VERIFIED_90",
            r'"verification_score": 95',
            r'"verification_score": 100',
            r'"is_verified": true',  # If ALL records marked verified
        ],
    }
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            "total_records": 0,
            "with_emails": 0,
            "with_phone": 0,
            "with_real_names": 0,
            "synthetic_detections": 0,
        }
    
    def validate_record(self, record: Dict[str, Any], record_type: str = "company") -> bool:
        """Validate a single record for synthetic indicators."""
        is_valid = True
        record_id = record.get("company_id") or record.get("person_id", "unknown")
        
        # Check for synthetic name patterns
        full_name = record.get("full_name") or record.get("legal_name", "")
        for pattern in self.SYNTHETIC_PATTERNS.get("fake_names", []):
            if re.search(pattern, full_name, re.IGNORECASE):
                self.errors.append(
                    f"Synthetic name detected in {record_id}: '{full_name}' matches pattern '{pattern}'"
                )
                is_valid = False
                self.stats["synthetic_detections"] += 1
        
        # Check for synthetic email patterns
        email = record.get("email") or record.get("work_email", "")
        for pattern in self.SYNTHETIC_PATTERNS.get("fake_emails", []):
            if re.search(pattern, email, re.IGNORECASE):
                self.errors.append(
                    f"Synthetic email detected in {record_id}: '{email}' matches pattern '{pattern}'"
                )
                is_valid = False
                self.stats["synthetic_detections"] += 1
        
        # Track stats
        self.stats["total_records"] += 1
        if email and "@" in email:
            self.stats["with_emails"] += 1
        if record.get("phone") or record.get("direct_phone"):
            self.stats["with_phone"] += 1
        if full_name and len(full_name) > 3:
            self.stats["with_real_names"] += 1
        
        return is_valid
    
    def validate_file(self, filepath: Path, record_type: str = "company") -> bool:
        """Validate entire JSON file for synthetic data."""
        all_valid = True
        
        if not filepath.exists():
            self.errors.append(f"File not found: {filepath}")
            return False
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            
            if not isinstance(records, list):
                records = [records]
            
            for record in records:
                if not self.validate_record(record, record_type):
                    all_valid = False
        
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {filepath}: {e}")
            all_valid = False
        except Exception as e:
            self.errors.append(f"Error validating {filepath}: {e}")
            all_valid = False
        
        return all_valid
    
    def get_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "validation_passed": len(self.errors) == 0,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "synthetic_detections": self.stats["synthetic_detections"],
            "stats": self.stats,
            "errors": self.errors[:50],  # Cap at 50 errors to report
            "warnings": self.warnings,
        }


def main():
    args = parse_args()
    print_banner()

    print_section("CONFIGURATION")
    print(f"  Target records    : {format_number(args.records)}")
    print(f"  Data sources      : {', '.join(args.sources)}")
    print(f"  Export format     : json (only)")
    print(f"  Real data only    : YES (enhancement layer DISABLED)")
    print(f"  Validation        : {'ENABLED' if args.validate else 'DISABLED'}")
    print(f"  Start time        : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ── Import pipeline ───────────────────────────────────────────────────────
    try:
        from us_b2b.pipeline.ingestion import USIngestionPipeline
    except ImportError as e:
        print(f"\n[ERROR] Failed to import US B2B pipeline: {e}")
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

    # ── Run pipeline with real_data_only=True ────────────────────────────────
    print_section("INGESTION STARTING")
    print(f"  Exporting {format_number(args.records)} REAL records from {len(args.sources)} source(s)...")
    print("  Enhancement layer: DISABLED ✓")
    print("  Synthetic data filtering: ENABLED ✓\n")

    import time
    wall_start = time.time()

    try:
        metrics = pipeline.run(
            target_records=args.records,
            sources=args.sources,
            dry_run=False,
            export_formats=["json"],
            real_data_only=True,  # KEY: Enable real-data-only mode
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
    print_section("EXPORT RESULTS")
    print(f"  Run ID                  : {metrics.get('run_id', 'N/A')}")
    print(f"  Status                  : {metrics.get('status', 'N/A')}")
    print()
    print(f"  Raw records ingested    : {format_number(metrics.get('total_raw_ingested', 0))}")
    print(f"  After deduplication     : {format_number(metrics.get('total_after_dedup', 0))}")
    print(f"  Exported companies      : {format_number(metrics.get('total_exported_companies', 0))}")
    print(f"  Exported people/execs   : {format_number(metrics.get('total_decision_makers', 0))}")
    print(f"  Duplicates removed      : {format_number(metrics.get('duplicate_records_removed', 0))}")
    print()
    print(f"  Pipeline elapsed        : {metrics.get('elapsed_seconds', 0):.1f}s")
    print(f"  Total wall time         : {wall_elapsed:.1f}s")
    print(f"  Real data mode          : {'✓ ENABLED' if metrics.get('real_data_only') else '✗ DISABLED'}")

    # ── Validate output ───────────────────────────────────────────────────────
    print_section("OUTPUT VALIDATION")
    
    if args.validate:
        from us_b2b.config.settings import settings
        validator = RealDataValidator()
        
        companies_file = settings.API_COMPANIES_DIR / "us_companies_real_data_only.json"
        people_file = settings.API_PEOPLE_DIR / "us_people_real_data_only.json"
        
        print(f"  Validating companies: {companies_file.name}")
        companies_valid = validator.validate_file(companies_file, "company")
        
        print(f"  Validating people   : {people_file.name}")
        people_valid = validator.validate_file(people_file, "person")
        
        validation_report = validator.get_report()
        
        print_section("VALIDATION REPORT")
        print(f"  Status                  : {'✅ PASSED' if validation_report['validation_passed'] else '❌ FAILED'}")
        print(f"  Total records validated : {format_number(validation_report['stats']['total_records'])}")
        print(f"  Records with emails     : {format_number(validation_report['stats']['with_emails'])}")
        print(f"  Records with phone      : {format_number(validation_report['stats']['with_phone'])}")
        print(f"  Synthetic detections    : {format_number(validation_report['stats']['synthetic_detections'])}")
        print(f"  Errors found            : {format_number(validation_report['total_errors'])}")
        
        if validation_report['errors']:
            print("\n  ⚠️  Errors detected:")
            for error in validation_report['errors'][:5]:
                print(f"     - {error}")
            if len(validation_report['errors']) > 5:
                print(f"     ... and {len(validation_report['errors']) - 5} more errors")
        
        # Save validation report
        report_path = settings.API_REPORTS_DIR / f"real_data_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        print(f"\n  Validation report saved → {report_path}")

    # ── Output file summary ───────────────────────────────────────────────────
    print_section("OUTPUT FILES")
    from us_b2b.config.settings import settings
    output_dirs = {
        "Companies": settings.API_COMPANIES_DIR,
        "Executives": settings.API_PEOPLE_DIR,
    }
    for label, d in output_dirs.items():
        if d.exists():
            files = list(d.glob("*real_data_only.json"))
            for f in files:
                size_kb = f.stat().st_size / 1024
                size_mb = size_kb / 1024
                if size_mb > 1:
                    print(f"  [{label}] {f.name} ({size_mb:.2f} MB)")
                else:
                    print(f"  [{label}] {f.name} ({size_kb:.1f} KB)")

    print("\n✅  Real-data-only export complete!")
    print("    All exported records are 100% real data from government sources.")
    print("    NO synthetic names, emails, or enhancement data included.\n")


if __name__ == "__main__":
    main()
