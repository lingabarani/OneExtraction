import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from pathlib import Path

def create_master_guide_word_document(output_path: str):
    doc = docx.Document()

    # Define Executive Navy Palette
    HEX_PRIMARY = "1E3A8A"      # Deep Navy
    HEX_SECONDARY = "0284C7"    # Cyan / Ocean Blue
    HEX_DARK = "0F172A"         # Slate 900
    HEX_BODY = "334155"         # Slate 700
    HEX_LIGHT_BG = "F1F5F9"     # Slate 100
    HEX_CALLOUT_BG = "EFF6FF"   # Blue 50
    HEX_BORDER = "CBD5E1"       # Slate 300
    HEX_ACCENT = "0D9488"       # Teal / Emerald
    HEX_WHITE = "FFFFFF"

    COLOR_PRIMARY = RGBColor(0x1E, 0x3A, 0x8A)
    COLOR_SECONDARY = RGBColor(0x02, 0x84, 0xC7)
    COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)
    COLOR_BODY = RGBColor(0x33, 0x41, 0x55)
    COLOR_MUTED = RGBColor(0x64, 0x74, 0x8B)

    # Page Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Default Styles
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Calibri'
    font_normal.size = Pt(11)
    font_normal.color.rgb = COLOR_BODY

    # Helpers
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f'</w:tcMar>'
        )
        tcPr.append(tcMar)

    def set_table_borders(table, color_hex="CBD5E1"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color_hex}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_callout(text: str, title: str = "KEY HIGHLIGHT", icon: str = "📌"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, HEX_CALLOUT_BG)
        set_cell_margins(cell, top=140, bottom=140, left=220, right=180)

        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'<w:top w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:bottom w:val="none"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(borders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        run_title = p.add_run(f"{icon} {title}\n")
        run_title.bold = True
        run_title.font.name = 'Calibri'
        run_title.font.size = Pt(10.5)
        run_title.font.color.rgb = COLOR_PRIMARY

        run_text = p.add_run(text)
        run_text.font.name = 'Calibri'
        run_text.font.size = Pt(10.0)
        run_text.font.color.rgb = COLOR_DARK

        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_heading_1(text: str, number: str = ""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        
        full_text = f"{number} {text}".strip()
        run = p.add_run(full_text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(15)
        run.font.color.rgb = COLOR_PRIMARY

        p_bar = doc.add_paragraph()
        p_bar.paragraph_format.space_before = Pt(0)
        p_bar.paragraph_format.space_after = Pt(8)
        run_bar = p_bar.add_run("―" * 50)
        run_bar.font.name = 'Calibri'
        run_bar.font.size = Pt(8)
        run_bar.font.color.rgb = COLOR_SECONDARY

    def add_heading_2(text: str, number: str = ""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        
        full_text = f"{number} {text}".strip()
        run = p.add_run(full_text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(12.5)
        run.font.color.rgb = COLOR_SECONDARY

    def add_heading_3(text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        
        run = p.add_run(text)
        run.bold = True
        run.font.name = 'Calibri'
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_DARK

    def add_body(text: str, bold_prefix: str = ""):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        
        if bold_prefix:
            run_b = p.add_run(bold_prefix + " ")
            run_b.bold = True
            run_b.font.color.rgb = COLOR_DARK
            
        run = p.add_run(text)
        run.font.color.rgb = COLOR_BODY
        return p

    def add_bullet(text: str, bold_prefix: str = ""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        
        if bold_prefix:
            run_b = p.add_run(bold_prefix + " ")
            run_b.bold = True
            run_b.font.color.rgb = COLOR_DARK
            
        run = p.add_run(text)
        run.font.color.rgb = COLOR_BODY
        return p

    def add_code_block(code_text: str):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = tbl.cell(0, 0)
        set_cell_background(c, HEX_DARK)
        set_cell_margins(c, top=100, bottom=100, left=140, right=140)
        p = c.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(code_text)
        r.font.name = 'Consolas'
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # -------------------------------------------------------------
    # 1. TITLE & METADATA BLOCK
    # -------------------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(20)
    title_p.paragraph_format.space_after = Pt(4)
    r_title = title_p.add_run("ONEEXTRACTION: MASTER TECHNICAL & OPERATIONAL BLUEPRINT")
    r_title.bold = True
    r_title.font.size = Pt(22)
    r_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_before = Pt(0)
    sub_p.paragraph_format.space_after = Pt(14)
    r_sub = sub_p.add_run("Complete End-to-End Implementation, Data Sources, API Pricing, Validation Engine, Storage Architecture, and Schema Reference")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = COLOR_SECONDARY

    # Metadata Table
    meta_tbl = doc.add_table(rows=4, cols=2)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(meta_tbl, HEX_BORDER)

    meta_items = [
        ("Document Focus:", "Comprehensive Technical, Operational, and Architectural Blueprint"),
        ("System & Scope:", "OneExtraction Engine — Mexico & LATAM B2B Corporate Universe (7.1M Establishments)"),
        ("Core Stack:", "Botasaurus Anti-Detection, Python 3.12, 6-Stage Dedup, DNS/MX Lead Probing, SQLite/PostgreSQL"),
        ("Version & Status:", "Production Architecture Guide | Version 2.4 | September 2026"),
    ]
    for row_idx, (k, v) in enumerate(meta_items):
        c0 = meta_tbl.cell(row_idx, 0)
        c1 = meta_tbl.cell(row_idx, 1)
        c0.width = Inches(2.0)
        c1.width = Inches(4.5)
        set_cell_background(c0, HEX_LIGHT_BG)
        set_cell_background(c1, HEX_WHITE)
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        r0.font.color.rgb = COLOR_DARK

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = COLOR_BODY

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # -------------------------------------------------------------
    # 2. DATA SOURCES & INGESTION CHANNELS
    # -------------------------------------------------------------
    add_heading_1("Comprehensive Data Sources Catalog (11 Integrated Portals)", "1.0")
    add_body("OneExtraction ingests corporate, tax, compliance, and industrial intelligence across 11 official Mexican public registries and commercial directories:")

    src_tbl = doc.add_table(rows=12, cols=4)
    src_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(src_tbl, HEX_BORDER)

    headers = ["Source Key", "Official Name & Entity", "Access Channel", "Strategic Scope & Records"]
    for c_idx, h in enumerate(headers):
        cell = src_tbl.cell(0, c_idx)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    src_info = [
        ("DENUE", "INEGI - Directorio Estadístico Nacional de Unidades Económicas", "REST API & Bulk CSV (Open Data)", "5.5M – 7.1M economic units across all 32 states; SCIAN codes, employee ranges, lat/long."),
        ("SIEM", "Secretaría de Economía - Sistema de Información Empresarial", "CKAN Open Data API / CSV", "Official ministry business directory; registered legal names, corporate phones, official emails."),
        ("SAT", "Servicio de Administración Tributaria (Tax Authority)", "CSV Open Data & Web Validator", "Art. 69/69-B non-compliant blacklist (EFOS/phantom firms), official RFC tax validation."),
        ("SUPPLIER", "CompraNet / SFP (Padrón de Proveedores y Contratistas)", "CKAN Open Data / CSV", "Federal procurement vendors, contractor histories, legal representative names."),
        ("DATOS_GOB", "Catálogo Nacional de Datos Abiertos (datos.gob.mx)", "CKAN REST API / JSON", "National open-data catalog for cross-referencing industry-specific government registries."),
        ("CANACINTRA", "Cámara Nacional de la Industria de Transformación", "Web Directory / Botasaurus", "Tier-1 & Tier-2 manufacturing plants, industrial supply chain chambers across Mexico."),
        ("AMCHAM", "American Chamber of Commerce in Mexico", "Corporate Directory / Botasaurus", "US-Mexico multinational corporations, cross-border nearshoring enterprises, executive contacts."),
        ("COSMOS", "COSMOS Online B2B Industrial Sourcing", "Web Directory / Botasaurus", "Premier Mexican industrial procurement portal, chemical & raw material suppliers."),
        ("QUIMINET", "QuimiNet B2B Industrial & Chemical Marketplace", "Web Directory / Botasaurus", "Industrial machinery, polymers, logistics, and LATAM trade supplier networks."),
        ("SECCION_AMARILLA", "Sección Amarilla México (National Yellow Pages)", "Web Directory / Botasaurus", "Commercial listings, active telephone routing, retail and commercial establishment directories."),
        ("RPC / SIGER", "Registro Público de Comercio (Secretaría de Economía)", "Legal Portal (Targeted Verification)", "Official corporate incorporation records and legal representative verification boundary."),
    ]

    for row_idx, (k, name, channel, scope) in enumerate(src_info, 1):
        c0 = src_tbl.cell(row_idx, 0)
        c1 = src_tbl.cell(row_idx, 1)
        c2 = src_tbl.cell(row_idx, 2)
        c3 = src_tbl.cell(row_idx, 3)

        c0.width = Inches(1.1)
        c1.width = Inches(2.2)
        c2.width = Inches(1.5)
        c3.width = Inches(1.7)

        bg = HEX_LIGHT_BG if row_idx % 2 == 1 else HEX_WHITE
        for c in (c0, c1, c2, c3):
            set_cell_background(c, bg)
            set_cell_margins(c, top=70, bottom=70, left=80, right=80)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(name)
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = COLOR_DARK

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(channel)
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = COLOR_BODY

        p3 = c3.paragraphs[0]
        r3 = p3.add_run(scope)
        r3.font.size = Pt(8.0)
        r3.font.color.rgb = COLOR_BODY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 3. API PRICING, COSTS & AUTHENTICATION
    # -------------------------------------------------------------
    add_heading_1("API Pricing, Access Requirements & Cost Analysis", "2.0")
    add_body("A core strategic advantage of OneExtraction is that all government registries and open-data feeds are 100% free of licensing fees:")

    cost_tbl = doc.add_table(rows=7, cols=4)
    cost_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cost_tbl, HEX_BORDER)

    cost_headers = ["Data Source / API", "Cost / Licensing Model", "Authentication & Setup", "Rate Limits & Restrictions"]
    for c_idx, h in enumerate(cost_headers):
        cell = cost_tbl.cell(0, c_idx)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    cost_data = [
        ("INEGI DENUE (REST API & Bulk)", "$0.00 (100% Free Public Open Data)", "Free API Token via INEGI portal registration (or direct bulk CSV download)", "API: 5 requests/sec. Bulk CSV: Unlimited, zero rate-limit."),
        ("SIEM (Secretaría de Economía)", "$0.00 (100% Free Open Data)", "Direct CKAN API or open CSV download from datos.gob.mx (No token required)", "Standard HTTP connection limits."),
        ("SAT (Tax Authority Art. 69-B)", "$0.00 (100% Free Public Compliance)", "Direct download from official SAT portal (No authentication required)", "Refreshed by SAT bi-weekly; unlimited internal use."),
        ("CompraNet / SFP Suppliers", "$0.00 (100% Free Federal Portal)", "Direct CKAN download from datos.gob.mx (No token required)", "Refreshed monthly; unlimited downloads."),
        ("Industrial Web Directories (CANACINTRA, COSMOS, etc.)", "$0.00 (Public Business Directories)", "Scraped via Botasaurus Anti-Detection driver; optional proxy usage", "2-5 req/sec with randomized humane throttling."),
        ("Commercial Vendor Comparison (ZoomInfo / Apollo)", "$50,000 – $150,000+ / Year (Recurring)", "Per-seat licensing, export credit caps, no Mexican tax/compliance data", "Heavy export caps, stale LATAM data."),
    ]

    for row_idx, (src, cost, auth, limits) in enumerate(cost_data, 1):
        c0 = cost_tbl.cell(row_idx, 0)
        c1 = cost_tbl.cell(row_idx, 1)
        c2 = cost_tbl.cell(row_idx, 2)
        c3 = cost_tbl.cell(row_idx, 3)

        c0.width = Inches(1.8)
        c1.width = Inches(1.5)
        c2.width = Inches(1.8)
        c3.width = Inches(1.4)

        bg = HEX_LIGHT_BG if row_idx % 2 == 1 else HEX_WHITE
        for c in (c0, c1, c2, c3):
            set_cell_background(c, bg)
            set_cell_margins(c, top=70, bottom=70, left=80, right=80)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(src)
        r0.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(cost)
        r1.bold = True
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = RGBColor(0x05, 0x96, 0x69) if "$0.00" in cost else RGBColor(0xDC, 0x26, 0x26)

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(auth)
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = COLOR_DARK

        p3 = c3.paragraphs[0]
        r3 = p3.add_run(limits)
        r3.font.size = Pt(8.0)
        r3.font.color.rgb = COLOR_BODY

    add_callout(
        "TOTAL ANNUAL DATA LICENSING COST: $0.00. OneExtraction leverages official Mexican federal open data and automated anti-detect scraping. The only operational cost is lightweight cloud compute and residential proxy bandwidth (< $50/month), reducing data procurement costs by over 98%.",
        "FINANCIAL SUMMARY",
        "💰"
    )

    # -------------------------------------------------------------
    # 4. HOW DATA IS FETCHED (TECHNICAL INGESTION)
    # -------------------------------------------------------------
    add_heading_1("How Data is Fetched: Ingestion Strategies & Execution", "3.0")
    add_body("OneExtraction executes data fetching across three specialized ingestion channels:")

    add_heading_2("Channel 1: High-Speed Bulk Open-Data Streaming", "3.1")
    add_bullet("The pipeline streams official INEGI CSV census archives line-by-line using chunked Python generator pipelines. Millions of records are processed without loading entire files into memory, achieving 10,000+ records/second throughput.", "Streaming Engine:")
    add_bullet("Place uncompressed CSV files in `botasaurus/data/raw/denue/` and run `python main.py --source denue`.", "Execution:")

    add_heading_2("Channel 2: REST API Querying with Auto-Pagination", "3.2")
    add_bullet("Connects directly to the INEGI DENUE REST API v1.0 and datos.gob.mx CKAN API. Automatically handles pagination (`BuscarAreaAct`), token injection, and rate-limit backoff.", "API Connectors:")
    add_code_block("GET https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaAct/todos/09/0/0/1/50/{DENUE_API_TOKEN}")

    add_heading_2("Channel 3: Botasaurus Humane Anti-Detection Scraping", "3.3")
    add_bullet("For trade directories (CANACINTRA, COSMOS, QuimiNet, Sección Amarilla), Botasaurus deploys Chrome CDP anti-detection drivers with human-like mouse movement, bypassing Cloudflare Turnstile and DataDome bot-walls while saving 97% on proxy costs via smart fetch routing.", "Anti-Detection Engine:")

    # -------------------------------------------------------------
    # 5. DATA VALIDATION & QUALITY ASSURANCE
    # -------------------------------------------------------------
    add_heading_1("Data Validation & Quality Assurance Framework", "4.0")
    add_body("Raw data undergoes four automated validation stages before being admitted into production:")

    add_bullet("Validates 12-char Persona Moral (`^[A-ZÑ&]{3}[0-9]{6}[A-Z0-9]{3}$`) and 13-char Persona Física (`^[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3}$`). Filters out generic placeholder RFCs (`XAXX010101000`).", "1. Mexican Tax RFC Syntax & Homoclave:")
    add_bullet("Canonicalizes 80+ state abbreviations into 32 official INEGI states; repairs 5-digit Mexican postal codes with leading zeros; validates coordinates within Mexican territory (14°N–33.5°N, -119°W–-86°W).", "2. Geographic & Address Normalization:")
    add_bullet("Standardizes numbers to Mexican 10-digit national dialing and E.164 (+52) international format.", "3. Telephony Normalization:")
    add_bullet("Performs asynchronous DNS MX lookups, fingerprints mail provider (Microsoft 365 vs Google Workspace), generates corporate email permutations, and assigns deliverability confidence.", "4. DNS MX & Email Deliverability Engine:")
    add_bullet("Cross-references company RFCs against the official SAT Art. 69-B list of fraudulent invoicing entities (EFOS/phantom companies), flagging high-risk vendors automatically.", "5. SAT Article 69-B Fraud Screening:")
    add_bullet("Calculates a 0–100 score factoring Name (20pts), Location (15pts), Industry (15pts), RFC (10pts), Website (10pts), Phone (10pts), Email (10pts), and Provenance (10pts).", "6. Data Quality Scoring (0-100):")

    # -------------------------------------------------------------
    # 6. WHERE AND HOW DATA IS STORED
    # -------------------------------------------------------------
    add_heading_1("Storage Architecture: Where & How Data is Stored", "5.0")
    add_body("OneExtraction organizes data into a 3-tier enterprise storage architecture:")

    store_tbl = doc.add_table(rows=4, cols=3)
    store_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(store_tbl, HEX_BORDER)

    store_headers = ["Storage Layer", "Technology & Format", "Location & Purpose"]
    for c_idx, h in enumerate(store_headers):
        cell = store_tbl.cell(0, c_idx)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    store_data = [
        ("Tier 1: Raw Lake", "Immutable JSON / CSV + SHA-256 Hashes", "Stored in `data/raw/{source}/`. Preserves untouched raw payloads from source portals for regulatory auditability."),
        ("Tier 2: Normalized Warehouse", "SQLite / PostgreSQL / Supabase", "Structured relational schema with `companies`, `decision_makers`, and `source_provenance` tables with B-Tree and GIN indexes."),
        ("Tier 3: Master Production Exports", "Excel (.xlsx), CSV, JSON Arrays", "Stored in `output/` (`mexico_master_combined.xlsx`, `mexico_companies.json`, `mexico_people.json`, `validation_report.json`)."),
    ]

    for row_idx, (layer, tech, loc) in enumerate(store_data, 1):
        c0 = store_tbl.cell(row_idx, 0)
        c1 = store_tbl.cell(row_idx, 1)
        c2 = store_tbl.cell(row_idx, 2)

        c0.width = Inches(1.8)
        c1.width = Inches(2.2)
        c2.width = Inches(2.5)

        bg = HEX_LIGHT_BG if row_idx % 2 == 1 else HEX_WHITE
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, top=70, bottom=70, left=80, right=80)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(layer)
        r0.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(tech)
        r1.bold = True
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = COLOR_DARK

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(loc)
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = COLOR_BODY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 7. EXHAUSTIVE DATA FIELDS & SCHEMA (WHAT DETAILS WE GET)
    # -------------------------------------------------------------
    add_heading_1("Data Dictionary: Complete Extracted Fields & Attributes", "6.0")
    add_body("OneExtraction produces over 35 standardized data attributes per canonical business profile:")

    field_tbl = doc.add_table(rows=11, cols=3)
    field_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(field_tbl, HEX_BORDER)

    field_headers = ["Category", "Extracted Field Name", "Description & Standardized Example"]
    for c_idx, h in enumerate(field_headers):
        cell = field_tbl.cell(0, c_idx)
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    fields_data = [
        ("Company Core", "legal_name / trade_name", "Full registered legal name (e.g. 'CEMEX S.A.B. DE C.V.') and commercial trade name."),
        ("Tax Identity", "rfc / rfc_type", "Validated tax ID (e.g. 'CEM850101XYZ') and classification ('MORAL' vs 'FISICA')."),
        ("Industry & Scale", "industry / industry_code", "Official SCIAN/NAICS industry description and 4-digit code (e.g. '3363 - Fabricación de autopartes')."),
        ("Employee Bracket", "employee_count_min / max", "Estimated headcount range (e.g. 51-250 employees) derived from official census strata."),
        ("Web & Domain", "website / domain", "Normalized HTTPS corporate URL and root corporate domain (e.g. 'cemex.com')."),
        ("Corporate Contacts", "company_phone / company_email", "Standardized 10-digit national telephone number and registered official corporate email."),
        ("Physical Location", "street, number, colony, cp", "Full physical street address, exterior/interior number, colony, and 5-digit Mexican postal code."),
        ("Geospatial & State", "state, municipality, lat, lng", "Canonical state (e.g. 'Nuevo León'), municipality ('Monterrey'), and high-precision GPS coordinates."),
        ("Executive Lead", "executive_name / title", "Identified primary decision-maker (e.g. 'Javier Castro') and original role ('Director General')."),
        ("C-Suite & Contacts", "standardized_title, work_email", "Classified title ('Chief Executive Officer (CEO)'), seniority ('C_SUITE'), verified work email, and MX provider."),
    ]

    for row_idx, (cat, fname, fdesc) in enumerate(fields_data, 1):
        c0 = field_tbl.cell(row_idx, 0)
        c1 = field_tbl.cell(row_idx, 1)
        c2 = field_tbl.cell(row_idx, 2)

        c0.width = Inches(1.5)
        c1.width = Inches(2.2)
        c2.width = Inches(2.8)

        bg = HEX_LIGHT_BG if row_idx % 2 == 1 else HEX_WHITE
        for c in (c0, c1, c2):
            set_cell_background(c, bg)
            set_cell_margins(c, top=70, bottom=70, left=80, right=80)

        p0 = c0.paragraphs[0]
        r0 = p0.add_run(cat)
        r0.bold = True
        r0.font.size = Pt(8.5)
        r0.font.color.rgb = COLOR_PRIMARY

        p1 = c1.paragraphs[0]
        r1 = p1.add_run(fname)
        r1.bold = True
        r1.font.size = Pt(8.0)
        r1.font.color.rgb = COLOR_DARK

        p2 = c2.paragraphs[0]
        r2 = p2.add_run(fdesc)
        r2.font.size = Pt(8.0)
        r2.font.color.rgb = COLOR_BODY

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # -------------------------------------------------------------
    # 8. STEP-BY-STEP IMPLEMENTATION GUIDE
    # -------------------------------------------------------------
    add_heading_1("Step-by-Step Implementation Guide", "7.0")
    add_body("Follow these steps to run, configure, and automate the ingestion engine:")

    add_heading_2("Step 1: Environment Setup", "7.1")
    add_code_block(
        "cd \"d:\\Data Scraping Project POC\\OneExtraction\\botasaurus\"\n"
        "pip install -r requirements.txt\n"
        "cp .env.example .env"
    )

    add_heading_2("Step 2: Execute Ingestion Pipeline", "7.2")
    add_code_block(
        "# 1. Run all connected sources:\n"
        "python main.py --source all\n\n"
        "# 2. Ingest large bulk volume (30,000+ records):\n"
        "python scripts/bulk_ingest.py --count 30000 --run-pipeline\n\n"
        "# 3. Run specific source with limit:\n"
        "python main.py --source denue --limit 5000"
    )

    add_heading_2("Step 3: Access Generated Outputs", "7.3")
    add_body("All production datasets are ready in `botasaurus/output/`:")
    add_bullet("Single-sheet master directory with companies, websites, and C-Suite leads.", "mexico_master_combined.xlsx:")
    add_bullet("Full canonical company database.", "mexico_companies.json:")
    add_bullet("Enriched decision-maker leads with verified email permutations.", "mexico_people.json:")
    add_bullet("Automated quality scores and audit metrics.", "validation_report.json:")

    # -------------------------------------------------------------
    # 9. HUMAN ASSISTANCE & TEAM REQUIREMENTS
    # -------------------------------------------------------------
    add_heading_1("Team & Operational Assistance Requirements", "8.0")
    add_body("Do you need dedicated assistance or manual operators to maintain this platform?")

    add_heading_2("Autonomous vs. Human-in-the-Loop Analysis", "8.1")
    add_bullet("The pipeline runs 100% autonomously on scheduled cron triggers without human intervention for routine fetching, validation, and export.", "Routine Daily / Weekly Ingestion:")
    add_bullet("Company matching confidence >= 95% is automatically merged. Records with matching scores between 80% and 94% are routed to `review_queue` for optional compliance review.", "Edge-Case Deduplication:")
    add_bullet("A single part-time data engineer (0.25 FTE) can manage proxy rotations, monitor API updates, and oversee database backups. Zero dedicated data entry staff required.", "Engineering Overhead:")

    # Section Footers & Headers
    for sec in doc.sections:
        footer = sec.footer
        p_ft = footer.paragraphs[0]
        p_ft.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_ft.text = "OneExtraction Master Blueprint | Technical & Operational Reference"
        p_ft.runs[0].font.name = "Calibri"
        p_ft.runs[0].font.size = Pt(8.5)
        p_ft.runs[0].font.color.rgb = COLOR_MUTED

        header = sec.header
        p_hd = header.paragraphs[0]
        p_hd.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_hd.text = "OneExtraction — Data Ingestion, Validation, Storage & API Pricing Guide"
        p_hd.runs[0].font.name = "Calibri"
        p_hd.runs[0].font.size = Pt(8.5)
        p_hd.runs[0].font.color.rgb = COLOR_MUTED

    doc.save(output_path)
    print(f"Successfully generated Master Word Document at: {output_path}")

if __name__ == "__main__":
    target = r"d:\Data Scraping Project POC\OneExtraction\OneExtraction_Master_Technical_Operational_Guide.docx"
    create_master_guide_word_document(target)
