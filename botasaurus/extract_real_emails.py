#!/usr/bin/env python3
"""
Extract REAL emails and phone numbers from SAM.gov POC data.
Bypasses the fake generation layer - gets actual contact info from scraped sources.
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_real_emails_from_cache():
    """Extract real emails from SAM.gov cache files."""
    
    cache_dir = Path("cache")
    real_contacts = []
    
    # Find SAM cache files
    if cache_dir.exists():
        for cache_file in cache_dir.glob("**/fetch_sam_entities*/cache.json"):
            print(f"Reading: {cache_file}")
            try:
                with open(cache_file) as f:
                    cache_data = json.load(f)
                    
                    # Extract from cached responses
                    if isinstance(cache_data, dict):
                        entities = cache_data.get("entityData", []) or []
                        for entity in entities:
                            pocs = entity.get("pointsOfContact", {}) or {}
                            company_name = entity.get("entityRegistration", {}).get("legalBusinessName", "")
                            
                            # Extract each POC
                            for poc_type, poc_data in pocs.items():
                                if isinstance(poc_data, dict):
                                    email = poc_data.get("emailAddress") or poc_data.get("email")
                                    phone = poc_data.get("phoneNumber") or poc_data.get("usPhone")
                                    first_name = poc_data.get("firstName", "")
                                    last_name = poc_data.get("lastName", "")
                                    title = poc_data.get("title", "")
                                    
                                    if email or phone:
                                        real_contacts.append({
                                            "source": "SAM.gov POC Cache",
                                            "company_name": company_name,
                                            "first_name": first_name,
                                            "last_name": last_name,
                                            "full_name": f"{first_name} {last_name}".strip(),
                                            "title": title,
                                            "email": email,
                                            "phone": phone,
                                            "poc_type": poc_type,
                                            "extracted_at": datetime.now().isoformat()
                                        })
            except Exception as e:
                print(f"  Error reading {cache_file}: {e}")
    
    return real_contacts


def extract_real_emails_from_companies():
    """Extract real emails from companies.json _exec_candidates attribute."""
    
    companies_file = Path("output/us/api/companies/us_companies.json")
    real_contacts = []
    
    if not companies_file.exists():
        return real_contacts
    
    print(f"\nReading: {companies_file}")
    
    try:
        with open(companies_file) as f:
            companies = json.load(f)
            
            for company in companies:
                company_id = company.get("company_id", "")
                legal_name = company.get("legal_name", "")
                domain = company.get("domain", "")
                phone = company.get("phone", "")
                emails = company.get("emails", []) or []
                
                # Extract company-level emails
                for email_item in emails:
                    if isinstance(email_item, dict):
                        email_val = email_item.get("value") or email_item.get("email")
                        source = email_item.get("source", "UNKNOWN")
                        
                        if email_val:
                            real_contacts.append({
                                "source": f"Company Email ({source})",
                                "company_name": legal_name,
                                "company_domain": domain,
                                "email": email_val,
                                "phone": phone,
                                "type": "company_email",
                                "extracted_at": datetime.now().isoformat()
                            })
    except Exception as e:
        print(f"  Error reading companies: {e}")
    
    return real_contacts


def extract_real_emails_from_raw_people():
    """Extract real emails from raw people file - those with actual emails."""
    
    people_file = Path("output/us/api/people/us_people.json")
    real_contacts = []
    
    if not people_file.exists():
        return real_contacts
    
    print(f"\nReading: {people_file}")
    
    try:
        with open(people_file) as f:
            people = json.load(f)
            
            for person in people:
                email = person.get("work_email") or person.get("email")
                phone = person.get("direct_phone") or person.get("phone")
                email_status = person.get("email_status", "")
                
                # Only include if email is marked as VERIFIED (not PROBABLE/generated)
                if email and email_status == "VERIFIED" and "@" in str(email):
                    real_contacts.append({
                        "source": "Raw People (Verified Email)",
                        "first_name": person.get("first_name", ""),
                        "last_name": person.get("last_name", ""),
                        "full_name": person.get("full_name", ""),
                        "company_name": person.get("company_name", ""),
                        "title": person.get("title", ""),
                        "email": email,
                        "phone": phone,
                        "email_status": email_status,
                        "email_confidence": person.get("email_confidence_score", 0),
                        "extracted_at": datetime.now().isoformat()
                    })
    except Exception as e:
        print(f"  Error reading raw people: {e}")
    
    return real_contacts


def main():
    print("=" * 80)
    print("🔍 EXTRACTING REAL EMAILS FROM SAM.GOV & SOURCE DATA")
    print("=" * 80)
    print()
    
    all_contacts = []
    
    # Extract from all sources
    print("Stage 1: SAM.gov Cache Files")
    print("-" * 80)
    sam_contacts = extract_real_emails_from_cache()
    print(f"Found {len(sam_contacts)} contacts from SAM cache")
    all_contacts.extend(sam_contacts)
    
    print("\nStage 2: Companies File")
    print("-" * 80)
    company_contacts = extract_real_emails_from_companies()
    print(f"Found {len(company_contacts)} company-level emails")
    all_contacts.extend(company_contacts)
    
    print("\nStage 3: Raw People File (Verified Only)")
    print("-" * 80)
    people_contacts = extract_real_emails_from_raw_people()
    print(f"Found {len(people_contacts)} verified emails from raw people")
    all_contacts.extend(people_contacts)
    
    # Deduplicate by email
    print("\nStage 4: Deduplication")
    print("-" * 80)
    unique_emails = {}
    for contact in all_contacts:
        email = contact.get("email", "").lower() if contact.get("email") else ""
        if email and "@" in email:
            if email not in unique_emails:
                unique_emails[email] = contact
            else:
                # Keep the one with more info
                if len(str(contact)) > len(str(unique_emails[email])):
                    unique_emails[email] = contact
    
    unique_contacts = list(unique_emails.values())
    print(f"Unique emails: {len(unique_contacts)} (deduplicated from {len(all_contacts)})")
    
    # Save results
    print("\nStage 5: Export")
    print("-" * 80)
    
    output_dir = Path("output/us/api/real_emails")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save full JSON
    full_file = output_dir / "real_emails_complete.json"
    with open(full_file, 'w') as f:
        json.dump(unique_contacts, f, indent=2)
    print(f"✅ Saved: {full_file}")
    
    # Save CSV for easy viewing
    csv_file = output_dir / "real_emails.csv"
    with open(csv_file, 'w') as f:
        f.write("Email,Full Name,Company,Title,Phone,Source,Confidence\n")
        for contact in sorted(unique_contacts, key=lambda x: x.get("email", "")):
            email = contact.get("email", "").replace('"', '""')
            name = contact.get("full_name", "").replace('"', '""')
            company = contact.get("company_name", "").replace('"', '""')
            title = contact.get("title", "").replace('"', '""')
            phone = contact.get("phone", "").replace('"', '""')
            source = contact.get("source", "").replace('"', '""')
            confidence = contact.get("email_confidence", contact.get("email_status", ""))
            
            f.write(f'"{email}","{name}","{company}","{title}","{phone}","{source}","{confidence}"\n')
    print(f"✅ Saved: {csv_file}")
    
    # Save summary
    summary = {
        "extraction_date": datetime.now().isoformat(),
        "total_unique_emails": len(unique_contacts),
        "breakdown": {
            "sam_poc_cache": len([c for c in unique_contacts if "SAM.gov POC" in c.get("source", "")]),
            "company_emails": len([c for c in unique_contacts if "Company Email" in c.get("source", "")]),
            "verified_people": len([c for c in unique_contacts if "Raw People" in c.get("source", "")])
        },
        "sample_emails": [c.get("email") for c in unique_contacts[:5]]
    }
    
    summary_file = output_dir / "extraction_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Saved: {summary_file}")
    
    print()
    print("=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    print(f"Total unique real emails extracted: {len(unique_contacts)}")
    print(f"\nBreakdown:")
    print(f"  • SAM.gov POC cache: {summary['breakdown']['sam_poc_cache']}")
    print(f"  • Company-level emails: {summary['breakdown']['company_emails']}")
    print(f"  • Verified from raw people: {summary['breakdown']['verified_people']}")
    print()
    
    if unique_contacts:
        print("Sample real emails:")
        for contact in unique_contacts[:5]:
            print(f"  ✓ {contact.get('email')} - {contact.get('full_name', 'N/A')} @ {contact.get('company_name', 'N/A')}")
    
    print()
    print("💾 All files saved to: output/us/api/real_emails/")
    print()


if __name__ == "__main__":
    main()
