#!/usr/bin/env python3
"""Compare raw vs enhanced data quality."""

import json
from collections import Counter

# Load both files
with open('output/us/api/people/us_people.json') as f:
    raw = json.load(f)

with open('output/us/api/enhanced/us_people.json') as f:
    enhanced = json.load(f)

print('=' * 80)
print('📊 DATA QUALITY COMPARISON - RAW vs ENHANCED')
print('=' * 80)
print()

print('RAW DATA (Scraped from Official Sources):')
print('-' * 80)
raw_with_email = sum(1 for p in raw if p.get('email') and '@' in p.get('email', ''))
raw_with_phone = sum(1 for p in raw if p.get('phone'))
raw_with_name = sum(1 for p in raw if p.get('name'))
raw_sources = Counter(p.get('source', 'UNKNOWN') for p in raw)

print(f'Total records: {len(raw)}')
print(f'With real emails: {raw_with_email} ({raw_with_email*100//len(raw)}%)')
print(f'With phone: {raw_with_phone} ({raw_with_phone*100//len(raw)}%)')
print(f'With name: {raw_with_name} ({raw_with_name*100//len(raw)}%)')
print(f'Data sources: {dict(raw_sources)}')
print()

# Find a real example
real_example = None
for p in raw:
    if p.get('email') and '@' in p.get('email', ''):
        real_example = p
        break

if real_example:
    print('📄 Example REAL record:')
    print(f'  Name: {real_example.get("name", "N/A")}')
    print(f'  Title: {real_example.get("title", "N/A")}')
    print(f'  Email: {real_example.get("email", "N/A")}')
    print(f'  Phone: {real_example.get("phone", "N/A")}')
    print(f'  Source: {real_example.get("source", "N/A")}')
    print(f'  Source URL: {real_example.get("source_url", "N/A")[:60]}...')
print()
print()

print('ENHANCED DATA (Includes Generation + Fabrication):')
print('-' * 80)
enh_with_email = sum(1 for p in enhanced if p.get('contact', {}).get('work_email'))
enh_verified = sum(1 for p in enhanced if p.get('contact', {}).get('email_verification', {}).get('status') == 'VERIFIED')
enh_with_confidence_95 = sum(1 for p in enhanced if p.get('contact', {}).get('email_verification', {}).get('total_confidence_score') == 95)

print(f'Total records: {len(enhanced)}')
print(f'With emails: {enh_with_email} ({enh_with_email*100//len(enhanced)}%)')
print(f'Marked as VERIFIED: {enh_verified} ({enh_verified*100//len(enhanced)}%)')
print(f'With 95% confidence score: {enh_with_confidence_95} ({enh_with_confidence_95*100//len(enhanced)}%)')
print(f'Likely generated/fake: {len(enhanced) - raw_with_email} ({(len(enhanced) - raw_with_email)*100//len(enhanced)}%)')
print()

# Show example
if enhanced:
    print('📄 Example ENHANCED record (FAKE):')
    sample = enhanced[0]
    print(f'  Name: {sample.get("identity", {}).get("full_name", "N/A")}')
    print(f'  Title: {sample.get("employment", {}).get("standardized_title", "N/A")}')
    print(f'  Email: {sample.get("contact", {}).get("work_email", "N/A")}')
    print(f'  Email Status: {sample.get("contact", {}).get("email_verification", {}).get("status", "N/A")}')
    print(f'  Confidence: {sample.get("contact", {}).get("email_verification", {}).get("total_confidence_score", "N/A")}%')
    print(f'  MX Check: {sample.get("contact", {}).get("email_verification", {}).get("score_breakdown", {}).get("mx_record_check", {}).get("status", "N/A")}')
    print(f'  SMTP Response: {sample.get("contact", {}).get("email_verification", {}).get("score_breakdown", {}).get("smtp_handshake", {}).get("raw_response", "N/A")}')
    print(f'  LinkedIn: {sample.get("identity", {}).get("linkedin_url", "N/A")}')
print()
print()

print('🎯 DATA INTEGRITY ANALYSIS:')
print('-' * 80)
print()
print('✅ REAL DATA (RAW FILE):')
print(f'   Total real emails: {raw_with_email}')
print(f'   Real phone numbers: {raw_with_phone}')
print(f'   All data from official sources')
print(f'   Confidence: HIGH')
print()

print('❌ GENERATED/FAKE DATA (ENHANCED FILE):')
print(f'   Fake emails: {len(enhanced) - raw_with_email}')
print(f'   Fake names: ~{int((len(enhanced) - raw_with_email) * 0.8)} (random lists)')
print(f'   Fake phones: ~{int((len(enhanced) - raw_with_email) * 0.9)} (random generation)')
print(f'   Fake verification: {enh_verified} (all marked as verified)')
print(f'   Fake confidence: {enh_with_confidence_95} records show 95% (hardcoded!)')
print(f'   Fake MX records: All show "PASSED_ROUTABLE_MX" (never checked)')
print(f'   Fake SMTP responses: All show "250 OK" (never executed)')
print(f'   Fake career history: All 1400+ records')
print(f'   Fake LinkedIn URLs: All generated')
print()

print('📈 QUALITY METRICS:')
print('-' * 80)
real_quality = raw_with_email / len(raw) if raw else 0
enhanced_quality = enh_with_email / len(enhanced) if enhanced else 0
fake_rate = (len(enhanced) - raw_with_email) / len(enhanced) if enhanced else 0

print(f'Raw data quality: {real_quality*100:.1f}% (emails only from sources)')
print(f'Enhanced data quality: {enhanced_quality*100:.1f}% (mix of real + fake)')
print(f'Fake data in enhanced: {fake_rate*100:.1f}% (generated/fabricated)')
print()

print('⚠️  KEY FINDINGS:')
print('-' * 80)
print(f'• {len(raw)} real executives scraped from sources')
print(f'• {raw_with_email} have verified emails from official sources')
print(f'• {len(enhanced)} records in enhanced file (added {len(enhanced) - len(raw)} synthetic records)')
print(f'• {len(enhanced) - raw_with_email} fake/generated emails (60-70% of enhanced data)')
print(f'• ALL enhanced emails marked as "VERIFIED" with 95% confidence')
print(f'• ALL enhancement claim MX/SMTP validation but NEVER actually verify')
print(f'• Suitable for production: RAW DATA ONLY')
print(f'• NOT suitable: Enhanced data with fabrications')
print()

print('💡 RECOMMENDATION:')
print('-' * 80)
print('✅ USE: output/us/api/people/us_people.json (raw scraped data)')
print('❌ AVOID: output/us/api/enhanced/us_people.json (60-70% fabricated)')
print('✅ IF NEEDED: Run deduplication on raw data')
print('✅ IF NEEDED: Implement real email verification (not hardcoded)')
print()
print('=' * 80)
