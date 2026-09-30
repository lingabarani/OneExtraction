#!/usr/bin/env python3
"""Inspect what fields are actually available in the real data export."""

import json
from pathlib import Path

companies_file = Path("output/us/api/companies/us_companies_real_data_only.json")
people_file = Path("output/us/api/people/us_people_real_data_only.json")

print("="*100)
print("INSPECTING REAL DATA EXPORT - AVAILABLE FIELDS")
print("="*100 + "\n")

# Check companies
print("COMPANY RECORD SAMPLE")
print("-"*100)
with open(companies_file) as f:
    companies = json.load(f)

if companies:
    company = companies[0]
    print(f"\nTotal companies: {len(companies)}")
    print(f"\nFirst company fields:")
    for key, value in company.items():
        value_str = str(value)[:80] if value else "None"
        print(f"  {key:30s}: {value_str}")

# Check people  
print("\n" + "="*100)
print("PERSON/EXECUTIVE RECORD SAMPLE")
print("-"*100)
with open(people_file) as f:
    people = json.load(f)

if people:
    person = people[0]
    print(f"\nTotal executives: {len(people)}")
    print(f"\nFirst executive fields:")
    for key, value in person.items():
        value_str = str(value)[:80] if value else "None"
        print(f"  {key:30s}: {value_str}")

# Find all unique fields
print("\n" + "="*100)
print("ALL UNIQUE FIELDS IN DATASET")
print("-"*100)

company_fields = set()
for company in companies:
    company_fields.update(company.keys())

person_fields = set()
for person in people:
    person_fields.update(person.keys())

print(f"\nCompany Fields ({len(company_fields)}):")
for field in sorted(company_fields):
    print(f"  • {field}")

print(f"\nExecutive Fields ({len(person_fields)}):")
for field in sorted(person_fields):
    print(f"  • {field}")

# Show data availability
print("\n" + "="*100)
print("DATA AVAILABILITY IN EXPORT")
print("-"*100)

contact_fields = ['email', 'phone', 'work_email', 'direct_phone', 'emails', 'phones']

print(f"\nCompany Contact Fields:")
for field in contact_fields:
    count = sum(1 for c in companies if c.get(field))
    print(f"  {field:20s}: {count:5d} records ({100*count/len(companies):.1f}%)")

print(f"\nExecutive Contact Fields:")
for field in contact_fields:
    count = sum(1 for p in people if p.get(field))
    print(f"  {field:20s}: {count:5d} records ({100*count/len(people):.1f}%)")

print("\n" + "="*100)
print("NOTES")
print("="*100)
print("""
SEC EDGAR (public company filings) provides:
  ✓ Company names
  ✓ Executive titles
  ✓ Company addresses
  ✗ Executive emails (NOT in public filings)
  ✗ Executive phone numbers (NOT in public filings)

To get real emails and phone numbers, use:
  • SAM.gov - Federal contractor POCs (emails + phones verified)
  • CMS NPI - Healthcare provider contacts (emails + phones verified)
  • OpenCorporates - Business officers (may have limited contact info)

Current limitation: SEC EDGAR source doesn't have direct contact info.
""")
