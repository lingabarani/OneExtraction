#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract C-Suite Executives + Company/People Contact Information
================================================================

Extracts from multiple real sources:
- SAM.gov: Federal contractors with POC contacts
- CMS NPI: Healthcare providers with verified contacts
- OpenCorporates: Business officers
- ProPublica 990: Nonprofit officers

Output: CSV files with real emails, phone numbers, C-suite executives
"""

import json
import csv
import sys
import io
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# C-Suite titles to extract
CSUITE_TITLES = {
    'CEO', 'CFO', 'COO', 'CTO', 'CMO', 'CHRO', 'CLO', 'CRO', 'CSO', 'CIO', 'CDO',
    'Chief Executive Officer', 'Chief Financial Officer', 'Chief Operating Officer',
    'Chief Technology Officer', 'Chief Marketing Officer', 'Chief Human Resources Officer',
    'Chief Legal Officer', 'Chief Revenue Officer', 'Chief Security Officer',
    'Chief Information Officer', 'Chief Data Officer', 'Chief Strategy Officer',
    'Chief Product Officer', 'Chief Innovation Officer',
    'Executive Vice President', 'Senior Vice President', 'President'
}

class CSuiteContactExtractor:
    """Extract C-Suite executives and contact information."""
    
    def __init__(self):
        self.companies = []
        self.people = []
        self.csuite_executives = []
        self.company_contacts = []
        self.people_contacts = []
        self.errors = []
    
    def load_export(self, companies_file: Path, people_file: Path):
        """Load real data export."""
        try:
            with open(companies_file) as f:
                self.companies = json.load(f)
            print(f"✓ Loaded {len(self.companies)} companies")
        except Exception as e:
            self.errors.append(f"Error loading companies: {e}")
        
        try:
            with open(people_file) as f:
                self.people = json.load(f)
            print(f"✓ Loaded {len(self.people)} people/executives")
        except Exception as e:
            self.errors.append(f"Error loading people: {e}")
    
    def is_csuite(self, title: str) -> bool:
        """Check if title is C-Suite."""
        if not title:
            return False
        title_upper = str(title).upper()
        return any(csuite in title_upper for csuite in CSUITE_TITLES)
    
    def extract_csuite_executives(self):
        """Extract C-Suite executives with company details."""
        print("\n" + "="*100)
        print("EXTRACTING C-SUITE EXECUTIVES")
        print("="*100)
        
        company_map = {c['company_id']: c for c in self.companies}
        csuite_count = 0
        
        for person in self.people:
            title = person.get('title', '') or person.get('standardized_title', '')
            
            if self.is_csuite(title):
                company = company_map.get(person.get('company_id'), {})
                
                record = {
                    'person_id': person.get('person_id'),
                    'first_name': person.get('first_name'),
                    'last_name': person.get('last_name'),
                    'full_name': person.get('full_name'),
                    'title': title,
                    'seniority_level': person.get('seniority_level'),
                    'department': person.get('department'),
                    'company_id': person.get('company_id'),
                    'company_name': person.get('company_name'),
                    'company_email': company.get('email'),
                    'company_phone': company.get('phone'),
                    'company_website': company.get('website'),
                    'company_domain': company.get('domain'),
                    'company_industry': company.get('industry'),
                    'company_naics': company.get('naics_code'),
                    'executive_email': person.get('work_email'),
                    'executive_phone': person.get('direct_phone'),
                    'email_status': person.get('email_status'),
                    'email_confidence': person.get('email_confidence_score'),
                    'is_active': person.get('is_active'),
                    'source': person.get('source'),
                }
                self.csuite_executives.append(record)
                csuite_count += 1
        
        print(f"✓ Extracted {csuite_count} C-Suite executives")
        print(f"  Breakdown:")
        for title_type in ['CEO', 'CFO', 'COO', 'CTO', 'CMO', 'CHRO']:
            count = sum(1 for e in self.csuite_executives if title_type in e['title'].upper())
            if count > 0:
                print(f"    • {title_type}: {count}")
        
        return csuite_count
    
    def extract_company_contacts(self):
        """Extract company email and phone contacts."""
        print("\n" + "="*100)
        print("EXTRACTING COMPANY CONTACT INFORMATION")
        print("="*100)
        
        email_count = 0
        phone_count = 0
        
        for company in self.companies:
            if company.get('email'):
                self.company_contacts.append({
                    'company_id': company.get('company_id'),
                    'company_name': company.get('legal_name'),
                    'email': company.get('email'),
                    'contact_type': 'email',
                    'industry': company.get('industry'),
                    'source': company.get('source_records', [{}])[0].get('source', 'Unknown'),
                    'verified': True
                })
                email_count += 1
            
            if company.get('phone'):
                self.company_contacts.append({
                    'company_id': company.get('company_id'),
                    'company_name': company.get('legal_name'),
                    'phone': company.get('phone'),
                    'contact_type': 'phone',
                    'industry': company.get('industry'),
                    'source': company.get('source_records', [{}])[0].get('source', 'Unknown'),
                    'verified': True
                })
                phone_count += 1
        
        print(f"✓ Extracted company contacts:")
        print(f"  • {email_count} email addresses")
        print(f"  • {phone_count} phone numbers")
        
        return email_count + phone_count
    
    def extract_people_contacts(self):
        """Extract people/executive contact information."""
        print("\n" + "="*100)
        print("EXTRACTING PEOPLE/EXECUTIVE CONTACT INFORMATION")
        print("="*100)
        
        email_count = 0
        phone_count = 0
        
        for person in self.people:
            if person.get('work_email'):
                self.people_contacts.append({
                    'person_id': person.get('person_id'),
                    'full_name': person.get('full_name'),
                    'title': person.get('title'),
                    'email': person.get('work_email'),
                    'contact_type': 'email',
                    'company': person.get('company_name'),
                    'company_id': person.get('company_id'),
                    'email_status': person.get('email_status'),
                    'email_confidence': person.get('email_confidence_score'),
                    'source': person.get('source'),
                    'verified': person.get('email_status') in ('VERIFIED', 'PROBABLE')
                })
                email_count += 1
            
            if person.get('direct_phone'):
                self.people_contacts.append({
                    'person_id': person.get('person_id'),
                    'full_name': person.get('full_name'),
                    'title': person.get('title'),
                    'phone': person.get('direct_phone'),
                    'contact_type': 'phone',
                    'company': person.get('company_name'),
                    'company_id': person.get('company_id'),
                    'phone_type': person.get('phone_type'),
                    'source': person.get('source'),
                    'verified': True
                })
                phone_count += 1
        
        print(f"✓ Extracted people contacts:")
        print(f"  • {email_count} email addresses")
        print(f"  • {phone_count} phone numbers")
        
        return email_count + phone_count
    
    def export_to_csv(self):
        """Export all extracted data to CSV files."""
        print("\n" + "="*100)
        print("EXPORTING TO CSV FILES")
        print("="*100)
        
        # Ensure output directory
        output_dir = Path("output/us/api/real_emails")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export C-Suite executives
        if self.csuite_executives:
            csuite_file = output_dir / "csuite_executives.csv"
            with open(csuite_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'person_id', 'full_name', 'first_name', 'last_name', 'title', 'seniority_level',
                    'company_id', 'company_name', 'company_industry', 'company_naics',
                    'company_email', 'company_phone', 'company_website', 'company_domain',
                    'department', 'executive_email', 'executive_phone',
                    'email_status', 'email_confidence', 'is_active', 'source'
                ], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self.csuite_executives)
            print(f"✓ Exported {len(self.csuite_executives)} C-Suite executives to csuite_executives.csv")
        
        # Export company emails
        company_emails = [c for c in self.company_contacts if c.get('email')]
        if company_emails:
            file_path = output_dir / "company_emails.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['company_name', 'email', 'industry', 'source'], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(company_emails)
            print(f"✓ Exported {len(company_emails)} company emails to company_emails.csv")
        
        # Export company phones
        company_phones = [c for c in self.company_contacts if c.get('phone')]
        if company_phones:
            file_path = output_dir / "company_phones.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['company_name', 'phone', 'industry', 'source'], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(company_phones)
            print(f"✓ Exported {len(company_phones)} company phone numbers to company_phones.csv")
        
        # Export people emails
        people_emails = [p for p in self.people_contacts if p.get('email')]
        if people_emails:
            file_path = output_dir / "people_emails.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'full_name', 'title', 'email', 'company', 'email_status',
                    'email_confidence', 'verified', 'source'
                ], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(people_emails)
            print(f"✓ Exported {len(people_emails)} people emails to people_emails.csv")
        
        # Export people phones
        people_phones = [p for p in self.people_contacts if p.get('phone')]
        if people_phones:
            file_path = output_dir / "people_phones.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'full_name', 'title', 'phone', 'company', 'phone_type', 'verified', 'source'
                ], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(people_phones)
            print(f"✓ Exported {len(people_phones)} people phone numbers to people_phones.csv")
        
        # Export comprehensive contact list
        comprehensive = self._build_comprehensive_list()
        if comprehensive:
            file_path = output_dir / "comprehensive_contacts.csv"
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'name', 'title', 'company', 'industry', 'email', 'phone',
                    'record_type', 'source', 'verified'
                ], extrasaction='ignore')
                writer.writeheader()
                writer.writerows(comprehensive)
            print(f"✓ Exported {len(comprehensive)} comprehensive contacts to comprehensive_contacts.csv")
        
        return output_dir
    
    def _build_comprehensive_list(self) -> List[Dict]:
        """Build comprehensive contact list combining all data."""
        comprehensive = []
        
        # Add C-Suite with company info
        for exec in self.csuite_executives:
            comprehensive.append({
                'name': exec.get('full_name'),
                'title': exec.get('title'),
                'company': exec.get('company_name'),
                'industry': exec.get('company_industry'),
                'email': exec.get('executive_email') or exec.get('company_email'),
                'phone': exec.get('executive_phone') or exec.get('company_phone'),
                'record_type': 'C-Suite Executive',
                'source': exec.get('source'),
                'verified': 'Yes' if exec.get('executive_email') or exec.get('executive_phone') else 'Partial'
            })
        
        # Add other people contacts
        for person in self.people_contacts:
            if person.get('email') or person.get('phone'):
                comprehensive.append({
                    'name': person.get('full_name'),
                    'title': person.get('title'),
                    'company': person.get('company'),
                    'industry': '',
                    'email': person.get('email'),
                    'phone': person.get('phone'),
                    'record_type': 'Employee/Executive',
                    'source': person.get('source'),
                    'verified': 'Yes' if person.get('verified') else 'Unverified'
                })
        
        # Add company contacts
        for company in self.company_contacts:
            if company.get('email') or company.get('phone'):
                comprehensive.append({
                    'name': company.get('company_name'),
                    'title': 'Main Office',
                    'company': company.get('company_name'),
                    'industry': company.get('industry'),
                    'email': company.get('email'),
                    'phone': company.get('phone'),
                    'record_type': 'Company',
                    'source': company.get('source'),
                    'verified': 'Yes'
                })
        
        return comprehensive
    
    def generate_report(self, output_dir: Path):
        """Generate summary report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_companies': len(self.companies),
                'total_people': len(self.people),
                'csuite_executives': len(self.csuite_executives),
                'company_contacts': len(self.company_contacts),
                'people_contacts': len(self.people_contacts),
            },
            'breakdown': {
                'company_emails': len([c for c in self.company_contacts if c.get('email')]),
                'company_phones': len([c for c in self.company_contacts if c.get('phone')]),
                'people_emails': len([p for p in self.people_contacts if p.get('email')]),
                'people_phones': len([p for p in self.people_contacts if p.get('phone')]),
            },
            'csuite_by_title': self._count_by_title(),
            'data_sources': self._get_sources(),
            'errors': self.errors
        }
        
        report_file = output_dir / "extraction_summary.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved to extraction_summary.json")
        return report
    
    def _count_by_title(self) -> Dict[str, int]:
        """Count executives by title."""
        counts = defaultdict(int)
        for exec in self.csuite_executives:
            title = exec.get('title', 'Unknown')
            counts[title] += 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    
    def _get_sources(self) -> Dict[str, int]:
        """Get data sources count."""
        sources = defaultdict(int)
        for exec in self.csuite_executives:
            sources[exec.get('source', 'Unknown')] += 1
        return dict(sorted(sources.items(), key=lambda x: x[1], reverse=True))


def main():
    print("\n" + "="*100)
    print("C-SUITE EXECUTIVES + CONTACT INFORMATION EXTRACTOR")
    print("="*100)
    
    # Find latest real data export
    companies_file = Path("output/us/api/companies/us_companies_real_data_only.json")
    people_file = Path("output/us/api/people/us_people_real_data_only.json")
    
    if not companies_file.exists() or not people_file.exists():
        print(f"\n[ERROR] Real data export files not found!")
        print(f"Expected: {companies_file}")
        print(f"Expected: {people_file}")
        print(f"\nRun first: python scripts/export_real_data_only.py --records 5000 --sources SAM_GOV CMS_NPI OPENCORPORATES")
        sys.exit(1)
    
    extractor = CSuiteContactExtractor()
    extractor.load_export(companies_file, people_file)
    
    # Extract data
    extractor.extract_csuite_executives()
    extractor.extract_company_contacts()
    extractor.extract_people_contacts()
    
    # Export
    output_dir = extractor.export_to_csv()
    
    # Generate report
    report = extractor.generate_report(output_dir)
    
    # Print summary
    print("\n" + "="*100)
    print("EXTRACTION SUMMARY")
    print("="*100)
    print(f"\nC-Suite Executives: {report['summary']['csuite_executives']}")
    print(f"Company Contacts: {report['summary']['company_contacts']}")
    print(f"People Contacts: {report['summary']['people_contacts']}")
    print(f"\nBreakdown:")
    print(f"  • Company Emails: {report['breakdown']['company_emails']}")
    print(f"  • Company Phones: {report['breakdown']['company_phones']}")
    print(f"  • People Emails: {report['breakdown']['people_emails']}")
    print(f"  • People Phones: {report['breakdown']['people_phones']}")
    print(f"\nOutput Directory: {output_dir}")
    print(f"Files Generated:")
    print(f"  • csuite_executives.csv - C-Suite with company details")
    print(f"  • company_emails.csv - Company email addresses")
    print(f"  • company_phones.csv - Company phone numbers")
    print(f"  • people_emails.csv - People/executive emails")
    print(f"  • people_phones.csv - People/executive phone numbers")
    print(f"  • comprehensive_contacts.csv - All contacts combined")
    print(f"  • extraction_summary.json - Detailed report")
    print("\n✅ Extraction complete!\n")


if __name__ == "__main__":
    main()

