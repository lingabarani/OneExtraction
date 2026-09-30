#!/usr/bin/env python3
"""Extract and list all emails and phone numbers from real data export."""

import json
from pathlib import Path
from collections import defaultdict

def extract_contacts():
    """Extract all emails and phones from real data JSON files."""
    
    companies_file = Path("output/us/api/companies/us_companies_real_data_only.json")
    people_file = Path("output/us/api/people/us_people_real_data_only.json")
    
    print("\n" + "="*100)
    print("EMAILS AND PHONE NUMBERS FROM REAL DATA EXPORT")
    print("="*100 + "\n")
    
    # Load data
    with open(companies_file) as f:
        companies = json.load(f)
    
    with open(people_file) as f:
        people = json.load(f)
    
    # Extract company contacts
    print("COMPANY EMAIL AND PHONE CONTACTS")
    print("-" * 100)
    
    company_emails = []
    company_phones = []
    company_map = {c['company_id']: c['legal_name'] for c in companies}
    
    for company in companies:
        if company.get('email'):
            company_emails.append({
                'company': company.get('legal_name'),
                'email': company.get('email'),
                'source': company.get('source_records', [{}])[0].get('source', 'Unknown')
            })
        if company.get('phone'):
            company_phones.append({
                'company': company.get('legal_name'),
                'phone': company.get('phone'),
                'source': company.get('source_records', [{}])[0].get('source', 'Unknown')
            })
    
    print(f"\nCompany Emails ({len(company_emails)} total):")
    for i, item in enumerate(company_emails, 1):
        print(f"{i:3d}. {item['email']:30s} | {item['company']:40s} | {item['source']}")
    
    print(f"\nCompany Phone Numbers ({len(company_phones)} total):")
    for i, item in enumerate(company_phones, 1):
        print(f"{i:3d}. {item['phone']:20s} | {item['company']:40s} | {item['source']}")
    
    # Extract person/executive contacts
    print("\n" + "="*100)
    print("EXECUTIVE/DECISION MAKER EMAIL AND PHONE CONTACTS")
    print("-" * 100)
    
    person_emails = []
    person_phones = []
    
    for person in people:
        if person.get('work_email'):
            person_emails.append({
                'name': person.get('full_name'),
                'title': person.get('title'),
                'company': person.get('company_name'),
                'email': person.get('work_email'),
                'source': person.get('source', 'Unknown')
            })
        if person.get('direct_phone'):
            person_phones.append({
                'name': person.get('full_name'),
                'title': person.get('title'),
                'company': person.get('company_name'),
                'phone': person.get('direct_phone'),
                'source': person.get('source', 'Unknown')
            })
    
    print(f"\nExecutive Emails ({len(person_emails)} total):")
    for i, item in enumerate(person_emails, 1):
        print(f"{i:3d}. {item['name']:30s} | {item['title']:25s} | {item['email']:40s}")
        print(f"     Company: {item['company']} | Source: {item['source']}\n")
    
    print(f"\nExecutive Phone Numbers ({len(person_phones)} total):")
    for i, item in enumerate(person_phones, 1):
        print(f"{i:3d}. {item['name']:30s} | {item['title']:25s} | {item['phone']:20s}")
        print(f"     Company: {item['company']} | Source: {item['source']}\n")
    
    # Summary statistics
    print("\n" + "="*100)
    print("CONTACT COVERAGE SUMMARY")
    print("-" * 100)
    
    total_companies = len(companies)
    total_people = len(people)
    
    company_with_email = len([c for c in companies if c.get('email')])
    company_with_phone = len([c for c in companies if c.get('phone')])
    person_with_email = len([p for p in people if p.get('work_email')])
    person_with_phone = len([p for p in people if p.get('direct_phone')])
    
    print(f"\nCompanies:")
    print(f"  Total: {total_companies}")
    print(f"  With Email: {company_with_email} ({100*company_with_email/total_companies:.1f}%)")
    print(f"  With Phone: {company_with_phone} ({100*company_with_phone/total_companies:.1f}%)")
    
    print(f"\nExecutives/Decision Makers:")
    print(f"  Total: {total_people}")
    print(f"  With Email: {person_with_email} ({100*person_with_email/total_people:.1f}%)")
    print(f"  With Phone: {person_with_phone} ({100*person_with_phone/total_people:.1f}%)")
    
    print(f"\nOverall Contact Data:")
    print(f"  Total Email Addresses: {len(company_emails) + len(person_emails)}")
    print(f"  Total Phone Numbers: {len(company_phones) + len(person_phones)}")
    print(f"  Total Contacts: {len(company_emails) + len(person_emails) + len(company_phones) + len(person_phones)}")
    
    # Export to CSV
    print("\n" + "="*100)
    print("EXPORTING TO CSV FILES")
    print("-" * 100)
    
    # Company emails CSV
    if company_emails:
        with open('company_emails.csv', 'w', encoding='utf-8') as f:
            f.write('Company,Email,Source\n')
            for item in company_emails:
                f.write(f'"{item["company"]}","{item["email"]}","{item["source"]}"\n')
        print(f"✓ Exported {len(company_emails)} company emails to company_emails.csv")
    
    # Company phones CSV
    if company_phones:
        with open('company_phones.csv', 'w', encoding='utf-8') as f:
            f.write('Company,Phone,Source\n')
            for item in company_phones:
                f.write(f'"{item["company"]}","{item["phone"]}","{item["source"]}"\n')
        print(f"✓ Exported {len(company_phones)} company phone numbers to company_phones.csv")
    
    # Executive emails CSV
    if person_emails:
        with open('executive_emails.csv', 'w', encoding='utf-8') as f:
            f.write('Name,Title,Company,Email,Source\n')
            for item in person_emails:
                f.write(f'"{item["name"]}","{item["title"]}","{item["company"]}","{item["email"]}","{item["source"]}"\n')
        print(f"✓ Exported {len(person_emails)} executive emails to executive_emails.csv")
    
    # Executive phones CSV
    if person_phones:
        with open('executive_phones.csv', 'w', encoding='utf-8') as f:
            f.write('Name,Title,Company,Phone,Source\n')
            for item in person_phones:
                f.write(f'"{item["name"]}","{item["title"]}","{item["company"]}","{item["phone"]}","{item["source"]}"\n')
        print(f"✓ Exported {len(person_phones)} executive phone numbers to executive_phones.csv")
    
    print("\n✅ Contact extraction complete!\n")

if __name__ == "__main__":
    extract_contacts()
