import sqlite3

conn = sqlite3.connect('output/us/api/oneextraction.db')
cursor = conn.cursor()

# Get stats
cursor.execute('SELECT COUNT(*) FROM companies')
total_companies = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM companies WHERE email IS NOT NULL')
companies_with_email = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_status = 'EXTRACTED'")
extracted = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM enrichment_results WHERE email_verified = 1')
verified = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM enrichment_results WHERE email_status = 'VERIFIED_SAFE'")
verified_safe = cursor.fetchone()[0]

print(f'Total companies:          {total_companies:,}')
print(f'Companies with emails:    {companies_with_email:,}')
print(f'Emails extracted:         {extracted:,}')
print(f'Emails verified:          {verified:,}')
print(f'Emails verified safe:     {verified_safe:,}')

conn.close()
