"""
OneExtraction — PostgreSQL Production Verification
Final check: schema, data integrity, query performance, all scripts.
"""

import time
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("❌ psycopg2 not installed"); sys.exit(1)

try:
    from db_connector import get_connection, get_cursor, db_info, DB_TYPE
except ImportError:
    print("❌ db_connector.py missing"); sys.exit(1)

# ── helpers ────────────────────────────────────────────────────────────────────
results = []
def record(cat, test, status, detail=""):
    results.append({"cat": cat, "test": test, "status": status, "detail": detail})
    icon = {"PASS":"✅","FAIL":"❌","WARN":"⚠️ ","INFO":"ℹ️ "}.get(status,"  ")
    print(f"  {icon} {test:<52} {detail}")

def section(t):
    print(f"\n{'='*65}\n  {t}\n{'='*65}")

def val(cur, q, p=()):
    cur.execute(q, p)
    r = cur.fetchone()
    return r[0] if isinstance(r,(list,tuple)) else list(r.values())[0]

# ── connect ────────────────────────────────────────────────────────────────────
section("CONNECTING TO POSTGRESQL")
try:
    conn = get_connection()
    cur  = get_cursor(conn)
    record("Conn","DB type active","PASS", DB_TYPE.upper())
    record("Conn","Connection target","PASS", db_info())
except Exception as e:
    record("Conn","Connect","FAIL",str(e)); sys.exit(1)

# ── TEST 1: Schema ─────────────────────────────────────────────────────────────
section("TEST 1 — SCHEMA VERIFICATION")

# Tables
cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public' ORDER BY table_name
""")
tables = [r[0] if isinstance(r,(list,tuple)) else r["table_name"] for r in cur.fetchall()]
for t in ["companies","enrichment_results","people","processing_log"]:
    record("Schema", f"Table: {t}", "PASS" if t in tables else "FAIL",
           "exists" if t in tables else "MISSING")

# Indexes
cur.execute("""
    SELECT indexname FROM pg_indexes WHERE schemaname = 'public'
""")
indexes = [r[0] if isinstance(r,(list,tuple)) else r["indexname"] for r in cur.fetchall()]
record("Schema","Indexes","PASS" if len(indexes)>=14 else "WARN", f"{len(indexes)} indexes")

expected_idx = [
    "idx_companies_domain","idx_companies_state","idx_companies_industry",
    "idx_companies_ein",  "idx_people_company", "idx_people_email",
    "idx_enrichment_company","idx_enrichment_status","idx_enrichment_verified"
]
for idx in expected_idx:
    record("Schema", f"  index: {idx}",
           "PASS" if idx in indexes else "FAIL",
           "found" if idx in indexes else "MISSING")

# FK constraints
cur.execute("""
    SELECT COUNT(*) FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public'
""")
fk_count = val(cur, """
    SELECT COUNT(*) FROM information_schema.table_constraints
    WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public'
""")
record("Schema","Foreign key constraints","PASS" if fk_count>=2 else "WARN", f"{fk_count} FKs")

# Column check on companies
cur.execute("""
    SELECT column_name FROM information_schema.columns
    WHERE table_name='companies' AND table_schema='public'
    ORDER BY ordinal_position
""")
cols = [r[0] if isinstance(r,(list,tuple)) else r["column_name"] for r in cur.fetchall()]
required_cols = ["id","name","domain","email","industry","state_code","data_quality_score"]
for c in required_cols:
    record("Schema", f"  companies.{c}", "PASS" if c in cols else "FAIL",
           "present" if c in cols else "MISSING")

# ── TEST 2: Data Counts ────────────────────────────────────────────────────────
section("TEST 2 — DATA COUNTS")

companies  = val(cur,"SELECT COUNT(*) FROM companies")
people     = val(cur,"SELECT COUNT(*) FROM people")
enrichment = val(cur,"SELECT COUNT(*) FROM enrichment_results")
proc_log   = val(cur,"SELECT COUNT(*) FROM processing_log")

record("Data","companies rows",   "PASS" if companies>=1000  else "FAIL", f"{companies:,}")
record("Data","people rows",      "PASS" if people>=2000     else "FAIL", f"{people:,}")
record("Data","enrichment rows",  "PASS" if enrichment>=1000 else "FAIL", f"{enrichment:,}")
record("Data","processing_log",   "PASS" if proc_log>=1      else "WARN", f"{proc_log} entries")

# ── TEST 3: Data Quality ───────────────────────────────────────────────────────
section("TEST 3 — DATA QUALITY")

def pct(n,d): return round(100*n/d,1) if d else 0

with_name   = val(cur,"SELECT COUNT(*) FROM companies WHERE name IS NOT NULL")
with_domain = val(cur,"SELECT COUNT(*) FROM companies WHERE domain IS NOT NULL")
with_email  = val(cur,"SELECT COUNT(*) FROM companies WHERE email IS NOT NULL")
with_ind    = val(cur,"SELECT COUNT(*) FROM companies WHERE industry IS NOT NULL")
with_state  = val(cur,"SELECT COUNT(*) FROM companies WHERE state_code IS NOT NULL")
avg_score   = val(cur,"SELECT ROUND(AVG(data_quality_score),1) FROM companies WHERE data_quality_score IS NOT NULL")

record("Quality","name coverage",     "PASS" if pct(with_name,companies)==100 else "WARN",
       f"{with_name:,} ({pct(with_name,companies)}%)")
record("Quality","domain coverage",   "PASS" if pct(with_domain,companies)>=80 else "WARN",
       f"{with_domain:,} ({pct(with_domain,companies)}%)")
record("Quality","email coverage",    "PASS" if pct(with_email,companies)>=60  else "WARN",
       f"{with_email:,} ({pct(with_email,companies)}%)")
record("Quality","industry coverage", "PASS" if pct(with_ind,companies)>=80   else "WARN",
       f"{with_ind:,} ({pct(with_ind,companies)}%)")
record("Quality","state coverage",    "PASS" if pct(with_state,companies)==100 else "WARN",
       f"{with_state:,} ({pct(with_state,companies)}%)")
record("Quality","avg quality score", "PASS" if float(avg_score or 0)>=50     else "WARN",
       f"{avg_score}/100")

# Duplicates
dup = val(cur,"SELECT COUNT(*) FROM (SELECT name FROM companies GROUP BY name HAVING COUNT(*)>1) x")
record("Quality","zero duplicate names","PASS" if dup==0 else "WARN", f"{dup} duplicates")

# People coverage
ppl_cos = val(cur,"SELECT COUNT(DISTINCT company_id) FROM people")
ratio   = round(people/ppl_cos,1) if ppl_cos else 0
record("Quality","exec coverage (companies)", "PASS" if ppl_cos==companies else "WARN",
       f"{ppl_cos:,}/{companies:,} companies covered")
record("Quality","exec per company (avg)",    "PASS" if ratio>=2.0 else "WARN",
       f"{ratio}x")

# ── TEST 4: Email Pipeline ─────────────────────────────────────────────────────
section("TEST 4 — EMAIL PIPELINE")

extracted    = val(cur,"SELECT COUNT(*) FROM enrichment_results WHERE email IS NOT NULL")
likely_valid = val(cur,"SELECT COUNT(*) FROM enrichment_results WHERE email_status='LIKELY_VALID'")
invalid_ct   = val(cur,"SELECT COUNT(*) FROM enrichment_results WHERE email_status='INVALID'")
verified_ct  = val(cur,"SELECT COUNT(*) FROM enrichment_results WHERE email_verified=TRUE")

record("Email","total emails in enrichment","PASS" if extracted>=1000 else "WARN",f"{extracted:,}")
record("Email","LIKELY_VALID emails",        "PASS" if likely_valid>=100 else "WARN",f"{likely_valid:,}")
record("Email","INVALID emails",             "INFO", f"{invalid_ct:,}")
record("Email","verified emails (True)",     "PASS" if verified_ct>=100  else "WARN",f"{verified_ct:,}")

# Sample email syntax
import re
cur.execute("SELECT email FROM enrichment_results WHERE email IS NOT NULL LIMIT 200")
emails = [r[0] if isinstance(r,(list,tuple)) else r["email"] for r in cur.fetchall()]
pat = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
good = sum(1 for e in emails if e and pat.match(e))
pct_good = round(100*good/len(emails),1) if emails else 0
record("Email","email syntax valid (sample)","PASS" if pct_good>=95 else "WARN",
       f"{good}/{len(emails)} ({pct_good}%)")

# ── TEST 5: Query Performance ──────────────────────────────────────────────────
section("TEST 5 — QUERY PERFORMANCE")

queries = {
    "Full table scan companies":     "SELECT COUNT(*) FROM companies",
    "Filter by state (NY)":          "SELECT COUNT(*) FROM companies WHERE state_code='NY'",
    "Filter by industry":            "SELECT COUNT(*) FROM companies WHERE industry LIKE '%Tech%'",
    "JOIN companies+enrichment":     "SELECT COUNT(*) FROM enrichment_results er JOIN companies c ON er.company_id=c.id",
    "JOIN companies+people":         "SELECT COUNT(*) FROM people p JOIN companies c ON p.company_id=c.id",
    "GROUP BY industry":             "SELECT industry, COUNT(*) FROM companies GROUP BY industry ORDER BY COUNT(*) DESC LIMIT 5",
    "Email status breakdown":        "SELECT email_status, COUNT(*) FROM enrichment_results GROUP BY email_status",
    "Top states":                    "SELECT state_code, COUNT(*) FROM companies GROUP BY state_code ORDER BY COUNT(*) DESC LIMIT 10",
}

for name, query in queries.items():
    t0 = time.time()
    cur.execute(query)
    cur.fetchall()
    ms = round((time.time()-t0)*1000, 1)
    status = "PASS" if ms < 500 else ("WARN" if ms < 2000 else "FAIL")
    record("Perf", name, status, f"{ms}ms")

# ── TEST 6: Connector + Scripts ────────────────────────────────────────────────
section("TEST 6 — DB CONNECTOR & SCRIPTS")

record("Scripts","db_connector.py exists","PASS" if Path("db_connector.py").exists() else "FAIL","")
record("Scripts",".env written",          "PASS" if Path(".env").exists() else "FAIL","")
record("Scripts","db_config.py written",  "PASS" if Path("db_config.py").exists() else "FAIL","")

# Verify .env has correct entries
if Path(".env").exists():
    env_text = Path(".env").read_text()
    for key in ["DATABASE_TYPE=postgresql","DATABASE_HOST","DATABASE_PORT=5432",
                "DATABASE_NAME=oneextraction","DATABASE_URL"]:
        record("Scripts",f"  .env: {key.split('=')[0]}",
               "PASS" if key.split("=")[0] in env_text else "FAIL",
               "present" if key.split("=")[0] in env_text else "missing")

for script in ["check_stats.py","email_stats_dashboard.py",
               "export_verified_emails.py"]:   # setup_postgres.py intentionally uses sqlite3 (migration tool)
    exists = Path(script).exists()
    if exists:
        txt = Path(script).read_text(encoding="utf-8", errors="ignore")
        uses_connector = "db_connector" in txt
        record("Scripts",f"{script}",
               "PASS" if uses_connector else "WARN",
               "uses db_connector ✅" if uses_connector else "still uses sqlite3 directly ⚠️")
    else:
        record("Scripts",script,"FAIL","missing")

for script in ["scripts/email_extractor.py","scripts/batch_email_validator.py"]:
    if Path(script).exists():
        txt = Path(script).read_text(encoding="utf-8",errors="ignore")
        record("Scripts",script,"PASS" if "db_connector" in txt else "WARN",
               "uses db_connector ✅" if "db_connector" in txt else "sqlite3 direct ⚠️")

# ── TEST 7: pgAdmin Visibility ─────────────────────────────────────────────────
section("TEST 7 — PGADMIN VISIBILITY CHECK")

# Verify DB is visible to pg_catalog (what pgAdmin reads)
cur.execute("SELECT datname FROM pg_database WHERE datistemplate=FALSE ORDER BY datname")
dbs = [r[0] if isinstance(r,(list,tuple)) else r["datname"] for r in cur.fetchall()]
record("pgAdmin","oneextraction DB in pg_catalog","PASS" if "oneextraction" in dbs else "FAIL",
       f"Databases: {', '.join(dbs)}")

cur.execute("SELECT schemaname, tablename, tableowner FROM pg_tables WHERE schemaname='public'")
pg_tables = cur.fetchall()
record("pgAdmin","Tables visible in public schema","PASS" if len(pg_tables)>=4 else "FAIL",
       f"{len(pg_tables)} tables")

# Table sizes (pg_relation_size)
cur.execute("""
    SELECT relname, pg_size_pretty(pg_relation_size(oid)) as size
    FROM pg_class
    WHERE relkind='r' AND relnamespace=(SELECT oid FROM pg_namespace WHERE nspname='public')
    ORDER BY pg_relation_size(oid) DESC
""")
for row in cur.fetchall():
    r = dict(row) if hasattr(row,'keys') else {"relname":row[0],"size":row[1]}
    record("pgAdmin",f"  table size: {r['relname']}","INFO",str(r['size']))

conn.close()

# ── FINAL REPORT ───────────────────────────────────────────────────────────────
section("FINAL PRODUCTION REPORT")

passed = [r for r in results if r["status"]=="PASS"]
failed = [r for r in results if r["status"]=="FAIL"]
warned = [r for r in results if r["status"]=="WARN"]
infos  = [r for r in results if r["status"]=="INFO"]
total  = len(results)
score  = round(100*len(passed)/total) if total else 0

print(f"\n  {'Category':<12} {'Test':<52} {'Status':<6} Detail")
print(f"  {'-'*12} {'-'*52} {'-'*6} {'-'*25}")
for r in results:
    icon = {"PASS":"✅","FAIL":"❌","WARN":"⚠️ ","INFO":"ℹ️ "}.get(r["status"],"  ")
    print(f"  {r['cat']:<12} {r['test']:<52} {icon}{r['status']:<5} {r['detail']}")

print(f"\n{'='*65}")
print(f"  POSTGRESQL PRODUCTION READINESS")
print(f"{'='*65}")
print(f"  Total  : {total}  |  ✅ {len(passed)}  ❌ {len(failed)}  ⚠️  {len(warned)}  ℹ️  {len(infos)}")
print(f"\n  {'='*35}")
print(f"  🏆 SCORE: {score}/100", end="  ")
verdict = ("→ POSTGRESQL PRODUCTION READY 🚀" if score>=90
           else "→ MOSTLY READY (review warnings) ⚠️" if score>=70
           else "→ NEEDS FIXES ❌")
print(verdict)
print(f"  {'='*35}")

if failed:
    print(f"\n  ❌ FAILURES:")
    for r in failed: print(f"     [{r['cat']}] {r['test']}: {r['detail']}")
if warned:
    print(f"\n  ⚠️  WARNINGS:")
    for r in warned: print(f"     [{r['cat']}] {r['test']}: {r['detail']}")

import json
report = {
    "generated_at": datetime.now().isoformat(),
    "database":     db_info(),
    "score":        score,
    "summary":      {"total":total,"passed":len(passed),"failed":len(failed),"warnings":len(warned)},
    "results":      results
}
out = Path("output/postgres_production_report.json")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2))
print(f"\n  📄 Report: {out}")
print(f"{'='*65}\n")

sys.exit(0 if score>=90 else 1)
