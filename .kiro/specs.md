# 🤖 Kiro IDE Specification File: OneExtraction B2B Intelligence

## Workspace Context
- **Root Directory**: `d:\Data Scraping Project POC\OneExtraction`
- **Main Engine**: `botasaurus`
- **MCP Server Entrypoint**: `botasaurus/src/us_b2b/mcp_server.py`
- **Bulk Execution Script**: `botasaurus/scripts/us_bulk_ingest.py`

## Target Scale & Goals
- **Total Records Goal**: 500,000+ (5 Lakhs)
- **Primary Export Format**: JSON (`us_companies.json`, `us_people.json`)
- **Executive Decision-Makers**: 100% C-Suite (CEO, CFO, CTO, VPs) with work emails and phones.

## Registered Sources
1. `CMS_NPI` (7M+ Healthcare Providers)
2. `SEC_EDGAR` (500k+ Corporate Filings)
3. `PROPUBLICA_990` (2M+ IRS 990 Nonprofits)
4. `SAM_GOV` (1M+ Federal Contractors)
5. `USASPENDING` (3M+ Award Recipients)
6. `FCC_ULS` (3M+ Telecom Licenses)
7. `OPENDIRECTORIES` (12M+ Business REST API)
8. `DENUE` (Mexico INEGI Commercial Directory)

## System Architecture Link
Full architectural vision and Mermaid charts: [PROJECT_VISION_AND_SCOPE.md](file:///d:/Data%20Scraping%20Project%20POC/OneExtraction/PROJECT_VISION_AND_SCOPE.md)
