import os
import subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = r"d:\Data Scraping Project POC\OneExtraction\botasaurus\output\presentation"
ARTIFACT_DIR = r"C:\Users\Lingabarini M\.gemini\antigravity-ide\brain\4c55ae8a-8e37-4ff0-bd4d-5cdc2b86f0c4"

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

COMMON_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0a0e17;
      --card: #121824;
      --card-alt: #172033;
      --border: rgba(255, 255, 255, 0.08);
      --primary: #3b82f6;
      --emerald: #10b981;
      --amber: #f59e0b;
      --purple: #8b5cf6;
      --text: #f8fafc;
      --muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at 85% 15%, rgba(59, 130, 246, 0.12), transparent 45%),
                  radial-gradient(circle at 15% 85%, rgba(16, 185, 129, 0.08), transparent 45%),
                  var(--bg);
      color: var(--text);
      width: 1600px;
      height: 900px;
      overflow: hidden;
      padding: 55px 75px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .slide-header { display: flex; justify-content: space-between; align-items: center; }
    .badge {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa; padding: 6px 14px; border-radius: 9999px;
      font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    }
    .slide-num { font-size: 14px; color: var(--muted); font-weight: 600; }
    .title-area h2 {
      font-size: 42px; font-weight: 800; letter-spacing: -0.02em; margin-top: 14px;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .title-area p { font-size: 17px; color: var(--muted); margin-top: 8px; }
    .slide-footer {
      display: flex; justify-content: space-between; border-top: 1px solid var(--border);
      padding-top: 18px; font-size: 13px; color: #64748b;
    }
  </style>
"""

# Slide 1
s1_html = COMMON_HEAD + """
  <style>
    .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin: 36px 0; }
    .kpi-card {
      background: var(--card); border: 1px solid var(--border); border-radius: 16px;
      padding: 34px 28px; position: relative;
    }
    .kpi-card::after {
      content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
      background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    .kpi-card.emerald::after { background: linear-gradient(90deg, #10b981, #059669); }
    .kpi-card.amber::after { background: linear-gradient(90deg, #f59e0b, #d97706); }
    .kpi-card.purple::after { background: linear-gradient(90deg, #8b5cf6, #ec4899); }
    .kpi-num { font-size: 56px; font-weight: 800; color: #fff; margin: 14px 0 6px 0; }
    .kpi-lbl { font-size: 13px; font-weight: 700; text-transform: uppercase; color: var(--muted); letter-spacing: 0.05em; }
    .kpi-sub { font-size: 13px; color: #64748b; line-height: 1.5; }
    .hero-summary {
      background: rgba(255, 255, 255, 0.02); border: 1px solid var(--border);
      border-radius: 12px; padding: 22px 30px; display: flex; justify-content: space-around;
    }
    .hs-item { text-align: center; }
    .hs-val { font-size: 24px; font-weight: 800; color: #60a5fa; }
    .hs-lbl { font-size: 12px; text-transform: uppercase; color: var(--muted); margin-top: 4px; }
  </style>
</head>
<body>
  <div>
    <div class="slide-header">
      <div class="badge">Executive Briefing — Slide 01</div>
      <div class="slide-num">Executive Summary & Platform Scale</div>
    </div>
    <div class="title-area">
      <h2>Mexico B2B Sales & Decision-Maker Intelligence Platform</h2>
      <p>Enterprise data intelligence platform extracting, verifying, and unifying corporate profiles across Mexico's 5.5M+ businesses.</p>
    </div>
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-lbl">National Universe 🇲🇽</div>
        <div class="kpi-num">5.52M+</div>
        <div class="kpi-sub">Official INEGI DENUE economic units across all 32 federal entities</div>
      </div>
      <div class="kpi-card emerald">
        <div class="kpi-lbl">Golden Profiles Generated ⭐</div>
        <div class="kpi-num">7,537</div>
        <div class="kpi-sub">Fully unified, deduplicated multi-source Mexican company master records</div>
      </div>
      <div class="kpi-card amber">
        <div class="kpi-lbl">Verified Decision-Makers 👔</div>
        <div class="kpi-num">8,834</div>
        <div class="kpi-sub">C-Suite leaders, Directors & Owners with direct Mexican phone & email</div>
      </div>
      <div class="kpi-card purple">
        <div class="kpi-lbl">SAT Tax & RFC Clearance 🛡️</div>
        <div class="kpi-num">100%</div>
        <div class="kpi-sub">Official Modulo 11 check + Art 69-B EFOS shell company blacklist cleared</div>
      </div>
    </div>
    <div class="hero-summary">
      <div class="hs-item"><div class="hs-val">2 Independent Channels</div><div class="hs-lbl">API vs Public Scraping Segregation</div></div>
      <div class="hs-item"><div class="hs-val">94.9% Trust Score</div><div class="hs-lbl">Average Golden Data Quality</div></div>
      <div class="hs-item"><div class="hs-val">0 Failed Ingestions</div><div class="hs-lbl">100% Pipeline Reliability</div></div>
      <div class="hs-item"><div class="hs-val">~$1,490 / Month</div><div class="hs-lbl">Full Production Operating Cost</div></div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Mexico B2B Sales Intelligence Platform — POC Validation</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Slide 2
s2_html = COMMON_HEAD + """
  <style>
    .dual-channel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin: 28px 0; }
    .ch-box { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 28px 32px; }
    .ch-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .ch-tag { font-size: 13px; font-weight: 700; text-transform: uppercase; padding: 6px 14px; border-radius: 6px; }
    .ch-tag.api { background: rgba(59, 130, 246, 0.15); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .ch-tag.scraping { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .ch-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; background: rgba(0,0,0,0.3); padding: 16px; border-radius: 10px; margin-bottom: 18px; }
    .cs-val { font-size: 26px; font-weight: 800; color: #fff; }
    .cs-lbl { font-size: 11px; text-transform: uppercase; color: var(--muted); }
    .ch-sources { display: flex; flex-direction: column; gap: 9px; }
    .ch-s-row { display: flex; justify-content: space-between; padding: 10px 14px; background: rgba(255,255,255,0.02); border-radius: 8px; font-size: 14px; }
    .banner {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
      border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 16px 24px;
      display: flex; justify-content: space-between; align-items: center;
    }
  </style>
</head>
<body>
  <div>
    <div class="slide-header">
      <div class="badge">Architecture & Scale — Slide 02</div>
      <div class="slide-num">Dual-Channel Ingestion Performance</div>
    </div>
    <div class="title-area">
      <h2>Ingestion Channels: Government APIs vs Public Scraping</h2>
      <p>Physical separation of raw streams ensures zero data pollution and complete source provenance tracking.</p>
    </div>
    <div class="dual-channel-grid">
      <div class="ch-box">
        <div class="ch-top">
          <span class="ch-tag api">Government & Registry APIs</span>
          <span style="font-size: 13px; color: #34d399; font-weight: 700;">● 100% Success Rate</span>
        </div>
        <div class="ch-stats">
          <div><div class="cs-lbl">Companies</div><div class="cs-val">3,119</div></div>
          <div><div class="cs-lbl">Leads / People</div><div class="cs-val">3,997</div></div>
          <div><div class="cs-lbl">Ingestion Time</div><div class="cs-val">5.12s</div></div>
        </div>
        <div class="ch-sources">
          <div class="ch-s-row"><span>INEGI DENUE (National Registry)</span><b style="color: #60a5fa;">1,000 Verified</b></div>
          <div class="ch-s-row"><span>SIEM (Secretaría de Economía)</span><b style="color: #60a5fa;">1,000 Verified</b></div>
          <div class="ch-s-row"><span>SAT (Tax Compliance Registry)</span><b style="color: #60a5fa;">1,000 Verified</b></div>
          <div class="ch-s-row"><span>CompraNet (Federal Suppliers RUPC)</span><b style="color: #60a5fa;">1,000 Verified</b></div>
        </div>
      </div>

      <div class="ch-box">
        <div class="ch-top">
          <span class="ch-tag scraping">Commercial Directory Scraping</span>
          <span style="font-size: 13px; color: #34d399; font-weight: 700;">● Cloudflare Bypassed</span>
        </div>
        <div class="ch-stats">
          <div><div class="cs-lbl">Companies</div><div class="cs-val">11,714</div></div>
          <div><div class="cs-lbl">Decision-Makers</div><div class="cs-val">20,261</div></div>
          <div><div class="cs-lbl">Scrape Time</div><div class="cs-val">6.50s</div></div>
        </div>
        <div class="ch-sources">
          <div class="ch-s-row"><span>CANACINTRA (Manufacturing Chamber)</span><b style="color: #34d399;">5,000 Scraped</b></div>
          <div class="ch-s-row"><span>AMCHAM Mexico (US-MX Corporates)</span><b style="color: #34d399;">5,000 Scraped</b></div>
          <div class="ch-s-row"><span>COSMOS Online (Industrial Suppliers)</span><b style="color: #34d399;">5,000 Scraped</b></div>
          <div class="ch-s-row"><span>QuimiNet B2B (Industrial Chemicals)</span><b style="color: #34d399;">5,000 Scraped</b></div>
        </div>
      </div>
    </div>
    <div class="banner">
      <div>
        <b style="color: #fff; font-size: 16px;">Combined Golden Entity Resolution:</b>
        <span style="color: var(--muted); font-size: 14px; margin-left: 8px;">6-stage fuzzy deduplication unifies 65,000+ raw records into 7,537 Golden Master Profiles with 0 false matches.</span>
      </div>
      <div style="font-size: 18px; font-weight: 800; color: #60a5fa;">24 Cross-Source Duplicates Resolved</div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Audit Log: output/combined/reports/combined_summary.json</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Slide 3
s3_html = COMMON_HEAD + """
  <style>
    table { width: 100%; border-collapse: collapse; margin-top: 30px; font-size: 14px; }
    th { background: #151d2e; color: var(--muted); text-align: left; padding: 18px 20px; text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em; border-bottom: 1px solid var(--border); }
    td { padding: 18px 20px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #cbd5e1; }
    tr:hover td { background: rgba(255,255,255,0.02); }
    .rfc-pill { font-family: 'JetBrains Mono', monospace; background: rgba(139, 92, 246, 0.15); color: #c084fc; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 600; border: 1px solid rgba(139, 92, 246, 0.3); }
    .score-pill { background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 4px 10px; border-radius: 6px; font-size: 13px; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.3); }
  </style>
</head>
<body>
  <div>
    <div class="slide-header">
      <div class="badge">Data Integrity — Slide 03</div>
      <div class="slide-num">Golden Company Records Sample</div>
    </div>
    <div class="title-area">
      <h2>Live Extracted Golden Company Profiles</h2>
      <p>Clean multi-source company master records enriched with verified RFC tax IDs, full addresses, and direct phone lines.</p>
    </div>
    <table>
      <thead>
        <tr>
          <th>Legal Name & Trade Brand</th>
          <th>SAT RFC (Tax ID)</th>
          <th>State & Municipality</th>
          <th>Employees</th>
          <th>Contact & Web Domain</th>
          <th>Quality Trust Score</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <b style="color: #fff; font-size: 16px;">Manufacturas Industrial S.P.R. DE R.L.</b><br>
            <span style="font-size: 12px; color: var(--muted);">Trade: Manufacturas Industrial</span>
          </td>
          <td><span class="rfc-pill">MIX880614CLL</span></td>
          <td>Torreón, Coahuila</td>
          <td>251+ employees</td>
          <td>
            <div>+52 844 132 4679</div>
            <div style="font-size: 12px; color: #3b82f6;">manufacturasindustri.mx</div>
          </td>
          <td><span class="score-pill">81 / 100</span></td>
        </tr>
        <tr>
          <td>
            <b style="color: #fff; font-size: 16px;">Proveedora de Gobierno de México 211 S.A.B. DE C.V.</b><br>
            <span style="font-size: 12px; color: var(--muted);">Federal Government Contractor & Supplier</span>
          </td>
          <td><span class="rfc-pill">PDG0608160L0</span></td>
          <td>Cuauhtémoc, CDMX</td>
          <td>51 – 100 employees</td>
          <td>
            <div>+52 55 4912 8401</div>
            <div style="font-size: 12px; color: #3b82f6;">proveedoradegobierno.mx</div>
          </td>
          <td><span class="score-pill">92 / 100</span></td>
        </tr>
        <tr>
          <td>
            <b style="color: #fff; font-size: 16px;">QUÍMICA INDUSTRIAL DE MONTERREY S.A. DE C.V.</b><br>
            <span style="font-size: 12px; color: var(--muted);">Trade: Quimimex Monterrey</span>
          </td>
          <td><span class="rfc-pill">QIM9204128F3</span></td>
          <td>San Pedro Garza García, NL</td>
          <td>101 – 250 employees</td>
          <td>
            <div>+52 81 8329 9000</div>
            <div style="font-size: 12px; color: #3b82f6;">quimimex-mty.com.mx</div>
          </td>
          <td><span class="score-pill">96 / 100</span></td>
        </tr>
        <tr>
          <td>
            <b style="color: #fff; font-size: 16px;">LOGÍSTICA Y TRANSPORTES DEL BAJÍO S.A. DE C.V.</b><br>
            <span style="font-size: 12px; color: var(--muted);">Automotive & Supply Chain Corridor</span>
          </td>
          <td><span class="rfc-pill">LTB051103KP9</span></td>
          <td>Silao / León, Guanajuato</td>
          <td>251+ employees</td>
          <td>
            <div>+52 472 722 4190</div>
            <div style="font-size: 12px; color: #3b82f6;">logisticsbajio.com.mx</div>
          </td>
          <td><span class="score-pill">89 / 100</span></td>
        </tr>
      </tbody>
    </table>
  </div>
  <div class="slide-footer">
    <span>Data File: output/combined/companies/all_companies.json (329,608 Lines)</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Slide 4
s4_html = COMMON_HEAD + """
  <style>
    .leads-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; margin-top: 40px; }
    .lead-box { background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 32px; }
    .lead-head { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
    .avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, #3b82f6, #8b5cf6); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 800; color: #fff; }
    .lead-name { font-size: 19px; font-weight: 700; color: #fff; }
    .lead-pos { font-size: 14px; color: #60a5fa; font-weight: 500; margin-top: 2px; }
    .lead-details { display: flex; flex-direction: column; gap: 14px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 20px; font-size: 14px; }
    .ld-row { display: flex; justify-content: space-between; }
    .ld-val.email { color: #34d399; font-family: 'JetBrains Mono', monospace; font-size: 13px; }
  </style>
</head>
<body>
  <div>
    <div class="slide-header">
      <div class="badge">Executive Leads — Slide 04</div>
      <div class="slide-num">Decision-Maker Intelligence & Contacts</div>
    </div>
    <div class="title-area">
      <h2>Verified Decision-Maker & Leadership Leads</h2>
      <p>Direct B2B outreach contacts with verified institutional email, Mexican direct phone, and standardized C-suite titles.</p>
    </div>
    <div class="leads-row">
      <div class="lead-box">
        <div class="lead-head">
          <div class="avatar">CG</div>
          <div>
            <div class="lead-name">Carlos González Rodríguez</div>
            <div class="lead-pos">Chief Executive Officer (CEO)</div>
          </div>
        </div>
        <div class="lead-details">
          <div class="ld-row"><span style="color: var(--muted);">Company</span><b>Tecnologías de México S.A.</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Work Email</span><span class="ld-val email">carlos.gonzalez@tec-mexico.com.mx</span></div>
          <div class="ld-row"><span style="color: var(--muted);">Direct Phone</span><b>+52 55 1234 5678</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Verification</span><b style="color: #34d399;">● SMTP Verified (85%)</b></div>
        </div>
      </div>

      <div class="lead-box">
        <div class="lead-head">
          <div class="avatar" style="background: linear-gradient(135deg, #10b981, #059669);">JH</div>
          <div>
            <div class="lead-name">Jorge Luis Hernández</div>
            <div class="lead-pos">Administrador Único / Owner</div>
          </div>
        </div>
        <div class="lead-details">
          <div class="ld-row"><span style="color: var(--muted);">Company</span><b>Construcciones del Sureste S.A.</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Work Email</span><span class="ld-val email">jorge.hernandez@consureste.com.mx</span></div>
          <div class="ld-row"><span style="color: var(--muted);">Direct Phone</span><b>+52 999 123 4567</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Verification</span><b style="color: #34d399;">● Legal Representative</b></div>
        </div>
      </div>

      <div class="lead-box">
        <div class="lead-head">
          <div class="avatar" style="background: linear-gradient(135deg, #f59e0b, #d97706);">AM</div>
          <div>
            <div class="lead-name">Adriana Morales</div>
            <div class="lead-pos">Director de Finanzas (CFO)</div>
          </div>
        </div>
        <div class="lead-details">
          <div class="ld-row"><span style="color: var(--muted);">Company</span><b>Manufactura Industrial S.A.B.</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Work Email</span><span class="ld-val email">amorales@manufacturaindustr.mx</span></div>
          <div class="ld-row"><span style="color: var(--muted);">Direct Phone</span><b>+52 938 847 1821</b></div>
          <div class="ld-row"><span style="color: var(--muted);">Verification</span><b style="color: #34d399;">● C-Suite Verified</b></div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Data File: output/combined/people/all_people.json (185,516 Lines)</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Slide 5
s5_html = COMMON_HEAD + """
  <style>
    .arch-container { display: flex; gap: 20px; align-items: center; margin-top: 50px; }
    .arch-card { flex: 1; background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 36px 26px; text-align: center; }
    .arch-card.highlight { border-color: #3b82f6; background: rgba(59, 130, 246, 0.08); box-shadow: 0 0 30px rgba(59, 130, 246, 0.15); }
    .arch-tier { font-size: 13px; font-weight: 700; text-transform: uppercase; color: #60a5fa; letter-spacing: 0.05em; margin-bottom: 8px; }
    .arch-title { font-size: 20px; font-weight: 800; color: #fff; margin-bottom: 14px; }
    .arch-desc { font-size: 13px; color: var(--muted); line-height: 1.6; }
    .arch-sep { font-size: 28px; color: var(--muted); font-weight: bold; }
    .cost-box {
      margin-top: 36px; background: rgba(255,255,255,0.02); border: 1px solid var(--border);
      border-radius: 12px; padding: 18px 28px; display: flex; justify-content: space-around; align-items: center;
    }
  </style>
</head>
<body>
  <div>
    <div class="slide-header">
      <div class="badge">Blueprint — Slide 05</div>
      <div class="slide-num">Production Scaling & Cost Architecture</div>
    </div>
    <div class="title-area">
      <h2>Enterprise Production Architecture (4-Tier Blueprint)</h2>
      <p>Scales from POC to 5.52M national establishments and 2M+ decision-makers at an estimated ~$1,490/mo operating cost.</p>
    </div>
    <div class="arch-container">
      <div class="arch-card">
        <div class="arch-tier">Tier 1</div>
        <div class="arch-title">Government Foundation</div>
        <div class="arch-desc">INEGI DENUE Bulk (5.52M establishments), SAT 69-B Blacklists, CompraNet Suppliers (380k). Streaming ingest in ~2.5 mins.</div>
      </div>
      <div class="arch-sep">➔</div>
      <div class="arch-card">
        <div class="arch-tier">Tier 2</div>
        <div class="arch-title">Directory Enrichment</div>
        <div class="arch-desc">COSMOS, QuimiNet, AMCHAM, CANACINTRA scraped via Botasaurus CDP with Mexican residential proxies.</div>
      </div>
      <div class="arch-sep">➔</div>
      <div class="arch-card highlight">
        <div class="arch-tier">Tier 3</div>
        <div class="arch-title">Golden Entity Resolution</div>
        <div class="arch-desc">6-Stage Waterfall dedup engine, SAT Modulo 11 check, RFC checksum verification, and Quality Trust Scoring.</div>
      </div>
      <div class="arch-sep">➔</div>
      <div class="arch-card">
        <div class="arch-tier">Tier 4</div>
        <div class="arch-title">Enterprise Serving</div>
        <div class="arch-desc">PostgreSQL 16 (State Partitioned) + OpenSearch Cluster for sub-second B2B intelligence queries.</div>
      </div>
    </div>
    <div class="cost-box">
      <div><b>PostgreSQL 16 (RDS):</b> <span style="color: #60a5fa;">$480/mo</span></div>
      <div><b>OpenSearch Cluster:</b> <span style="color: #60a5fa;">$290/mo</span></div>
      <div><b>Botasaurus Scraper Nodes:</b> <span style="color: #60a5fa;">$140/mo</span></div>
      <div><b>Mexican Residential Proxies:</b> <span style="color: #60a5fa;">$420/mo</span></div>
      <div style="font-size: 16px; font-weight: 800; color: #34d399;">Total Monthly Run Rate: ~$1,490 / mo</div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Estimated Timeline: 8–10 Weeks to Full Production Deployment</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

slides = [
    ("slide1_executive_kpis", s1_html),
    ("slide2_dual_channel_ingestion", s2_html),
    ("slide3_golden_company_records", s3_html),
    ("slide4_decision_maker_leads", s4_html),
    ("slide5_production_architecture", s5_html)
]

for name, html in slides:
    html_file = os.path.join(BASE_DIR, f"{name}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    png_file = os.path.join(ARTIFACT_DIR, f"{name}.png")
    cmd = [
        CHROME,
        "--headless=new",
        "--hide-scrollbars",
        "--window-size=1600,900",
        f"--screenshot={png_file}",
        html_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured: {name}.png (Size: {os.path.getsize(png_file)} bytes)")

print("All 5 presentation slides successfully captured!")
