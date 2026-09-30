#!/bin/bash
# Master ingestion script - pulls from ALL data sources with contact info

echo "=========================================="
echo "MASTER INGESTION: ALL REAL CONTACT DATA"
echo "=========================================="

cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"

echo ""
echo "Step 1: Ingesting from SAM.gov (Federal Contractors + POC Emails/Phones)"
python scripts/export_real_data_only.py \
  --records 5000 \
  --sources SAM_GOV \
  --validate

echo ""
echo "Step 2: Ingesting from CMS NPI (Healthcare Providers + Verified Contacts)"
python scripts/export_real_data_only.py \
  --records 5000 \
  --sources CMS_NPI \
  --validate

echo ""
echo "Step 3: Ingesting from OpenCorporates (Business Officers)"
python scripts/export_real_data_only.py \
  --records 5000 \
  --sources OPENCORPORATES \
  --validate

echo ""
echo "Step 4: Ingesting from ProPublica 990 (Nonprofit Officers)"
python scripts/export_real_data_only.py \
  --records 5000 \
  --sources PROPUBLICA_990 \
  --validate

echo ""
echo "Step 5: Extracting C-Suite + Contacts from all sources"
python extract_csuite_contacts.py

echo ""
echo "=========================================="
echo "✅ ALL DATA INGESTED AND EXTRACTED"
echo "=========================================="
echo ""
echo "Output files in: output/us/api/real_emails/"
echo "  • csuite_executives.csv"
echo "  • company_emails.csv"
echo "  • company_phones.csv"
echo "  • people_emails.csv"
echo "  • people_phones.csv"
echo "  • comprehensive_contacts.csv"
echo ""
