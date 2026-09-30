"""
Export verified safe emails to CSV
"""

import sqlite3
import csv
from pathlib import Path

def export_verified_emails():
    """Export verified safe emails to CSV"""
    db_path = "output/us/api/oneextraction.db"
    output_file = "output/exports/verified_emails.csv"
    
    # Create output directory if needed
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get verified safe emails
    cursor.execute("""
    SELECT 
        c.id,
        c.name as company_name,
        c.domain,
        c.industry,
        c.state_code,
        er.email,
        er.email_status,
        er.email_verified,
        er.created_at
    FROM enrichment_results er
    JOIN companies c ON er.company_id = c.id
    WHERE er.email_status = 'VERIFIED_SAFE'
    ORDER BY c.name
    """)
    
    rows = cursor.fetchall()
    total = len(rows)
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Company ID',
            'Company Name',
            'Domain',
            'Industry',
            'State',
            'Email',
            'Status',
            'Verified',
            'Validated At'
        ])
        
        # Rows
        for row in rows:
            writer.writerow([
                row['id'],
                row['company_name'],
                row['domain'],
                row['industry'],
                row['state_code'],
                row['email'],
                row['email_status'],
                'Yes' if row['email_verified'] else 'No',
                row['created_at']
            ])
    
    conn.close()
    
    print(f"✅ Exported {total} verified emails")
    print(f"📁 File: {output_file}")
    print(f"📊 Ready for sales team!")
    
    return total

if __name__ == "__main__":
    count = export_verified_emails()
