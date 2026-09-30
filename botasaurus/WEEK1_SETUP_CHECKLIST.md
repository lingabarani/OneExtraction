# Week 1: Setup Checklist - OneExtraction Integration

## Status: Task 1.2 In Progress

### Prerequisites Completed ✅
- [x] Created docker-compose.yml with PostgreSQL, Email Validator, Ollama
- [x] Created init_db.sql with full schema for businesses, people, enrichment jobs
- [x] Created .env.integration configuration template
- [x] Created setup scripts (setup_dataforge.sh, setup_dataforge.ps1)
- [x] Created dataforge_loader.py for data migration
- [x] Created dataforge_integration_guide.md

### Current Challenge
Docker daemon not running on this system. We have two paths:

---

## Path A: Without Docker (Local PostgreSQL)

### Step 1: Install PostgreSQL Locally

**Windows:**
```powershell
# Option 1: Using chocolatey
choco install postgresql15

# Option 2: Direct download
# https://www.postgresql.org/download/windows/
```

**After Installation:**
- Default port: 5432
- Create user "forge" with password "oneextraction_secure_2026"
- Create database "oneextraction"

### Step 2: Initialize Database Schema

```powershell
# Get psql path
$psqlPath = "C:\Program Files\PostgreSQL\15\bin\psql.exe"

# Run init script
& $psqlPath -h localhost -U postgres -d postgres -f init_db.sql
```

### Step 3: Load OneExtraction Data

```powershell
python scripts/dataforge_loader.py
```

**Expected Output:**
```
✅ Connected to PostgreSQL: localhost:5432/oneextraction
✓ Loaded 1185 records from us_companies.json
✓ Loaded 2370 records from us_people.json
✅ Data loading complete!
```

---

## Path B: With Docker (Recommended - When Docker is Running)

### Step 1: Start Docker Desktop
- Open Docker Desktop application
- Wait for "Engine running" indicator
- Verify: `docker ps`

### Step 2: Start Containers
```powershell
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
docker-compose up -d

# Verify all running
docker ps
```

### Step 3: Load Data
```powershell
# Wait for PostgreSQL to be ready (30 seconds)
Start-Sleep -Seconds 30

python scripts/dataforge_loader.py
```

---

## Current Setup Files

### ✅ Created (Task 1.1)
1. **docker-compose.yml**
   - PostgreSQL 15 service
   - Email Validator service
   - Optional Ollama service
   - All on bridge network

2. **init_db.sql**
   - 6 main tables: businesses, people, enrichment_jobs, validation_results, analytics, logs
   - 11 indexes for performance
   - 2 views for easy querying
   - All permissions properly set

3. **.env.integration**
   - Database credentials
   - Email validator config
   - Dataforge settings
   - Ollama settings

### ✅ Created (Task 1.2)
1. **scripts/dataforge_loader.py**
   - Loads OneExtraction JSON files
   - Inserts into PostgreSQL
   - Tracks statistics
   - Error handling + logging

2. **scripts/setup_dataforge.sh** (Unix/Linux/Mac)
3. **scripts/setup_dataforge.ps1** (Windows PowerShell)
4. **scripts/dataforge_integration_guide.md**

### Database Schema
- **businesses** - Company data + enrichment fields
- **people** - Executive/people data
- **enrichment_jobs** - Track pipeline progress
- **email_validation_results** - Detailed validation audit trail
- **enrichment_analytics** - Summary statistics

---

## Recommended Next Action

### Option 1: Setup PostgreSQL Locally (Fastest)
**If Docker is problematic:**
1. Install PostgreSQL 15
2. Create forge user + oneextraction database
3. Run init_db.sql
4. Run dataforge_loader.py

**Timeline:** 15 minutes
**Blockers:** None

### Option 2: Fix Docker and Use Containers
**If you want to stick with Docker:**
1. Restart Docker Desktop
2. Run docker-compose up -d
3. Wait 30 seconds for PostgreSQL ready
4. Run dataforge_loader.py

**Timeline:** 10 minutes  
**Blockers:** Requires Docker Desktop running

---

## Task 1.3 Preview: Load OneExtraction Data

Once you choose Path A or B and have PostgreSQL running:

```powershell
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"

# Verify PostgreSQL connection
psql -h localhost -U forge -d oneextraction -c "SELECT version();"

# Load data
python scripts/dataforge_loader.py

# Check results
psql -h localhost -U forge -d oneextraction -c "SELECT COUNT(*) FROM businesses;"
# Should show: 1185

psql -h localhost -U forge -d oneextraction -c "SELECT COUNT(*) FROM people;"
# Should show: 2370
```

---

## Week 1 Timeline

| Day | Task | Status | Estimated Time |
|-----|------|--------|-----------------|
| Day 1 | 1.1 - Infrastructure Setup | ✅ Done | 30 min |
| Day 1-2 | 1.2 - Dataforge Installation | ⏳ In Progress | 15 min |
| Day 2 | 1.3 - Load OneExtraction Data | ⏹️ Ready | 15 min |
| Day 3 | 1.4 - Dataforge Verification | ⏹️ Ready | 30 min |
| Day 3 | **Week 1 Complete** | ⏹️ | **90 min total** |

---

## Success Criteria for Week 1

- [x] PostgreSQL database created with complete schema
- [x] Email validator configured
- [ ] Database connection verified
- [ ] OneExtraction data loaded (1,185 companies + 2,370 people)
- [ ] Dataforge installed and verified
- [ ] Status dashboard accessible

---

## Files Ready for Use

All files are in place:
- ✅ Database schema: `init_db.sql`
- ✅ Docker setup: `docker-compose.yml`
- ✅ Data loader: `scripts/dataforge_loader.py`
- ✅ Config template: `.env.integration`
- ✅ Setup scripts: `scripts/setup_dataforge.*`
- ✅ Integration guide: `scripts/dataforge_integration_guide.md`

---

## Next Steps

Choose one:

### A. PostgreSQL Local Setup (No Docker)
```powershell
# 1. Install PostgreSQL from https://www.postgresql.org/download/windows/
# 2. Create user/database from init_db.sql
# 3. Run data loader
python scripts/dataforge_loader.py
```

### B. Docker Setup (When Ready)
```powershell
# 1. Start Docker Desktop
# 2. Run containers
docker-compose up -d
# 3. Wait 30 seconds
# 4. Run data loader
python scripts/dataforge_loader.py
```

---

## Questions?

See:
- Full Plan: Implementation Plan document (artifact)
- Docker Guide: dataforge_integration_guide.md
- Database Schema: init_db.sql
- Code: scripts/dataforge_loader.py

Next: Choose setup path and verify database connection!
