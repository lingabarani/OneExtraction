"""
Email Validation Statistics Dashboard
"""

import sqlite3
from pathlib import Path

def show_dashboard():
    """Show email validation statistics"""
    db_path = "output/us/api/oneextraction.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("\n" + "=" * 70)
    print("📊 EMAIL VALIDATION STATISTICS DASHBOARD")
    print("=" * 70 + "\n")
    
    # Total companies
    cursor.execute("SELECT COUNT(*) FROM companies")
    total_companies = cursor.fetchone()[0]
    
    # Companies with emails
    cursor.execute("SELECT COUNT(*) FROM companies WHERE email IS NOT NULL")
    companies_with_email = cursor.fetchone()[0]
    
    # Email validation counts
    cursor.execute("""
    SELECT 
        email_status,
        COUNT(*) as count
    FROM enrichment_results
    GROUP BY email_status
    """)
    
    status_counts = {}
    for status, count in cursor.fetchall():
        status_counts[status] = count
    
    # Totals
    cursor.execute("SELECT COUNT(*) FROM enrichment_results")
    total_validated = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_verified = 1")
    verified_count = cursor.fetchone()[0]
    
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
    SELECT 
        c.industry,
        COUNT(*) as count
    FROM enrichment_results er
    JOIN companies c ON er.company_id = c.id
    WHERE er.email_status = 'VERIFIED_SAFE'
    GROUP BY c.industry
    ORDER BY count DESC
    LIMIT 10
    """)
    
    for industry, count in cursor.fetchall():
        print(f"  {industry:<40} {count:>6} emails")
    
    # By state
    print(f"\n🗺️  TOP STATES BY VERIFIED EMAILS")
    cursor.execute("""
    SELECT 
        c.state_code,
        COUNT(*) as count
    FROM enrichment_results er
    JOIN companies c ON er.company_id = c.id
    WHERE er.email_status = 'VERIFIED_SAFE'
    GROUP BY c.state_code
    ORDER BY count DESC
    LIMIT 10
    """)
    
    for state, count in cursor.fetchall():
        print(f"  {state:<5} {count:>6} emails")
    
    print("\n" + "=" * 70 + "\n")
    
    conn.close()

if __name__ == "__main__":
    show_dashboard()
