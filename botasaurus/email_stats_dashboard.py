"""
Email Validation Statistics Dashboard
"""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from db_connector import get_connection, get_cursor, db_info
    _USE_CONNECTOR = True
except ImportError:
    _USE_CONNECTOR = False

def _val(cursor, q, params=()):
    cursor.execute(q, params)
    r = cursor.fetchone()
    return r[0] if isinstance(r, (list, tuple)) else list(r.values())[0]

def show_dashboard():
    """Show email validation statistics"""
    if _USE_CONNECTOR:
        conn   = get_connection()
        cursor = get_cursor(conn)
        print(f"\n🔌 Connected to: {db_info()}")
    else:
        conn   = sqlite3.connect("output/us/api/oneextraction.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

    print("\n" + "=" * 70)
    print("📊 EMAIL VALIDATION STATISTICS DASHBOARD")
    print("=" * 70 + "\n")

    total_companies      = _val(cursor, "SELECT COUNT(*) FROM companies")
    companies_with_email = _val(cursor, "SELECT COUNT(*) FROM companies WHERE email IS NOT NULL")
    total_validated      = _val(cursor, "SELECT COUNT(*) FROM enrichment_results")
    verified_count       = _val(cursor, "SELECT COUNT(*) FROM enrichment_results WHERE email_verified = TRUE")

    # Email status breakdown
    cursor.execute("SELECT email_status, COUNT(*) as count FROM enrichment_results GROUP BY email_status")
    rows = cursor.fetchall()
    status_counts = {}
    for row in rows:
        r = dict(row) if hasattr(row, 'keys') else {"email_status": row[0], "count": row[1]}
        status_counts[r["email_status"]] = r["count"]

    print(f"📈 OVERVIEW")
    print(f"  Total Companies:           {total_companies:,}")
    print(f"  Companies with Emails:     {companies_with_email:,} ({100*companies_with_email/total_companies:.1f}%)")
    print(f"  Total Validated:           {total_validated:,}")
    print(f"  Verified (True):           {verified_count:,}")

    print(f"\n📧 VALIDATION BREAKDOWN")
    print(f"  VERIFIED_SAFE:             {status_counts.get('VERIFIED_SAFE', 0):,} ✅")
    print(f"  LIKELY_VALID:              {status_counts.get('LIKELY_VALID', 0):,} ⚠️")
    print(f"  RISKY:                     {status_counts.get('RISKY', 0):,} ⚠️")
    print(f"  INVALID:                   {status_counts.get('INVALID', 0):,} ❌")
    print(f"  EXTRACTED (Not yet Val):   {status_counts.get('EXTRACTED', 0):,} ⏳")

    if total_validated > 0:
        safe_rate = 100 * status_counts.get('VERIFIED_SAFE', 0) / total_validated
        print(f"\n✅ VERIFIED SAFE RATE:         {safe_rate:.1f}%")

    # By industry
    print(f"\n🏭 TOP INDUSTRIES BY VERIFIED EMAILS")
    cursor.execute("""
        SELECT c.industry, COUNT(*) as count
        FROM enrichment_results er
        JOIN companies c ON er.company_id = c.id
        WHERE er.email_status = 'VERIFIED_SAFE'
        GROUP BY c.industry ORDER BY count DESC LIMIT 10
    """)
    for row in cursor.fetchall():
        r = dict(row) if hasattr(row, 'keys') else {"industry": row[0], "count": row[1]}
        print(f"  {str(r.get('industry','')):<40} {r.get('count',0):>6} emails")

    # By state
    print(f"\n🗺️  TOP STATES BY VERIFIED EMAILS")
    cursor.execute("""
        SELECT c.state_code, COUNT(*) as count
        FROM enrichment_results er
        JOIN companies c ON er.company_id = c.id
        WHERE er.email_status = 'VERIFIED_SAFE'
        GROUP BY c.state_code ORDER BY count DESC LIMIT 10
    """)
    for row in cursor.fetchall():
        r = dict(row) if hasattr(row, 'keys') else {"state_code": row[0], "count": row[1]}
        print(f"  {str(r.get('state_code','')):<5} {r.get('count',0):>6} emails")

    print("\n" + "=" * 70 + "\n")
    conn.close()

if __name__ == "__main__":
    show_dashboard()
