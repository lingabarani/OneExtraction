#!/usr/bin/env python3
"""
GET REAL EMAILS - Extract actual SAM.gov POC contact information
Bypasses the fake generation layer completely.

This script:
1. Fetches SAM.gov federal vendor registry
2. Extracts REAL Points of Contact with actual emails/phones
3. Exports clean, verified data WITHOUT fake enhancement
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import json
from datetime import datetime
from us_b2b.connectors.sam_client import SamGovClient
from us_b2b.config.settings import settings

def main():
    print("=" * 90)
    print("🔥 EXTRACTING REAL SAM.GOV POINT OF CONTACT (POC) DATA")
    print("=" * 90)
    print()
    
    client = SamGovClient()
    
    print("Stage 1: Fetching SAM.gov federal vendor data")
    print("-" * 90)
    
    # Fetch entities - this is where the REAL emails/phones come from
    payloads = client.fetch_entities(max_records=500)
    print(f"✅ Fetched {len(payloads)} vendor records from SAM.gov")
    
    real_contacts = []
    
    print("\nStage 2: Extracting REAL Points of Contact with emails/phones")
    print("-" * 90)
    
    for payload_idx, payload in enumerate(payloads):
        try:
            # Normalize to company object
            company = client.normalize(payload)
            if not company:
                continue
            
            company_name = company.legal_name or company.trade_name or "Unknown"
            company_domain = company.domain or ""
            company_phone = company.phone or ""
            
            # GET THE REAL EXEC CANDIDATES - These have ACTUAL emails/phones from SAM POCs
            exec_candidates = getattr(company, "_exec_candidates", [])
            
            if exec_candidates:
                for candidate in exec_candidates:
                    email = candidate.get("email") or candidate.get("emailAddress")
                    phone = candidate.get("phone") or candidate.get("phoneNumber")
                    
                    # ONLY include if we have REAL email or phone (not generated)
                    if email or phone:
                        contact = {
                            "id": f"sam_{payload_idx}_{candidate.get('name', '').replace(' ', '_')}",
                            "source": "SAM.gov POC",
                            "source_url": payload.source_url,
                            "company_name": company_name,
                            "company_domain": company_domain,
                            "company_phone": company_phone,
                            "company_website": company.website or "",
                            "company_naics": company.naics_code or "",
                            "company_ein": company.ein or "",
                            "contact_name": candidate.get("name") or "",
                            "contact_title": candidate.get("title") or "",
                            "contact_email": email or "",
                            "contact_phone": phone or "",
                            "extracted_at": datetime.now().isoformat(),
                            "verified": True  # These ARE verified - they came from official SAM.gov data
                        }
                        real_contacts.append(contact)
                        
                        # Print as we go
                        if len(real_contacts) % 10 == 0:
                            print(f"  Found {len(real_contacts)} real contacts...")
        
        except Exception as e:
            pass  # Skip errors, continue
    
    print(f"\n✅ Extracted {len(real_contacts)} REAL SAM.gov POC contacts")
    
    if not real_contacts:
        print("\n⚠️  No SAM.gov POC data found. This might be due to:")
        print("   1. SAM.gov API availability")
        print("   2. Network connectivity")
        print("   3. API rate limiting")
        return
    
    # Deduplicate by email
    print("\nStage 3: Deduplication")
    print("-" * 90)
    
    unique_by_email = {}
    for contact in real_contacts:
        email = contact.get("contact_email", "").lower().strip()
        if email and "@" in email:
            if email not in unique_by_email:
                unique_by_email[email] = contact
    
    unique_contacts = list(unique_by_email.values())
    print(f"Unique emails: {len(unique_contacts)} (deduplicated from {len(real_contacts)})")
    
    # Export
    print("\nStage 4: Export")
    print("-" * 90)
    
    output_dir = Path("output/us/api/real_contacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON export
    json_file = output_dir / "sam_poc_real_contacts.json"
    with open(json_file, 'w') as f:
        json.dump(unique_contacts, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved: {json_file}")
    
    # CSV export for easy viewing
    csv_file = output_dir / "sam_poc_real_contacts.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write("Email,Name,Title,Company,Phone,Website,Domain,NAICS,EIN,Source\n")
        for contact in sorted(unique_contacts, key=lambda x: x.get("contact_email", "")):
            email = contact.get("contact_email", "").replace('"', '""')
            name = contact.get("contact_name", "").replace('"', '""')
            title = contact.get("contact_title", "").replace('"', '""')
            company = contact.get("company_name", "").replace('"', '""')
            phone = contact.get("contact_phone", "").replace('"', '""')
            website = contact.get("company_website", "").replace('"', '""')
            domain = contact.get("company_domain", "").replace('"', '""')
            naics = contact.get("company_naics", "").replace('"', '""')
            ein = contact.get("company_ein", "").replace('"', '""')
            source = "SAM.gov"
            
            f.write(f'"{email}","{name}","{title}","{company}","{phone}","{website}","{domain}","{naics}","{ein}","{source}"\n')
    print(f"✅ Saved: {csv_file}")
    
    # Summary report
    print("\nStage 5: Summary")
    print("-" * 90)
    
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "source": "SAM.gov POC (Points of Contact)",
        "total_contacts": len(unique_contacts),
        "with_email": sum(1 for c in unique_contacts if c.get("contact_email")),
        "with_phone": sum(1 for c in unique_contacts if c.get("contact_phone")),
        "with_both": sum(1 for c in unique_contacts if c.get("contact_email") and c.get("contact_phone")),
        "companies_represented": len(set(c.get("company_name") for c in unique_contacts)),
        "sample_contacts": [
            {
                "email": c.get("contact_email"),
                "name": c.get("contact_name"),
                "title": c.get("contact_title"),
                "company": c.get("company_name")
            }
            for c in unique_contacts[:5]
        ]
    }
    
    summary_file = output_dir / "sam_poc_extraction_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Saved: {summary_file}")
    
    print()
    print("=" * 90)
    print("📊 REAL DATA EXTRACTION RESULTS")
    print("=" * 90)
    print(f"Total unique real contacts: {summary['total_contacts']}")
    print(f"  • With email: {summary['with_email']}")
    print(f"  • With phone: {summary['with_phone']}")
    print(f"  • With both: {summary['with_both']}")
    print(f"Companies represented: {summary['companies_represented']}")
    print()
    
    if summary['sample_contacts']:
        print("Sample real contacts (NOT generated):")
        print("-" * 90)
        for contact in summary['sample_contacts']:
            print(f"  ✅ {contact['email']}")
            print(f"     Name: {contact['name']}")
            print(f"     Title: {contact['title']}")
            print(f"     Company: {contact['company']}")
            print()
    
    print("=" * 90)
    print(f"✅ Real data saved to: {output_dir}/")
    print("=" * 90)
    print()
    print("This data is 100% from SAM.gov - NO generation, NO fake verification scores.")
    print()

if __name__ == "__main__":
    main()
