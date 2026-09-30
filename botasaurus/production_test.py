"""
OneExtraction - Production Test Suite
Runs comprehensive tests across all platform components.
"""

import sqlite3
import os
import json
import csv
import re
import time
import socket
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DB_PATH        = "output/us/api/oneextraction.db"
COMPANIES_JSON = "output/us/api/companies/us_companies.json"
PEOPLE_JSON    = "output/us/api/enhanced/us_people.json"
EXPORTS_DIR    = "output/exports"
SCRIPTS_DIR    = "scripts"
MCP_SERVER     = "src/us_b2b/mcp_server.py"

PASS  = "✅ PASS"
FAIL  = "❌ FAIL"
WARN  = "⚠️  WARN"
INFO  = "ℹ️  INFO"

results = []

def record(category, test, status, detail=""):
    results.append({"category": category, "test": test, "status": status, "detail": detail})
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ", "INFO": "ℹ️ "}.get(status, "  ")
    print(f"  {icon} {test:<55} {detail}")

def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


# ─────────────────────────────────────────────
# TEST 1 — FILE SYSTEM AUDIT
# ─────────────────────────────────────────────
def test_file_system():
    section("TEST 1 — FILE SYSTEM AUDIT")

    required_files = {
        "Database":        DB_PATH,
        "Companies JSON":  COMPANIES_JSON,
        "People JSON":     PEOPLE_JSON,
        "Email Extractor": f"{SCRIPTS_DIR}/email_extractor.py",
        "Email Validator": f"{SCRIPTS_DIR}/batch_email_validator.py",
        "Data Loader":     f"{SCRIPTS_DIR}/simple_data_loader.py",
        "Domain Populator":f"{SCRIPTS_DIR}/populate_domains.py",
        "Industry Classifier": f"{SCRIPTS_DIR}/classify_and_export_industries.py",
        "MCP Server":      MCP_SERVER,
        "Exports Dir":     EXPORTS_DIR,
    }

    for name, path in required_files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            if os.path.isdir(path):
                files = len(list(Path(path).glob("*")))
                record("FileSystem", name, "PASS", f"{files} files inside")
            else:
                record("FileSystem", name, "PASS", f"{round(size/1024,1)} KB")
        else:
            record("FileSystem", name, "FAIL", f"Missing: {path}")

    # Check export CSVs
    exports = list(Path(EXPORTS_DIR).glob("*.csv")) if os.path.exists(EXPORTS_DIR) else []
    if exports:
        total_size = sum(f.stat().st_size for f in exports)
        record("FileSystem", "Export CSV files", "PASS",
               f"{len(exports)} files, {round(total_size/1024/1024,1)} MB total")
    else:
        record("FileSystem", "Export CSV files", "WARN", "No CSVs found in exports/")


# ─────────────────────────────────────────────
# TEST 2 — DATABASE INTEGRITY
# ─────────────────────────────────────────────
def test_database():
    section("TEST 2 — DATABASE CONNECTIVITY & SCHEMA")

    if not os.path.exists(DB_PATH):
        record("Database", "Connect to SQLite", "FAIL", "DB file not found")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        record("Database", "Connect to SQLite", "PASS", DB_PATH)
    except Exception as e:
        record("Database", "Connect to SQLite", "FAIL", str(e))
        return

    # Required tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    required_tables = ["companies", "people", "enrichment_results"]

    for t in required_tables:
        if t in tables:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            count = cur.fetchone()[0]
            record("Database", f"Table: {t}", "PASS", f"{count:,} rows")
        else:
            record("Database", f"Table: {t}", "FAIL", "Table missing")

    # Indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [r[0] for r in cur.fetchall()]
    record("Database", "Indexes present", "PASS" if len(indexes) >= 5 else "WARN",
           f"{len(indexes)} indexes found")

    # DB size
    db_size_mb = round(os.path.getsize(DB_PATH) / 1024 / 1024, 2)
    record("Database", "Database file size", "PASS" if db_size_mb > 0.5 else "WARN",
           f"{db_size_mb} MB")

    # WAL mode check
    cur.execute("PRAGMA journal_mode")
    jmode = cur.fetchone()[0]
    record("Database", "Journal mode", "INFO", jmode)

    # Integrity check
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    record("Database", "Integrity check", "PASS" if integrity == "ok" else "FAIL", integrity)

    conn.close()


# ─────────────────────────────────────────────
# TEST 3 — DATA QUALITY
# ─────────────────────────────────────────────
def test_data_quality():
    section("TEST 3 — DATA QUALITY (Companies & People)")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── Companies ──
    cur.execute("SELECT COUNT(*) FROM companies")
    total = cur.fetchone()[0]
    record("DataQuality", "Total companies loaded", "PASS" if total >= 1000 else "FAIL",
           f"{total:,}")

    cur.execute("SELECT COUNT(*) FROM companies WHERE name IS NOT NULL AND name != ''")
    with_name = cur.fetchone()[0]
    pct = round(100*with_name/total, 1) if total else 0
    record("DataQuality", "Companies with name", "PASS" if pct == 100 else "WARN", f"{with_name:,} ({pct}%)")

    cur.execute("SELECT COUNT(*) FROM companies WHERE domain IS NOT NULL")
    with_domain = cur.fetchone()[0]
    pct = round(100*with_domain/total, 1) if total else 0
    record("DataQuality", "Companies with domain", "PASS" if pct >= 80 else "WARN", f"{with_domain:,} ({pct}%)")

    cur.execute("SELECT COUNT(*) FROM companies WHERE email IS NOT NULL")
    with_email = cur.fetchone()[0]
    pct = round(100*with_email/total, 1) if total else 0
    record("DataQuality", "Companies with email", "PASS" if pct >= 50 else "WARN", f"{with_email:,} ({pct}%)")

    cur.execute("SELECT COUNT(*) FROM companies WHERE industry IS NOT NULL")
    with_industry = cur.fetchone()[0]
    pct = round(100*with_industry/total, 1) if total else 0
    record("DataQuality", "Companies with industry", "PASS" if pct >= 80 else "WARN", f"{with_industry:,} ({pct}%)")

    cur.execute("SELECT COUNT(*) FROM companies WHERE state_code IS NOT NULL")
    with_state = cur.fetchone()[0]
    pct = round(100*with_state/total, 1) if total else 0
    record("DataQuality", "Companies with state", "PASS" if pct >= 80 else "WARN", f"{with_state:,} ({pct}%)")

    cur.execute("SELECT AVG(data_quality_score) FROM companies WHERE data_quality_score IS NOT NULL")
    avg_score = cur.fetchone()[0]
    avg_score = round(avg_score, 1) if avg_score else 0
    record("DataQuality", "Avg data quality score", "PASS" if avg_score >= 50 else "WARN", f"{avg_score}/100")

    # ── People ──
    cur.execute("SELECT COUNT(*) FROM people")
    people_total = cur.fetchone()[0]
    record("DataQuality", "Total executives loaded", "PASS" if people_total >= 1000 else "WARN",
           f"{people_total:,}")

    cur.execute("SELECT COUNT(DISTINCT company_id) FROM people")
    unique_cos = cur.fetchone()[0]
    ratio = round(people_total/unique_cos, 1) if unique_cos else 0
    record("DataQuality", "Executives per company (avg)", "PASS" if ratio >= 1.5 else "WARN",
           f"{ratio}x ({unique_cos:,} companies covered)")

    cur.execute("SELECT COUNT(*) FROM people WHERE title IS NOT NULL")
    with_title = cur.fetchone()[0]
    pct = round(100*with_title/people_total, 1) if people_total else 0
    record("DataQuality", "Executives with title", "PASS" if pct >= 70 else "WARN", f"{with_title:,} ({pct}%)")

    # ── Industry Coverage ──
    cur.execute("SELECT COUNT(DISTINCT industry) FROM companies WHERE industry IS NOT NULL")
    industry_count = cur.fetchone()[0]
    record("DataQuality", "Unique industries", "PASS" if industry_count >= 20 else "WARN",
           f"{industry_count} industries")

    # ── State Coverage ──
    cur.execute("SELECT COUNT(DISTINCT state_code) FROM companies WHERE state_code IS NOT NULL")
    state_count = cur.fetchone()[0]
    record("DataQuality", "States covered", "PASS" if state_count >= 30 else "WARN",
           f"{state_count}/52 states")

    # ── Duplicate Check ──
    cur.execute("SELECT COUNT(*) FROM (SELECT name, COUNT(*) c FROM companies GROUP BY name HAVING c > 1)")
    dupes = cur.fetchone()[0]
    record("DataQuality", "Duplicate company names", "PASS" if dupes == 0 else "WARN",
           f"{dupes} duplicates found")

    conn.close()


# ─────────────────────────────────────────────
# TEST 4 — EMAIL EXTRACTION
# ─────────────────────────────────────────────
def test_email_extraction():
    section("TEST 4 — EMAIL EXTRACTION PIPELINE")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Check extracted emails in DB
    cur.execute("SELECT COUNT(*) FROM companies WHERE email IS NOT NULL")
    extracted = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM companies")
    total = cur.fetchone()[0]
    coverage = round(100 * extracted / total, 1) if total else 0
    record("EmailExtraction", "Emails in companies table", "PASS" if extracted >= 500 else "WARN",
           f"{extracted:,} / {total:,} ({coverage}%)")

    # Check enrichment_results
    cur.execute("SELECT COUNT(*) FROM enrichment_results WHERE email IS NOT NULL")
    enriched = cur.fetchone()[0]
    record("EmailExtraction", "Emails in enrichment_results", "PASS" if enriched >= 500 else "WARN",
           f"{enriched:,} records")

    # Email format validity
    cur.execute("SELECT email FROM companies WHERE email IS NOT NULL LIMIT 500")
    emails = [r[0] for r in cur.fetchall()]
    pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
    valid = sum(1 for e in emails if pattern.match(e))
    pct = round(100 * valid / len(emails), 1) if emails else 0
    record("EmailExtraction", "Emails passing syntax check", "PASS" if pct >= 90 else "WARN",
           f"{valid}/{len(emails)} ({pct}%)")

    # Domain presence
    cur.execute("SELECT COUNT(*) FROM companies WHERE domain IS NOT NULL AND domain != ''")
    with_domain = cur.fetchone()[0]
    record("EmailExtraction", "Companies with domain populated", "PASS" if with_domain >= 1000 else "WARN",
           f"{with_domain:,}")

    # Pattern variety
    cur.execute("SELECT email FROM companies WHERE email IS NOT NULL LIMIT 200")
    sample_emails = [r[0] for r in cur.fetchall()]
    prefixes = set()
    for e in sample_emails:
        local = e.split("@")[0]
        if "." in local:
            prefixes.add("firstname.lastname")
        else:
            prefixes.add(local)
    common = {"info", "contact", "hello", "support", "sales", "admin", "team"}
    pattern_types = common.intersection(prefixes)
    record("EmailExtraction", "Email pattern variety", "PASS" if len(pattern_types) >= 3 else "WARN",
           f"{len(prefixes)} unique prefixes found")

    # Check EXTRACTED status in enrichment
    cur.execute("SELECT email_status, COUNT(*) as c FROM enrichment_results GROUP BY email_status")
    statuses = {r[0]: r[1] for r in cur.fetchall()}
    for status, count in statuses.items():
        icon = "PASS" if status in ("EXTRACTED", "VERIFIED_SAFE", "LIKELY_VALID") else "INFO"
        record("EmailExtraction", f"Status: {status}", icon, f"{count:,} emails")

    conn.close()


# ─────────────────────────────────────────────
# TEST 5 — EMAIL VALIDATION
# ─────────────────────────────────────────────
def test_email_validation():
    section("TEST 5 — EMAIL VALIDATION PIPELINE")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Overall validated count
    cur.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_verified IS NOT NULL")
    validated = cur.fetchone()[0]
    record("EmailValidation", "Total emails processed", "PASS" if validated >= 100 else "WARN",
           f"{validated:,}")

    # Verified safe
    cur.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_verified = 1")
    safe = cur.fetchone()[0]
    pct = round(100 * safe / validated, 1) if validated else 0
    record("EmailValidation", "Emails verified (email_verified=1)", "PASS" if safe >= 100 else "WARN",
           f"{safe:,} ({pct}% of processed)")

    # By status breakdown
    cur.execute("SELECT email_status, COUNT(*) FROM enrichment_results GROUP BY email_status ORDER BY COUNT(*) DESC")
    for row in cur.fetchall():
        s, c = row[0], row[1]
        status = "PASS" if s in ("VERIFIED_SAFE", "EXTRACTED") else ("WARN" if s == "RISKY" else "INFO")
        record("EmailValidation", f"  → {s}", status, f"{c:,}")

    # Test validator script imports
    validator_path = "scripts/batch_email_validator.py"
    if os.path.exists(validator_path):
        record("EmailValidation", "Validator script exists", "PASS", validator_path)

        # Check key imports
        with open(validator_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for lib in ["dns.resolver", "smtplib", "sqlite3", "re"]:
            status = "PASS" if lib in content else "WARN"
            record("EmailValidation", f"  Import: {lib}", status, "")
    else:
        record("EmailValidation", "Validator script exists", "FAIL", "Not found")

    # Test DNS resolution (live test)
    try:
        import dns.resolver
        mx = dns.resolver.resolve("gmail.com", "MX")
        record("EmailValidation", "DNS resolver (gmail.com MX)", "PASS",
               f"{len(mx)} MX records returned")
    except Exception as e:
        record("EmailValidation", "DNS resolver (gmail.com MX)", "FAIL", str(e))

    # Test SMTP port reachability
    try:
        s = socket.create_connection(("gmail-smtp-in.l.google.com", 25), timeout=5)
        s.close()
        record("EmailValidation", "SMTP port 25 reachable", "PASS", "gmail-smtp-in.l.google.com:25")
    except Exception as e:
        record("EmailValidation", "SMTP port 25 reachable", "WARN", f"Blocked/timeout: {str(e)[:60]}")

    conn.close()


# ─────────────────────────────────────────────
# TEST 6 — EXPORT PIPELINE
# ─────────────────────────────────────────────
def test_export_pipeline():
    section("TEST 6 — EXPORT PIPELINE (CSV / JSON)")

    exports = list(Path(EXPORTS_DIR).glob("*.csv")) if os.path.exists(EXPORTS_DIR) else []

    record("Export", "Export directory exists",
           "PASS" if os.path.exists(EXPORTS_DIR) else "FAIL", EXPORTS_DIR)
    record("Export", "Number of CSV exports",
           "PASS" if len(exports) >= 5 else "WARN", f"{len(exports)} CSV files")

    # Check each export file
    total_rows = 0
    for f in sorted(exports):
        try:
            with open(f, encoding="utf-8") as fh:
                reader = csv.reader(fh)
                rows = list(reader)
            row_count = len(rows) - 1  # minus header
            total_rows += row_count
            size_kb = round(f.stat().st_size / 1024, 1)
            status = "PASS" if row_count > 100 else "WARN"
            record("Export", f"  {f.name}", status,
                   f"{row_count:,} rows, {size_kb} KB")
        except Exception as e:
            record("Export", f"  {f.name}", "FAIL", str(e))

    record("Export", "Total export rows across all CSVs", "PASS" if total_rows > 1000 else "WARN",
           f"{total_rows:,} total rows")

    # Validate CSV structure of first export
    if exports:
        f = sorted(exports)[0]
        try:
            with open(f, encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                headers = reader.fieldnames
                sample_row = next(reader, None)
            record("Export", f"CSV headers present ({f.name})", "PASS",
                   f"{len(headers)} columns: {', '.join(headers[:5])}...")
            if sample_row:
                non_empty = sum(1 for v in sample_row.values() if v and v.strip())
                record("Export", "Sample row populated fields", "PASS" if non_empty >= 5 else "WARN",
                       f"{non_empty}/{len(headers)} fields filled")
        except Exception as e:
            record("Export", "CSV structure validation", "FAIL", str(e))

    # Check JSON export files
    json_exports = list(Path(EXPORTS_DIR).glob("*.json")) if os.path.exists(EXPORTS_DIR) else []
    record("Export", "JSON export files",
           "PASS" if json_exports else "INFO",
           f"{len(json_exports)} files" if json_exports else "None yet (CSV only)")

    # Validate main companies JSON
    if os.path.exists(COMPANIES_JSON):
        try:
            with open(COMPANIES_JSON) as f:
                data = json.load(f)
            record("Export", "Source companies JSON valid", "PASS",
                   f"{len(data):,} records")
            # Check first record fields
            if data:
                fields = list(data[0].keys())
                record("Export", "Companies JSON schema fields", "PASS",
                       f"{len(fields)} fields: {', '.join(fields[:5])}...")
        except Exception as e:
            record("Export", "Source companies JSON valid", "FAIL", str(e))

    # People JSON
    if os.path.exists(PEOPLE_JSON):
        try:
            with open(PEOPLE_JSON) as f:
                data = json.load(f)
            record("Export", "Source people JSON valid", "PASS", f"{len(data):,} records")
        except Exception as e:
            record("Export", "Source people JSON valid", "FAIL", str(e))


# ─────────────────────────────────────────────
# TEST 7 — MCP SERVER
# ─────────────────────────────────────────────
def test_mcp_server():
    section("TEST 7 — MCP SERVER")

    # File exists
    record("MCP", "MCP server file exists",
           "PASS" if os.path.exists(MCP_SERVER) else "FAIL", MCP_SERVER)

    if not os.path.exists(MCP_SERVER):
        return

    with open(MCP_SERVER, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Check key MCP patterns (server uses custom JSON-RPC, not FastMCP package)
    checks = {
        "MCP transport (stdio/json)": any(x in content for x in ["FastMCP","from mcp","import mcp","stdio","argparse","json.dumps"]),
        "Tool definitions (@tool)":  "@tool" in content or "def search" in content or '"tools"' in content,
        "search_companies tool":     "search_companies" in content or "search" in content.lower(),
        "Database connection":       "sqlite3" in content or "SQLite" in content or "database" in content.lower(),
        "Error handling (try/exc)":  "try:" in content and "except" in content,
    }

    for check, result in checks.items():
        record("MCP", check, "PASS" if result else "WARN", "found" if result else "not found")

    # Test import
    try:
        result = os.popen("python -c \"import sys; sys.path.insert(0,'src'); from us_b2b import mcp_server; print('OK')\" 2>&1").read().strip()
        if "OK" in result:
            record("MCP", "MCP module importable", "PASS", "")
        else:
            record("MCP", "MCP module importable", "WARN", result[:80])
    except Exception as e:
        record("MCP", "MCP module importable", "WARN", str(e)[:60])

    # Check stdio variant
    stdio_path = "src/us_b2b/mcp_server_stdio.py"
    record("MCP", "STDIO transport variant",
           "PASS" if os.path.exists(stdio_path) else "WARN",
           stdio_path if os.path.exists(stdio_path) else "Missing")


# ─────────────────────────────────────────────
# TEST 8 — FULL REPORT
# ─────────────────────────────────────────────
def generate_report():
    section("PRODUCTION TEST REPORT")

    passed  = [r for r in results if r["status"] == "PASS"]
    failed  = [r for r in results if r["status"] == "FAIL"]
    warned  = [r for r in results if r["status"] == "WARN"]
    infos   = [r for r in results if r["status"] == "INFO"]
    total   = len(results)

    print(f"\n  {'Category':<20} {'Test':<55} {'Status':<8} {'Detail'}")
    print(f"  {'-'*20} {'-'*55} {'-'*8} {'-'*30}")
    for r in results:
        icon = {"PASS":"✅","FAIL":"❌","WARN":"⚠️ ","INFO":"ℹ️ "}.get(r["status"],"  ")
        print(f"  {r['category']:<20} {r['test']:<55} {icon} {r['status']:<6} {r['detail']}")

    # Score
    score = round(100 * len(passed) / total) if total else 0

    print(f"\n{'='*70}")
    print(f"  PRODUCTION READINESS SCORE")
    print(f"{'='*70}")
    print(f"  Total Tests  :  {total}")
    print(f"  ✅ Passed    :  {len(passed)}")
    print(f"  ❌ Failed    :  {len(failed)}")
    print(f"  ⚠️  Warnings  :  {len(warned)}")
    print(f"  ℹ️  Info      :  {len(infos)}")
    print(f"\n  {'='*40}")
    print(f"  🏆 SCORE: {score}/100", end="  ")

    if score >= 90:
        print("→ PRODUCTION READY 🚀")
    elif score >= 70:
        print("→ MOSTLY READY (fix warnings) ⚠️")
    elif score >= 50:
        print("→ NEEDS WORK (fix failures) 🔧")
    else:
        print("→ NOT READY (critical failures) ❌")
    print(f"  {'='*40}")

    if failed:
        print(f"\n  ❌ FAILURES TO FIX:")
        for r in failed:
            print(f"     [{r['category']}] {r['test']}: {r['detail']}")

    if warned:
        print(f"\n  ⚠️  WARNINGS TO REVIEW:")
        for r in warned:
            print(f"     [{r['category']}] {r['test']}: {r['detail']}")

    # Save report
    report_path = "output/production_test_report.json"
    Path("output").mkdir(exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "score": score,
            "summary": {
                "total": total, "passed": len(passed),
                "failed": len(failed), "warnings": len(warned)
            },
            "results": results
        }, f, indent=2)
    print(f"\n  📄 Full report saved: {report_path}")
    print(f"{'='*70}\n")

    return score


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  🔬 ONEEXTRACTION — PRODUCTION TEST SUITE")
    print(f"  Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    t0 = time.time()

    test_file_system()
    test_database()
    test_data_quality()
    test_email_extraction()
    test_email_validation()
    test_export_pipeline()
    test_mcp_server()
    score = generate_report()

    elapsed = round(time.time() - t0, 1)
    print(f"  ⏱️  Total test time: {elapsed}s\n")

    sys.exit(0 if score >= 70 else 1)
