import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
try:
    from db_connector import get_connection, get_cursor, db_info
    conn = get_connection()
    cursor = get_cursor(conn)
    print(f"Connected to: {db_info()}")
except Exception:
    import sqlite3
    conn = sqlite3.connect('output/us/api/oneextraction.db')
    cursor = conn.cursor()

def _count(q):
    cursor.execute(q)
    r = cursor.fetchone()
    return r[0] if isinstance(r, (list,tuple)) else list(r.values())[0]

# Get stats — works for both PostgreSQL and SQLite
def _val(q):
    cursor.execute(q)
    r = cursor.fetchone()
    return r[0] if isinstance(r, (list, tuple)) else list(r.values())[0]

total_companies      = _val('SELECT COUNT(*) FROM companies')
companies_with_email = _val('SELECT COUNT(*) FROM companies WHERE email IS NOT NULL')
extracted     = _val("SELECT COUNT(*) FROM enrichment_results WHERE email_status = 'EXTRACTED'")
verified      = _val('SELECT COUNT(*) FROM enrichment_results WHERE email_verified = TRUE')
verified_safe = _val("SELECT COUNT(*) FROM enrichment_results WHERE email_status = 'VERIFIED_SAFE'")

print(f'Total companies:          {total_companies:,}')
print(f'Companies with emails:    {companies_with_email:,}')
print(f'Emails extracted:         {extracted:,}')
print(f'Emails verified:          {verified:,}')
print(f'Emails verified safe:     {verified_safe:,}')

conn.close()
