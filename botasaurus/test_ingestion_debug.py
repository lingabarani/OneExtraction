#!/usr/bin/env python3
"""Debug script to check what data is being ingested and why validation fails."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from us_b2b.connectors.edgar_client import EdgarClient
from us_b2b.pipeline.validation import validate_company

# Test SEC EDGAR
print("Testing SEC EDGAR ingestion...")
client = EdgarClient()
companies = client.fetch_batch(max_companies=5)

print(f"\nSEC EDGAR returned {len(companies)} companies\n")

for i, company in enumerate(companies, 1):
    print(f"Company {i}:")
    print(f"  Legal Name: {company.legal_name}")
    print(f"  Address: {company.address}")
    print(f"  State: {company.address.state if company.address else 'N/A'}")
    print(f"  Validation: {validate_company(company)}")
    print()
