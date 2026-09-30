# Dataforge Integration Guide for OneExtraction

## Important Note
Dataforge (forge-enrichment) is currently in active development. If the PyPI package isn't available, you have two options:

### Option A: Build from Source (Recommended for now)
```bash
# Clone the repository
git clone https://github.com/ghealysr/forge.git
cd forge

# Install in development mode
pip install -e .

# Verify
forge --version
```

### Option B: Use Docker (Easiest if source build fails)
We've included Docker containers in docker-compose.yml for:
- PostgreSQL (Dataforge database backend)
- Check-If-Email-Exists (Email validator)
- Optional: Ollama (Local AI models)

---

## Setup Steps

### 1. Start Docker Infrastructure
```bash
docker-compose up -d

# Verify all containers are running
docker ps
```

This will start:
- ✅ PostgreSQL on port 5432 (for storing enriched data)
- ✅ Email Validator on port 8081 (for validating emails)
- ⏳ Ollama on port 11434 (optional, for AI enrichment)

### 2. Verify Database Connection
```bash
# Windows PowerShell
.\scripts\dataforge_status.ps1

# Or use psql directly if installed
psql -h localhost -U forge -d oneextraction
```

### 3. Load OneExtraction Data

Run the Python data loader to transfer your existing OneExtraction companies and executives into PostgreSQL:

```bash
python scripts/dataforge_loader.py
```

**Expected Output:**
```
✅ Connected to PostgreSQL: localhost:5432/oneextraction
✓ Loaded 1185 records from us_companies.json
✓ Loaded 2370 records from us_people.json
✅ Companies loaded: 1185 inserted, 0 updated, 0 skipped
✅ People loaded: 2370 inserted, 0 updated, 0 skipped

📊 Data Loading Report
================================================
Companies loaded:    1185
Companies updated:   0
Companies skipped:   0
People loaded:       2370
People updated:      0
Errors:              0
================================================

✅ Data loading complete!
```

### 4. Alternative: Manual Dataforge Installation

If you want to try installing directly from PyPI:

```bash
# Try the latest version (not 2.0.0 if it's not released)
pip install forge-enrichment

# If that fails, install from GitHub
pip install git+https://github.com/ghealysr/forge.git
```

---

## What Dataforge Does (Overview)

Even if you run it separately, here's what it provides:

### Email Extraction (6-Layer Detection)
- Mailto links on website
- Regex pattern matching
- Cloudflare email decode
- JSON-LD structured data
- Obfuscation detection
- Contact form crawling

**Expected:** 60-70% email coverage from websites

### Tech Detection (30+ Technologies)
- WordPress, Shopify, Wix
- React, Vue, Next.js
- Stripe, Intercom, Google Analytics
- And many more...

**Expected:** 50-60% tech detection

### SMTP Verification
- Connects to mail servers
- Verifies deliverability
- Detects catch-all addresses
- Flags disposable emails

---

## Using the Data Without Dataforge

If Dataforge setup is blocked, you can still:

### 1. Use Check-If-Email-Exists (Email Validator)
```bash
# Already in docker-compose.yml, running on port 8081
# Use scripts/batch_email_validator.py to validate existing emails

python scripts/batch_email_validator.py
```

### 2. Use Your Existing Data
Your OneExtraction already has:
- ✅ 1,185 companies
- ✅ 2,370 executives
- ✅ SEC EDGAR verified data
- ✅ SAM.gov contact info
- ✅ Industry classifications

### 3. Manual Email Enrichment
```bash
# For executives without emails, you can:
# 1. Use Hunter.io (paid, highly accurate)
# 2. Use Clearbit (paid)
# 3. Use pattern-based generation:
#    - firstname.lastname@company.com
#    - first.last@domain.com
#    - flast@domain.com
#    - And validate with Check-If-Email
```

---

## Next Steps

### Immediate (This Week)
- [x] Start Docker containers
- [x] Load OneExtraction data to PostgreSQL
- [ ] Test email validator with existing data
- [ ] Create validation pipeline

### Week 2
- [ ] When Dataforge is available, run enrichment
- [ ] Extract emails using 6-layer detection
- [ ] Validate with Check-If-Email

### Week 3
- [ ] Quality assurance & reporting
- [ ] MCP integration
- [ ] Dashboard setup

### Week 4
- [ ] Export verified emails (CSV, JSON)
- [ ] CRM integration (Salesforce/HubSpot)
- [ ] Sales team handoff

---

## Architecture Without Dataforge (Fallback Plan)

```
OneExtraction Data
├── Companies: 1,185
└── Executives: 2,370
    ↓
PostgreSQL (Stores structured data)
    ↓
Check-If-Email-Exists (Validates emails)
    ↓
Output: Verified Safe Emails
├── 900-1,200 verified emails
├── Quality scores
└── Deliverability flags
    ↓
Export to CSV/JSON/XLSX
    ↓
CRM Integration (Salesforce/HubSpot)
```

---

## Troubleshooting

### PostgreSQL Connection Failed
```bash
# Verify containers are running
docker ps

# Check PostgreSQL logs
docker logs oneextraction-postgres

# Restart if needed
docker-compose down
docker-compose up -d
```

### Data Loader Failed
```bash
# Check if JSON files exist
ls -la output/us/api/companies/us_companies.json
ls -la output/us/api/people/us_people.json

# Check PostgreSQL is accessible
psql -h localhost -U forge -d oneextraction -c "SELECT 1"
```

### Email Validator Not Responding
```bash
# Check if it's running
docker ps | grep email-validator

# Test endpoint
curl -X POST http://localhost:8081/v0/check_email \
  -H "Content-Type: application/json" \
  -d '{"to_email":"test@example.com"}'
```

---

## Resources

- **Dataforge GitHub:** https://github.com/ghealysr/forge
- **Check-If-Email GitHub:** https://github.com/reacherhq/check-if-email-exists
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Hunter.io (for manual enrichment):** https://hunter.io/
- **Clearbit (for manual enrichment):** https://clearbit.com/

---

## Next Document

See `Week 2: Email Extraction & Validation Plan` in the main implementation document for continuing when Dataforge is ready.
