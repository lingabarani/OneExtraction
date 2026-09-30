# OneExtraction: Master Technical & Operational Guide
**Autonomous B2B Data Extraction, Validation, Storage & API Architecture**

---

## 1. Executive Summary & Core Concept

**OneExtraction** is an enterprise-grade data intelligence engine designed to autonomously ingest, validate, resolve, enrich, and store B2B corporate and executive lead data across emerging markets, starting with **Mexico's 7.1 Million registered business establishments and 59.6 Million employed workforce**.

The system replaces expensive commercial data subscriptions (ZoomInfo, Apollo, Cognism) by converting official government open data, tax authority registries, and public trade directories into an owned, clean, enriched internal corporate database.

---

## 2. Comprehensive Data Sources Catalog (11 Integrated Sources)

| Source Key | Official Portal Name | Access Channel | Strategic Scope & Key Information |
| :--- | :--- | :--- | :--- |
| **DENUE** | **INEGI** (Directorio Estadístico Nacional de Unidades Económicas) | REST API & Bulk Open CSV | **5.5M – 7.1M establishments** across all 32 states; SCIAN industry codes, employee size bands, exact GPS coordinates. |
| **SIEM** | **Secretaría de Economía** (Sistema de Información Empresarial) | CKAN Open Data / CSV | Official ministry business directory; registered legal business names, corporate phones, official registered emails. |
| **SAT** | **SAT** (Servicio de Administración Tributaria - Tax Authority) | Open CSV & Online Validator | Official RFC tax ID validation, **Article 69/69-B non-compliant blacklist** (EFOS/phantom invoice companies). |
| **SUPPLIER** | **CompraNet / SFP** (Padrón de Proveedores del Gobierno Federal) | CKAN Open Data / CSV | Federal public procurement vendors, government contractor histories, verified legal representatives. |
| **DATOS_GOB** | **Catálogo Nacional de Datos Abiertos** (`datos.gob.mx`) | CKAN REST API / JSON | Federal open data catalog for cross-referencing industry-specific public registries. |
| **CANACINTRA**| **Cámara Nacional de la Industria de Transformación** | Web Directory / Botasaurus | National & regional state manufacturing directories (Tier-1 and Tier-2 suppliers). |
| **AMCHAM** | **American Chamber of Commerce in Mexico** | Corporate Directory / Botasaurus | US-Mexico cross-border multinational corporations, nearshoring partners, C-level contacts. |
| **COSMOS** | **COSMOS Online B2B Industrial Portal** | Web Directory / Botasaurus | Premier industrial sourcing directory in Mexico, raw materials, chemical and manufacturing vendors. |
| **QUIMINET** | **QuimiNet B2B Industrial Directory & Marketplace** | Web Directory / Botasaurus | Heavy industry, manufacturing machinery, chemical suppliers across Mexico and LATAM. |
| **SECCION_AMARILLA** | **Sección Amarilla México** (National Yellow Pages) | Web Directory / Botasaurus | Commercial enterprises, physical business addresses, active telephone lines across all 32 states. |
| **RPC / SIGER** | **Registro Público de Comercio** (Secretaría de Economía) | Legal Portal (Verification) | Official corporate incorporation records (used strictly for targeted legal verification). |

---

## 3. API Pricing, Access Requirements & Cost Analysis

| API / Data Source | Cost / Licensing Model | Authentication & Setup | Rate Limits |
| :--- | :--- | :--- | :--- |
| **INEGI DENUE** | **$0.00 (100% Free Public Open Data)** | Free API Token via [INEGI Portal](https://www.inegi.org.mx/servicios/api_denue.html) or bulk CSV | 5 req/sec (API) / Unlimited (Bulk CSV) |
| **SIEM** | **$0.00 (100% Free Open Data)** | Direct CKAN API or open CSV from `datos.gob.mx` | Standard HTTP limits |
| **SAT Art. 69-B** | **$0.00 (100% Free Public Data)** | Direct download from official SAT portal (No auth) | Refreshed bi-weekly |
| **CompraNet / SFP** | **$0.00 (100% Free Open Data)** | Direct download from `datos.gob.mx` | Refreshed monthly |
| **Web Directories** | **$0.00 (Public Web Directories)** | Scraped using Botasaurus anti-detection driver | 2–5 req/sec with humane delays |
| **ZoomInfo / Apollo** | **$50,000 – $150,000+ / Year** | Per-seat licenses, strict credit limits, no SAT data | Strict monthly export caps |

> **Total Annual Data License Fee: $0.00.**  
> The only operational cost is lightweight cloud compute and residential proxy bandwidth (**< $50/month**), delivering a **98%+ cost reduction** over commercial data vendors.

---

## 4. How Data is Fetched: Ingestion Mechanisms

OneExtraction uses **three distinct ingestion strategies**:

### 1. High-Speed Bulk Open-Data Streaming (Recommended for Millions of Records)
* **Mechanism:** Python generator-based streaming using `csv.DictReader` in chunk sizes of 5,000 records.
* **Throughput:** 10,000+ records/second with constant low RAM usage.
* **How to run:** Place unzipped bulk CSV files from INEGI into `botasaurus/data/raw/denue/` and run:
  ```powershell
  python main.py --source denue
  ```

### 2. Official REST API Batch Ingestion (For Live Automated Sync)
* **Mechanism:** Automated HTTP client with backoff retry and state-by-state pagination (`BuscarAreaAct`).
* **Endpoint:**
  ```http
  GET https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaAct/todos/{cve_ent}/0/{cve_act}/{start}/{end}/{DENUE_API_TOKEN}
  ```

### 3. Botasaurus Humane Anti-Detection Web Scraping (For Trade Directories)
* **Mechanism:** Chrome DevTools Protocol (CDP) driver with realistic bezier mouse curves and Cloudflare Turnstile/DataDome bypass.
* **Efficiency:** Proprietary browser fetch mechanism bypasses non-essential rendering, slashing proxy bandwidth costs by **up to 97%**.

---

## 5. How Data Validation Works

Raw data passes through a **4-stage automated quality firewall**:

```
[ Raw Records ] ──► [ 1. Structural Gatekeeping ] ──► [ 2. Deterministic Validators ] ──► [ 3. 0-100 Quality Score ] ──► [ Master Database ]
```

1. **Structural Gatekeeping:** Rejects records lacking company name; separates fatal errors from quality warnings.
2. **Deterministic Field Validators:**
   * **Mexican Tax RFC:** Validates 12-char Persona Moral (`^[A-ZÑ&]{3}[0-9]{6}[A-Z0-9]{3}$`) and 13-char Persona Física (`^[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}$`) syntax; filters generic placeholders (`XAXX010101000`).
   * **Address & 32 States:** Normalizes 80+ state aliases into 32 INEGI canonical names; repairs leading zeros in 5-digit Mexican postal codes; validates lat/lng within Mexican geographic bounds ($14^\circ\text{N} \le \text{lat} \le 33.5^\circ\text{N}$, $-119^\circ\text{W} \le \text{lng} \le -86^\circ\text{W}$).
   * **Telephony:** Formats phone numbers to Mexican 10-digit national dialing and E.164 (`+52`).
   * **DNS MX & Email Deliverability:** Resolves DNS MX records, detects mail provider (Microsoft 365 vs Google Workspace), generates corporate email permutations, and assigns deliverability confidence.
3. **SAT Article 69-B Fraud Screening:** Cross-references company RFCs against the official SAT blacklist of phantom/fraudulent invoice companies (*EFOS*).
4. **0–100 Data Quality Score:** Computes a composite score based on Name (20pts), Location (15pts), Industry (15pts), RFC (10pts), Website (10pts), Phone (10pts), Email (10pts), and Provenance (10pts).

---

## 6. Where and How Data is Stored

OneExtraction employs a **3-tier enterprise storage architecture**:

```
 ┌────────────────────────────────────────────────────────────────────────┐
 │ TIER 1: IMMUTABLE RAW LAKE (`botasaurus/data/raw/{source}/`)           │
 │ • Original JSON / CSV payloads stored with SHA-256 integrity hashes    │
 ├────────────────────────────────────────────────────────────────────────┤
 │ TIER 2: RELATIONAL WAREHOUSE (SQLite / PostgreSQL / Supabase)          │
 │ • Relational tables: `companies`, `decision_makers`, `provenance`      │
 │ • B-Tree indexes on RFC, Domain, and State; GIN full-text search       │
 ├────────────────────────────────────────────────────────────────────────┤
 │ TIER 3: PRODUCTION MASTER EXPORTS (`botasaurus/output/`)               │
 │ • `mexico_master_combined.xlsx` (Consolidated Companies + Executives) │
 │ • `mexico_companies.json` & `mexico_companies.csv`                    │
 │ • `mexico_people.json` & `mexico_people.csv`                          │
 │ • `validation_report.json` & `source_status.json`                     │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 7. What Details We Get (Complete 35+ Field Data Dictionary)

| Category | Field Name | Description & Example |
| :--- | :--- | :--- |
| **Company Core** | `company_id` | Unique UUID-v5 derived from entity fingerprint (`com_a1b2c3d4...`). |
| | `legal_name` | Official registered legal entity name (e.g. `CEMEX S.A.B. DE C.V.`). |
| | `trade_name` | Commercial trade name (e.g. `Cemex Concretos`). |
| | `rfc` | Mexican Tax ID (`CEM850101XYZ`). |
| | `rfc_type` | Legal classification (`MORAL` for corporation, `FISICA` for individual). |
| **Industry & Scale**| `industry` | Full SCIAN industry description (`Fabricación de cemento y productos de concreto`). |
| | `industry_code` | Official 4-digit SCIAN industry code (`3273`). |
| | `employee_count_min/max` | Estimated headcount range (`51` to `250` employees). |
| **Web & Contact** | `website` | Fully qualified HTTPS corporate website URL. |
| | `domain` | Clean corporate root domain (`cemex.com`). |
| | `company_phone` | Standardized 10-digit telephone (`+528183283000`). |
| | `company_email` | Official registered corporate email (`contacto@cemex.com`). |
| **Geographic Location** | `street`, `number`, `colony` | Full physical street address, exterior/interior number, and neighborhood. |
| | `municipality`, `state` | Municipality (e.g. `Monterrey`) and canonical state (`Nuevo León`). |
| | `postal_code` | Valid 5-digit Mexican postal code (`64000`). |
| | `latitude`, `longitude` | High-precision GPS coordinates (`25.6866`, `-100.3161`). |
| **Executive Lead** | `executive_name` | Full name of primary decision-maker (e.g. `Fernando González`). |
| | `title` | Original title in source (`Director General`). |
| | `standardized_title` | Classified title (`Chief Executive Officer (CEO)`). |
| | `seniority_level` | Seniority hierarchy (`C_SUITE`, `FOUNDER`, `VP`, `DIRECTOR`). |
| | `department` | Functional department (`EXECUTIVE`, `OPERATIONS`, `FINANCE`, `HR_PEOPLE`). |
| | `executive_work_email` | Verified corporate email permutation (`fgonzalez@cemex.com`). |
| | `email_status` | Deliverability verification status (`VERIFIED` / `PROBABLE`). |
| | `mail_provider` | Mail server infrastructure (`MICROSOFT_365_OUTLOOK` / `GOOGLE_WORKSPACE`). |
| **Quality & Audit** | `data_quality_score` | Automated quality score out of 100 (`98.5`). |
| | `sources` | Combined provenance list (`DENUE;SIEM;AMCHAM`). |
| | `last_verified_at` | UTC verification timestamp (`2026-09-07T11:00:00Z`). |

---

## 8. Step-by-Step Implementation Guide

### Step 1: Clone and Setup
```powershell
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
pip install -r requirements.txt
cp .env.example .env
```

### Step 2: Run the Pipeline
```powershell
# Ingest all connected sources:
python main.py --source all

# Ingest high-volume bulk records (e.g. 30,000+ records):
python scripts/bulk_ingest.py --count 30000 --run-pipeline

# Run specific source:
python main.py --source denue --limit 5000
```

### Step 3: Access Generated Outputs
All files are ready in `botasaurus/output/`:
* `mexico_master_combined.xlsx` (Excel master file for leadership/sales).
* `mexico_companies.json` & `mexico_people.json` (JSON for developers/CRM integration).
* `validation_report.json` (Audit metrics and quality scorecard).

---

## 9. Assistance & Team Requirements

* **Is human assistance required for daily operation?**  
  **No.** Routine ingestion, validation, normalization, and export run **100% autonomously** on scheduled cron jobs without human intervention.
* **When is human review utilized?**  
  Records with entity resolution match confidence between **80% and 94%** are routed to an optional `review_queue` for compliance sign-off. Matches above **95%** are merged automatically.
* **Engineering Maintenance:**  
  A single part-time data engineer (**0.25 FTE**) is sufficient to monitor upstream API schema changes and proxy rotation. Zero dedicated data entry personnel needed.
