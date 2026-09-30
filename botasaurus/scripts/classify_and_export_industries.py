import os
import json
import re
import unicodedata
import pandas as pd
from collections import OrderedDict

def remove_accents(input_str):
    if not input_str: 
        return ""
    nfkd_form = unicodedata.normalize('NFKD', str(input_str))
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

# Define output directories
BASE_OUTPUT_DIR = r"d:\Data Scraping Project POC\OneExtraction\botasaurus\output"
EXPORTS_DIR = os.path.join(BASE_OUTPUT_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

INPUT_FILE = os.path.join(BASE_OUTPUT_DIR, "mexico_people.json")

print(f"Reading input dataset from: {INPUT_FILE}")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Loaded {len(records):,} records.")

# 11 Industry categories with strict keywords as specified
TAXONOMY = OrderedDict([
    (
        "Industrial Manufacturing & Transformation",
        {
            "code": "01",
            "file": "01_manufacturing.csv",
            "sheet": "Manufacturing",
            "keywords": [
                "METALURGICA", "MAQUINADOS", "GRUPO INDUSTRIAL", "TRANSFORMADORA",
                "ACEROS", "FUNDICION", "HERRAMIENTAS", "ESTRUCTURAS", "MECANICA", "FABRICACION"
            ]
        }
    ),
    (
        "Professional, Corporate & Advisory Services",
        {
            "code": "02",
            "file": "02_corporate_services.csv",
            "sheet": "Corporate Services",
            "keywords": [
                "SERVICIOS INTEGRALES", "CORPORATIVO", "SOLUCIONES", "ASESORES",
                "CONSULTORES", "HOLDING", "ESTRATEGICA", "DESPACHO"
            ]
        }
    ),
    (
        "Wholesale Trade, Sourcing & Distribution",
        {
            "code": "03",
            "file": "03_wholesale_distribution.csv",
            "sheet": "Wholesale & Distribution",
            "keywords": [
                "DISTRIBUIDORA", "COMERCIALIZADORA", "IMPORTADORA", "EXPORTADORA",
                "PROVEEDORA", "MAYOREO", "SUMINISTROS"
            ]
        }
    ),
    (
        "Chemicals, Polymers, Plastics & Packaging",
        {
            "code": "04",
            "file": "04_chemicals_plastics.csv",
            "sheet": "Chemicals & Plastics",
            "keywords": [
                "QUIMICA", "PLASTICOS", "EMPAQUES", "POLIMEROS",
                "ENVASES", "RESINAS", "TERMOFORMADOS", "RECUBRIMIENTOS"
            ]
        }
    ),
    (
        "Logistics, Freight & Transportation",
        {
            "code": "05",
            "file": "05_logistics_freight.csv",
            "sheet": "Logistics & Transport",
            "keywords": [
                "LOGISTICA", "TRANSPORTES", "FLETES", "CARGA",
                "AUTOTRANSPORTES", "DISTRIBUCION Y LOGISTICA", "ALMACENAMIENTO"
            ]
        }
    ),
    (
        "Real Estate, Infrastructure & Construction",
        {
            "code": "06",
            "file": "06_construction_real_estate.csv",
            "sheet": "Construction & Real Estate",
            "keywords": [
                "CONSTRUCCIONES", "INMOBILIARIA", "EDIFICACIONES", "OBRAS",
                "INFRAESTRUCTURA", "DESARROLLOS", "CONSTRUCTORA"
            ]
        }
    ),
    (
        "Technology, IT, Software & Systems",
        {
            "code": "07",
            "file": "07_technology_it.csv",
            "sheet": "Technology & IT",
            "keywords": [
                "TECNOLOGIA", "TECNOLOGIAS", "EQUIPOS Y SISTEMAS", "SOFTWARE",
                "SISTEMAS", "INFORMATICA", "DIGITAL", "NETWORKS"
            ]
        }
    ),
    (
        "Pharmaceuticals, Health & Biotechnology",
        {
            "code": "08",
            "file": "08_pharma_healthcare.csv",
            "sheet": "Pharma & Healthcare",
            "keywords": [
                "FARMACEUTICA", "LABORATORIOS", "SALUD", "MEDICA",
                "BIOTECNOLOGIA", "DIAGNOSTICA", "HOSPITALARIA"
            ]
        }
    ),
    (
        "Food, Beverage & Agribusiness",
        {
            "code": "09",
            "file": "09_food_agribusiness.csv",
            "sheet": "Food & Agribusiness",
            "keywords": [
                "ALIMENTOS", "BEBIDAS", "AGRO", "AGRICOLA",
                "ALIMENTARIA", "GRANOS", "FRUTICOLA"
            ]
        }
    ),
    (
        "Automotive, Autoparts & Aerospace",
        {
            "code": "10",
            "file": "10_automotive_aerospace.csv",
            "sheet": "Automotive & Aerospace",
            "keywords": [
                "AUTOMOTRIZ", "AUTOPARTES", "MOTORES", "AEROESPACIAL",
                "REFACCIONES", "PRECISION"
            ]
        }
    ),
    (
        "Energy, Oil, Gas & Mining",
        {
            "code": "11",
            "file": "11_energy_mining.csv",
            "sheet": "Energy & Mining",
            "keywords": [
                "ENERGIA", "PETROLEO", "GAS", "MINERIA",
                "SOLAR", "RENOVABLES", "POTENCIA", "COMBUSTIBLES"
            ]
        }
    )
])

FALLBACK_CATEGORY = "General Commercial & Services"
FALLBACK_META = {
    "code": "12",
    "file": "12_general_commercial.csv",
    "sheet": "General Commercial",
    "keywords": []
}

# Compile regex patterns for case-insensitive and accent-insensitive matching
compiled_patterns = []
for category, meta in TAXONOMY.items():
    # Build pattern matching any of the keywords
    sub_patterns = [r"\b" + re.escape(kw) + r"\b" if " " not in kw else re.escape(kw) for kw in meta["keywords"]]
    combined_regex = re.compile("|".join(sub_patterns), re.IGNORECASE)
    compiled_patterns.append((category, meta, combined_regex))

# Process and classify each record
classified_data = []

# Target schema columns
TARGET_COLUMNS = [
    "industry",
    "company_name",
    "company_domain",
    "full_name",
    "standardized_title",
    "seniority_level",
    "department",
    "work_email",
    "email_status",
    "email_confidence_score",
    "direct_phone",
    "created_at"
]

for rec in records:
    c_name = rec.get("company_name", "") or ""
    c_domain = rec.get("company_domain", "") or ""
    
    # Text to match against: normalized company name and domain
    search_text = f"{remove_accents(c_name).upper()} {remove_accents(c_domain).upper()}"
    
    assigned_industry = FALLBACK_CATEGORY
    assigned_meta = FALLBACK_META
    
    for category, meta, regex in compiled_patterns:
        if regex.search(search_text):
            assigned_industry = category
            assigned_meta = meta
            break
            
    row = {
        "industry": assigned_industry,
        "company_name": c_name,
        "company_domain": c_domain,
        "full_name": rec.get("full_name") or f"{rec.get('first_name', '')} {rec.get('last_name', '')}".strip(),
        "standardized_title": rec.get("standardized_title") or rec.get("title", ""),
        "seniority_level": rec.get("seniority_level") or rec.get("seniority", ""),
        "department": rec.get("department", ""),
        "work_email": rec.get("work_email") or rec.get("email", ""),
        "email_status": rec.get("email_status", ""),
        "email_confidence_score": rec.get("email_confidence_score", ""),
        "direct_phone": rec.get("direct_phone") or rec.get("phone", ""),
        "created_at": rec.get("created_at", "")
    }
    classified_data.append(row)

df = pd.DataFrame(classified_data, columns=TARGET_COLUMNS)

# 1. Export Master Classified CSV
master_csv_path = os.path.join(BASE_OUTPUT_DIR, "mexico_leads_master_classified.csv")
df.to_csv(master_csv_path, index=False, encoding="utf-8-sig")
print(f"\n[1/3] Generated Master Classified CSV: {master_csv_path} ({len(df):,} rows)")

# 2. Export Split CSV Files into exports/
print("\n[2/3] Generating 11+ Split CSV Files in exports/ ...")
split_files_summary = []

for category, meta, _ in compiled_patterns:
    sub_df = df[df["industry"] == category]
    file_path = os.path.join(EXPORTS_DIR, meta["file"])
    sub_df.to_csv(file_path, index=False, encoding="utf-8-sig")
    unique_companies = sub_df["company_name"].nunique()
    split_files_summary.append({
        "code": meta["code"],
        "industry": category,
        "sheet": meta["sheet"],
        "file": meta["file"],
        "leads_count": len(sub_df),
        "companies_count": unique_companies
    })
    print(f"  -> {meta['file']}: {len(sub_df):,} leads, {unique_companies:,} companies")

# Handle fallback if any
fallback_df = df[df["industry"] == FALLBACK_CATEGORY]
if len(fallback_df) > 0:
    fb_path = os.path.join(EXPORTS_DIR, FALLBACK_META["file"])
    fallback_df.to_csv(fb_path, index=False, encoding="utf-8-sig")
    fb_companies = fallback_df["company_name"].nunique()
    split_files_summary.append({
        "code": FALLBACK_META["code"],
        "industry": FALLBACK_CATEGORY,
        "sheet": FALLBACK_META["sheet"],
        "file": FALLBACK_META["file"],
        "leads_count": len(fallback_df),
        "companies_count": fb_companies
    })
    print(f"  -> {FALLBACK_META['file']}: {len(fallback_df):,} leads, {fb_companies:,} companies")

# 3. Export Consolidated Multi-Sheet Excel Workbook
excel_path = os.path.join(BASE_OUTPUT_DIR, "mexico_leads_by_industry.xlsx")
print(f"\n[3/3] Generating Consolidated Multi-Tab Excel: {excel_path} ...")

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    for item in split_files_summary:
        industry_name = item["industry"]
        sheet_name = item["sheet"][:31]  # Strict Excel 31 character sheet name limit
        sub_df = df[df["industry"] == industry_name]
        sub_df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Excel generation complete: {excel_path}")

# 4. Console Audit Table
print("\n" + "="*90)
print(f"{'MEXICO B2B DATASET - INDUSTRY CLASSIFICATION AUDIT REPORT':^90}")
print("="*90)
print(f"{'#':<3} | {'Industry Category':<43} | {'Excel Tab':<22} | {'Leads':<8} | {'Companies':<9}")
print("-" * 90)

total_leads_check = 0
for idx, s in enumerate(split_files_summary, 1):
    total_leads_check += s["leads_count"]
    print(f"{s['code']:<3} | {s['industry'][:43]:<43} | {s['sheet'][:22]:<22} | {s['leads_count']:<8,d} | {s['companies_count']:<9,d}")

print("-" * 90)
total_unique_companies = df["company_name"].nunique()
print(f"{'TOTAL AUDIT PARITY CHECK':<71} | {total_leads_check:<8,d} | {total_unique_companies:<9,d}")
print("="*90)

assert total_leads_check == len(records), f"Error: Mismatch in total records! Expected {len(records)}, got {total_leads_check}"
print(f"\nVerification Passed: 100% of {len(records):,} records successfully classified and accounted for with ZERO record loss.")
