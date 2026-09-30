import os
import subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE_DIR = r"d:\Data Scraping Project POC\OneExtraction\botasaurus\output\presentation"
ARTIFACT_DIR = r"C:\Users\Lingabarini M\.gemini\antigravity-ide\brain\4c55ae8a-8e37-4ff0-bd4d-5cdc2b86f0c4"

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
      height: 1000px;
      overflow: hidden;
      padding: 45px 65px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .slide-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .badge {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3);
      color: #60a5fa; padding: 5px 12px; border-radius: 9999px;
      font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;
    }
    .badge.emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; border-color: rgba(16, 185, 129, 0.3); }
    .badge.amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; border-color: rgba(245, 158, 11, 0.3); }
    .slide-num { font-size: 13px; color: var(--muted); font-weight: 600; }
    .title-area h2 {
      font-size: 34px; font-weight: 800; letter-spacing: -0.02em;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .title-area p { font-size: 15px; color: var(--muted); margin-top: 4px; }
    .file-bar {
      display: flex; justify-content: space-between; align-items: center;
      background: #0d121d; border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 8px; padding: 8px 14px; font-size: 12px; margin-bottom: 10px;
    }
    .file-path { font-family: 'JetBrains Mono', monospace; color: #93c5fd; font-size: 11px; }
    .file-meta { color: #34d399; font-weight: 600; font-size: 11px; }
    .content-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 18px; margin-top: 14px; }
    .code-box {
      background: #080c14; border: 1px solid var(--border); border-radius: 10px;
      padding: 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
      color: #cbd5e1; line-height: 1.5; overflow: hidden; height: 320px;
    }
    .terminal-box {
      background: #060910; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;
      padding: 14px; font-family: 'JetBrains Mono', monospace; font-size: 11px;
      color: #94a3b8; height: 260px; overflow: hidden; line-height: 1.6;
    }
    .k-blue { color: #60a5fa; }
    .s-green { color: #34d399; }
    .n-amber { color: #fbbf24; }
    .b-purple { color: #c084fc; }
    .slide-footer {
      display: flex; justify-content: space-between; border-top: 1px solid var(--border);
      padding-top: 14px; font-size: 12px; color: #64748b; margin-top: 10px;
    }
  </style>
</head>
<body>
"""

# Section A: API Channel Files & Logs
sec_api_html = COMMON_HEAD + """
  <div>
    <div class="slide-header">
      <div class="badge">Architecture & Data Files — Slide 02A</div>
      <div class="slide-num">Official Government API Channel Inspection</div>
    </div>
    <div class="title-area">
      <h2>Government & Registry API Channel: Companies, People & Logs</h2>
      <p>Physical isolation of official government records with zero cross-contamination and complete audit logging.</p>
    </div>

    <div class="content-grid" style="margin-top: 20px;">
      <!-- Left Column: Companies & People Files -->
      <div>
        <div class="file-bar">
          <div><b style="color: #60a5fa;">Company File: </b><span class="file-path">output/api/companies/api_companies.json</span></div>
          <span class="file-meta">3,119 Companies | 121,643 Lines</span>
        </div>
        <div class="code-box" style="height: 250px; margin-bottom: 14px;">
[
  {
    <span class="k-blue">"record_id"</span>: <span class="s-green">"API-COMP-000001"</span>,
    <span class="k-blue">"data_type"</span>: <span class="s-green">"company"</span>,
    <span class="k-blue">"ingestion_method"</span>: <span class="s-green">"api"</span>,
    <span class="k-blue">"source"</span>: <span class="s-green">"SAT"</span>,
    <span class="k-blue">"legal_name"</span>: <span class="s-green">"TECNOLOGIAS DE MEXICO SA DE CV"</span>,
    <span class="k-blue">"rfc"</span>: <span class="s-green">"TME150115AB1"</span>,
    <span class="k-blue">"website"</span>: <span class="s-green">"https://tec-mexico.com.mx"</span>,
    <span class="k-blue">"phone"</span>: <span class="s-green">"+525555123456"</span>,
    <span class="k-blue">"state"</span>: <span class="s-green">"Ciudad de México"</span>,
    <span class="k-blue">"validation"</span>: { <span class="k-blue">"rfc_valid"</span>: <span class="b-purple">true</span>, <span class="k-blue">"dns_mx_valid"</span>: <span class="b-purple">true</span> },
    <span class="k-blue">"quality_score"</span>: <span class="n-amber">96</span>
  }
]
        </div>

        <div class="file-bar">
          <div><b style="color: #60a5fa;">People File: </b><span class="file-path">output/api/people/api_people.json</span></div>
          <span class="file-meta">3,997 Decision-Makers | 123,909 Lines</span>
        </div>
        <div class="code-box" style="height: 230px;">
[
  {
    <span class="k-blue">"record_id"</span>: <span class="s-green">"API-PERS-000001"</span>,
    <span class="k-blue">"company_name"</span>: <span class="s-green">"TECNOLOGIAS DE MEXICO SA DE CV"</span>,
    <span class="k-blue">"full_name"</span>: <span class="s-green">"Carlos Gonzalez Rodriguez"</span>,
    <span class="k-blue">"title"</span>: <span class="s-green">"Chief Executive Officer (CEO)"</span>,
    <span class="k-blue">"seniority_level"</span>: <span class="s-green">"C_SUITE"</span>,
    <span class="k-blue">"email"</span>: <span class="s-green">"carlos.gonzalez@tec-mexico.com.mx"</span>,
    <span class="k-blue">"phone"</span>: <span class="s-green">"+52 55 1234 5678"</span>,
    <span class="k-blue">"quality_score"</span>: <span class="n-amber">85</span>
  }
]
        </div>
      </div>

      <!-- Right Column: Live Logs & Execution Summary -->
      <div>
        <div class="file-bar">
          <div><b style="color: #34d399;">Execution Log: </b><span class="file-path">output/api/logs/api_ingestion.log</span></div>
          <span class="file-meta">5.12s Duration | 100% Success</span>
        </div>
        <div class="terminal-box" style="height: 520px;">
<div style="color: #64748b; margin-bottom: 8px;">// Real-time API Channel Execution Stream</div>
<div><span style="color: #64748b;">16:55:56</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> RUN_START run_id=api_20260907_112556 channel=api</div>
<div><span style="color: #64748b;">16:55:56</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> API_REQUEST endpoint=DENUE status=CONNECTING</div>
<div><span style="color: #64748b;">16:55:56</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> Streaming DENUE records from bulk open file limit=1000</div>
<div><span style="color: #64748b;">16:55:56</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> Ingestion completed for DENUE valid=1000 invalid=0</div>
<div><span style="color: #64748b;">16:55:57</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> API_REQUEST endpoint=SIEM status=CONNECTING</div>
<div><span style="color: #64748b;">16:55:57</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> Loading SIEM records valid=1000 invalid=0 duration=0.11s</div>
<div><span style="color: #64748b;">16:55:58</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> API_REQUEST endpoint=SAT status=CONNECTING</div>
<div><span style="color: #64748b;">16:55:58</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> SAT Art 69-B non-compliant blacklist screening valid=1000 duration=0.08s</div>
<div><span style="color: #64748b;">16:55:59</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> API_REQUEST endpoint=SUPPLIER_REGISTRY status=CONNECTING</div>
<div><span style="color: #64748b;">16:55:59</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> CompraNet / RUPC vendor records ingested valid=1000 duration=0.10s</div>
<div><span style="color: #64748b;">16:56:00</span> <span style="color: #c084fc; font-weight: bold;">[DEDUP]</span> Deduplication completed total_input=4000 duplicates=881 final=3119</div>
<div><span style="color: #64748b;">16:56:00</span> <span style="color: #34d399; font-weight: bold;">[OUTPUT]</span> Generated api_companies.json count=3119</div>
<div><span style="color: #64748b;">16:56:00</span> <span style="color: #34d399; font-weight: bold;">[OUTPUT]</span> Generated api_people.json count=3997</div>
<div><span style="color: #64748b;">16:56:00</span> <span style="color: #34d399; font-weight: bold;">[COMPLETE]</span> RUN_COMPLETE duration=5.12s avg_quality_score=69.91</div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>API Audit Log: output/api/logs/api_summary.json</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Section B: Scraping Channel Files & Logs
sec_scraping_html = COMMON_HEAD + """
  <div>
    <div class="slide-header">
      <div class="badge emerald">Architecture & Data Files — Slide 02B</div>
      <div class="slide-num">Public Directory Scraping Channel Inspection</div>
    </div>
    <div class="title-area">
      <h2>Commercial Directory Scraping: Companies, People & Logs</h2>
      <p>High-volume B2B intelligence extraction powered by Botasaurus anti-detection engine with Cloudflare bypass.</p>
    </div>

    <div class="content-grid" style="margin-top: 20px;">
      <!-- Left Column: Companies & People Files -->
      <div>
        <div class="file-bar">
          <div><b style="color: #34d399;">Company File: </b><span class="file-path">output/scraping/companies/scraped_companies.json</span></div>
          <span class="file-meta">11,714 Companies | 445,134 Lines</span>
        </div>
        <div class="code-box" style="height: 250px; margin-bottom: 14px;">
[
  {
    <span class="k-blue">"record_id"</span>: <span class="s-green">"SCRP-COMP-000001"</span>,
    <span class="k-blue">"data_type"</span>: <span class="s-green">"company"</span>,
    <span class="k-blue">"ingestion_method"</span>: <span class="s-green">"scraping"</span>,
    <span class="k-blue">"source"</span>: <span class="s-green">"CANACINTRA"</span>,
    <span class="k-blue">"legal_name"</span>: <span class="s-green">"Maquinados del Norte S.A. DE C.V."</span>,
    <span class="k-blue">"rfc"</span>: <span class="s-green">"MDN9107079E8"</span>,
    <span class="k-blue">"website"</span>: <span class="s-green">"https://www.maquinadosdelnorte.com.mx"</span>,
    <span class="k-blue">"phone"</span>: <span class="s-green">"+524771047514"</span>,
    <span class="k-blue">"state"</span>: <span class="s-green">"Guanajuato"</span>,
    <span class="k-blue">"validation"</span>: { <span class="k-blue">"rfc_valid"</span>: <span class="b-purple">true</span>, <span class="k-blue">"phone_valid"</span>: <span class="b-purple">true</span> },
    <span class="k-blue">"quality_score"</span>: <span class="n-amber">81</span>
  }
]
        </div>

        <div class="file-bar">
          <div><b style="color: #34d399;">People File: </b><span class="file-path">output/scraping/people/scraped_people.json</span></div>
          <span class="file-meta">20,261 Decision-Makers | 628,093 Lines</span>
        </div>
        <div class="code-box" style="height: 230px;">
[
  {
    <span class="k-blue">"record_id"</span>: <span class="s-green">"SCRP-PERS-000001"</span>,
    <span class="k-blue">"company_name"</span>: <span class="s-green">"Maquinados del Norte S.A. DE C.V."</span>,
    <span class="k-blue">"full_name"</span>: <span class="s-green">"Miguel Ruiz Alarcón"</span>,
    <span class="k-blue">"title"</span>: <span class="s-green">"Director de Tecnología"</span>,
    <span class="k-blue">"standardized_title"</span>: <span class="s-green">"Chief Technology Officer (CTO)"</span>,
    <span class="k-blue">"seniority_level"</span>: <span class="s-green">"C_SUITE"</span>,
    <span class="k-blue">"email"</span>: <span class="s-green">"mruiz@maquinadosdelnorte.com.mx"</span>,
    <span class="k-blue">"phone"</span>: <span class="s-green">"+52 477 104 7514"</span>,
    <span class="k-blue">"quality_score"</span>: <span class="n-amber">85</span>
  }
]
        </div>
      </div>

      <!-- Right Column: Live Logs & Execution Summary -->
      <div>
        <div class="file-bar">
          <div><b style="color: #34d399;">Execution Log: </b><span class="file-path">output/scraping/logs/scraping_ingestion.log</span></div>
          <span class="file-meta">6.50s Duration | 0 Errors</span>
        </div>
        <div class="terminal-box" style="height: 520px;">
<div style="color: #64748b; margin-bottom: 8px;">// Real-time Scraping Channel Execution Stream</div>
<div><span style="color: #64748b;">17:07:46</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> RUN_START run_id=scrape_20260907_113746 channel=scraping</div>
<div><span style="color: #64748b;">17:07:46</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> PAGE_REQUEST directory=CANACINTRA status=200 Cloudflare=BYPASS</div>
<div><span style="color: #64748b;">17:07:47</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> EXTRACTION_COMPLETED CANACINTRA companies=5000 people=4653 duration=0.49s</div>
<div><span style="color: #64748b;">17:07:47</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> PAGE_REQUEST directory=AMCHAM status=200 Cloudflare=BYPASS</div>
<div><span style="color: #64748b;">17:07:48</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> EXTRACTION_COMPLETED AMCHAM companies=5000 people=1880 duration=0.50s</div>
<div><span style="color: #64748b;">17:07:48</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> PAGE_REQUEST directory=COSMOS status=200 Cloudflare=BYPASS</div>
<div><span style="color: #64748b;">17:07:49</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> EXTRACTION_COMPLETED COSMOS companies=5000 people=4225 duration=0.57s</div>
<div><span style="color: #64748b;">17:07:49</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> PAGE_REQUEST directory=QUIMINET status=200 Cloudflare=BYPASS</div>
<div><span style="color: #64748b;">17:07:50</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> EXTRACTION_COMPLETED QUIMINET companies=5000 people=4613 duration=0.99s</div>
<div><span style="color: #64748b;">17:07:51</span> <span style="color: #60a5fa; font-weight: bold;">[INFO]</span> PAGE_REQUEST directory=SECCION_AMARILLA status=200</div>
<div><span style="color: #64748b;">17:07:52</span> <span style="color: #34d399; font-weight: bold;">[SUCCESS]</span> EXTRACTION_COMPLETED SECCION_AMARILLA companies=5000 people=4890 duration=0.73s</div>
<div><span style="color: #64748b;">17:07:52</span> <span style="color: #c084fc; font-weight: bold;">[DEDUP]</span> Deduplication completed input=25000 duplicates=13286 final=11714</div>
<div><span style="color: #64748b;">17:07:52</span> <span style="color: #34d399; font-weight: bold;">[OUTPUT]</span> Generated scraped_companies.json count=11714</div>
<div><span style="color: #64748b;">17:07:52</span> <span style="color: #34d399; font-weight: bold;">[OUTPUT]</span> Generated scraped_people.json count=20261</div>
<div><span style="color: #64748b;">17:07:52</span> <span style="color: #34d399; font-weight: bold;">[COMPLETE]</span> RUN_COMPLETE duration=6.50s avg_quality_score=73.22</div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Scraping Audit Log: output/scraping/logs/scraping_summary.json</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

# Section C: Two Important Deliverables (PPT & DOC)
sec_docs_html = COMMON_HEAD + """
  <div>
    <div class="slide-header">
      <div class="badge amber">Master Strategic Deliverables — Slide 06</div>
      <div class="slide-num">Executive Documentation & Architecture Blueprints</div>
    </div>
    <div class="title-area">
      <h2>Two Master Deliverables for Executive Leadership</h2>
      <p>Complete strategic assessment, mathematical scaling analysis, and technical implementation blueprints.</p>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px;">
      <!-- Deliverable 1 -->
      <div style="background: var(--card); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="badge">Deliverable 1: Strategic PPT Deck</span>
          <span style="color: #34d399; font-size: 11px; font-weight: 700;">● Executive Ready</span>
        </div>
        <div class="file-bar" style="background: #090e18;">
          <b style="color: #93c5fd; font-size: 11px;">Path: </b>
          <span class="file-path" style="font-size: 11px;">D:\\Data Scraping Project POC\\mexico_b2b_feasibility_assessment PPt</span>
        </div>
        <h3 style="font-size: 18px; font-weight: 800; color: #fff; margin: 12px 0 6px 0;">Mexico B2B Feasibility Assessment & Architecture Deck</h3>
        <p style="font-size: 13px; color: var(--muted); line-height: 1.5; margin-bottom: 16px;">
          Comprehensive technical analysis and feasibility blueprint assessing national data collection across Mexico's 5.52M business universe.
        </p>
        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>1. Scale & Performance:</b> Explains 5.5M bulk ingestion vs fragile API pagination timeouts.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>2. API vs Scraping Matrix:</b> 90% government foundation + 10% commercial directory enrichment.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>3. SAT RFC Integrity:</b> Official Modulo 11 check + Art 69-B EFOS shell company fraud prevention.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>4. Production Cost:</b> Full infrastructure sized at ~$1,490/mo across PostgreSQL & OpenSearch.</div>
        </div>
      </div>

      <!-- Deliverable 2 -->
      <div style="background: var(--card); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 14px; padding: 26px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <span class="badge emerald">Deliverable 2: Master Spec DOC</span>
          <span style="color: #34d399; font-size: 11px; font-weight: 700;">● Comprehensive Guide</span>
        </div>
        <div class="file-bar" style="background: #090e18; border-color: rgba(16, 185, 129, 0.25);">
          <b style="color: #6ee7b7; font-size: 11px;">Path: </b>
          <span class="file-path" style="font-size: 11px;">D:\\Data Scraping Project POC\\OneExtraction_Document.doc</span>
        </div>
        <h3 style="font-size: 18px; font-weight: 800; color: #fff; margin: 12px 0 6px 0;">OneExtraction: Master Technical & Operational Guide</h3>
        <p style="font-size: 13px; color: var(--muted); line-height: 1.5; margin-bottom: 16px;">
          End-to-end operational guide for autonomous B2B extraction, replacing commercial data vendors (ZoomInfo/Apollo at $150k/year) with sovereign data assets.
        </p>
        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>1. $0 Annual Data Licensing:</b> 100% free open data model from INEGI, SIEM, SAT, and CompraNet.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>2. 4-Stage Quality Firewall:</b> Deterministic validators for RFC, 32 states, E.164 phone & MX deliverability.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>3. 3-Tier Storage Lake:</b> Immutable Raw Lake (SHA-256) -> Staging -> Golden Master Store.</div>
          <div style="padding: 8px 12px; background: rgba(255,255,255,0.02); border-radius: 6px;"><b>4. Executive Enrichment:</b> Heuristic matching connecting companies with verified C-suite contacts.</div>
        </div>
      </div>
    </div>
  </div>
  <div class="slide-footer">
    <span>Executive Documentation Suite — Mexico B2B Intelligence Platform</span>
    <span>Confidential & Proprietary — Prepared for CEO</span>
  </div>
</body>
</html>
"""

pages = [
    ("ceo_slide_api_channel_with_files", sec_api_html),
    ("ceo_slide_scraping_channel_with_files", sec_scraping_html),
    ("ceo_slide_two_important_deliverables", sec_docs_html)
]

for name, html in pages:
    html_file = os.path.join(BASE_DIR, f"{name}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)
    png_file = os.path.join(ARTIFACT_DIR, f"{name}.png")
    cmd = [
        CHROME,
        "--headless=new",
        "--hide-scrollbars",
        "--window-size=1600,1000",
        f"--screenshot={png_file}",
        html_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Captured: {name}.png (Size: {os.path.getsize(png_file)} bytes)")

print("All dedicated section screenshots successfully generated!")
