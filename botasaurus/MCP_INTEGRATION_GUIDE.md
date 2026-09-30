# OneExtraction MCP Integration Guide

**Complete setup guide for integrating the MCP server with Kiro IDE, Claude Desktop, and other AI agents.**

---

## Quick Start (3 Steps)

### Step 1: Verify MCP Server Works
```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python test_mcp_server.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED - MCP Server is working correctly!
```

### Step 2: Choose Your Integration

| Platform | Setup Time | Difficulty |
|----------|-----------|-----------|
| **Kiro IDE** | 2 min | ⭐ Easiest |
| **Claude Desktop** | 5 min | ⭐⭐ Easy |
| **Standalone** | 1 min | ⭐ Easiest |

### Step 3: Start Using

Once configured, you can ask your AI agent:
- "Find all tech companies in California"
- "Get details for NVIDIA including executives"
- "Verify nvidia.com is owned by NVIDIA"

---

## Integration Methods

## Method 1: Kiro IDE (Recommended)

### Why Choose Kiro?
- ✅ Automatic MCP discovery
- ✅ Single configuration file
- ✅ Real-time tool integration
- ✅ No manual copying needed

### Setup Instructions

**File Location**: `.kiro/settings/mcp.json`

This file should already exist in your project. If not, create it:

**Windows Path:**
```
d:\Data Scraping Project POC\OneExtraction\.kiro\settings\mcp.json
```

**Content** (already configured):
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": [
        "-m",
        "src.us_b2b.mcp_server"
      ],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
      "env": {
        "PYTHONPATH": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
        "PYTHONIOENCODING": "utf-8"
      },
      "disabled": false
    }
  }
}
```

### Verification

1. Restart Kiro IDE
2. Look for connection indicator in the status bar
3. 🟢 Green = Connected and ready
4. 🔴 Red = Connection failed
5. Use MCP tools directly in chat

### Troubleshooting Kiro

**Tools not appearing?**
- Check `.kiro/settings/mcp.json` exists
- Verify paths use `\\` (escaped backslashes)
- Restart Kiro completely

**Connection failed?**
- Test manually: `python -m src.us_b2b.mcp_server --test`
- Check Python path: `python --version`
- Verify database files exist: `ls output/us/api/companies/`

---

## Method 2: Claude Desktop

### Why Choose Claude Desktop?
- ✅ Use MCP in Claude's web interface
- ✅ Persistent configuration
- ✅ Available on multiple devices
- ⚠️ Requires manual config file editing

### Setup Instructions

#### Step 1: Locate Config Directory

**Windows:**
```powershell
# Open File Explorer to:
%APPDATA%\Claude\

# Or via PowerShell:
explorer $env:APPDATA\Claude
```

**macOS:**
```bash
~/Library/Application\ Support/Claude/
```

**Linux:**
```bash
~/.config/Claude/
```

#### Step 2: Create or Edit `claude_desktop_config.json`

**Windows Example:**
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": [
        "-m",
        "src.us_b2b.mcp_server_stdio"
      ],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
      "env": {
        "PYTHONPATH": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

**macOS/Linux Example:**
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": [
        "-m",
        "src.us_b2b.mcp_server_stdio"
      ],
      "cwd": "/path/to/OneExtraction/botasaurus",
      "env": {
        "PYTHONPATH": "/path/to/OneExtraction/botasaurus"
      }
    }
  }
}
```

#### Step 3: Restart Claude Desktop

1. Close Claude Desktop completely
2. Wait 5 seconds
3. Reopen Claude Desktop
4. Check connection indicator (should be 🟢 green)

#### Step 4: Start Chatting

```
You: "Find all semiconductor companies in California"

Claude (with MCP):
✅ Calls search_companies(industry="semiconductors", state="CA")
Returns: [NVIDIA, Intel, Broadcom, ...]

You: "Get the CEO of NVIDIA"

Claude (with MCP):
✅ Calls search_companies(query="NVIDIA")
✅ Calls get_csuite_executives(company_id=...)
Returns: Jensen Huang, Chief Executive Officer
```

### Troubleshooting Claude Desktop

**MCP Not Connecting?**

1. Verify config file syntax (use https://jsonlint.com/)
2. Restart Claude Desktop completely
3. Check logs: `%APPDATA%\Claude\logs\`
4. Test Python: `python -m src.us_b2b.mcp_server --test`

**Tools Not Appearing?**

1. Restart Claude Desktop
2. Wait 30 seconds for reconnection
3. Check MCP connection icon in settings
4. Try a simple query: "List available tools"

**Connection Indicator Issue?**

Look for MCP connection indicator:
- Click settings gear icon in Claude
- Look for "Connected Models" or "Extensions"
- Should show "oneextraction-b2b" as 🟢 Connected

---

## Method 3: Standalone (Testing)

### Why Choose Standalone?
- ✅ Quick testing without IDE setup
- ✅ No configuration needed
- ✅ Perfect for debugging
- ❌ Not persistent for regular use

### Running the Server

#### CLI Test Mode (Quick Demo)
```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python -m src.us_b2b.mcp_server --test
```

**Output:**
```
=== OneExtraction US B2B MCP Server Interface ===
Loaded Database Records: 1,185 Companies, 2,370 Executives

[Tool Test: search_companies_tool(limit=2)]
[
  {
    "company_id": "us_9eef2ff7-82cf-51d3-8407-b43677edfcdf",
    "legal_name": "NIAGARA UNIVERSITY",
    ...
  }
]
```

#### Stdio Mode (For MCP Protocol)
```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python -m src.us_b2b.mcp_server_stdio
```

This runs the server waiting for MCP requests via stdin/stdout.

#### Run Tests
```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python test_mcp_server.py
```

**Output:**
```
✅ MCP Stdio Server imported successfully
✅ MCP Server initialized with 5 tools:
   - search_companies
   - get_company_details
   - get_csuite_executives
   - enrich_domain_rdap
   - enrich_wikipedia_summary

[TEST 1] Initialize Request
✅ Initialize test passed: OneExtraction B2B MCP Server

[TEST 2] Tools/List Request
✅ Tools/list test passed: 5 tools available

...

✅ ALL TESTS PASSED - MCP Server is working correctly!
```

---

## Available MCP Tools

Once integrated, you have access to 5 tools:

### 1. search_companies
**Search for companies by name, industry, state**

**Inputs:**
- `query` (string): Company name or partial name
- `industry` (string): Industry filter (e.g., "software", "healthcare")
- `state` (string): US state code (e.g., "CA", "NY")
- `limit` (integer): Max results (default 10)

**Example:**
```
Claude: "Find tech companies in California"
→ search_companies(industry="tech", state="CA", limit=20)
```

**Returns:**
```json
[
  {
    "company_id": "us_edgar_0001045810",
    "legal_name": "NVIDIA CORP",
    "industry": "Semiconductors",
    "ein": "94-1404272",
    "website": "https://www.nvidia.com"
  }
]
```

---

### 2. get_company_details
**Get complete company profile with executives**

**Inputs:**
- `company_id` (string): Company ID, EIN, or CIK number

**Example:**
```
Claude: "Get full details for NVIDIA"
→ get_company_details("us_edgar_0001045810")
```

**Returns:**
```json
{
  "company_id": "us_edgar_0001045810",
  "legal_name": "NVIDIA CORPORATION",
  "ein": "94-1404272",
  "website": "https://www.nvidia.com",
  "phone": "1-408-486-2000",
  "industry": "Semiconductors",
  "executives": [
    {
      "full_name": "Jensen Huang",
      "title": "Chief Executive Officer (CEO)",
      "department": "EXECUTIVE"
    },
    {
      "full_name": "Colette Kress",
      "title": "Chief Financial Officer (CFO)",
      "department": "FINANCE"
    }
  ]
}
```

---

### 3. get_csuite_executives
**Get C-suite executives for a company**

**Inputs:**
- `company_id` (string): Company ID

**Example:**
```
Claude: "Who are the executives at NVIDIA?"
→ get_csuite_executives("us_edgar_0001045810")
```

**Returns:**
```json
[
  {
    "full_name": "Jensen Huang",
    "title": "Chief Executive Officer (CEO)",
    "seniority_level": "C_SUITE",
    "department": "EXECUTIVE",
    "is_active": true
  },
  {
    "full_name": "Colette Kress",
    "title": "Chief Financial Officer (CFO)",
    "seniority_level": "C_SUITE",
    "department": "FINANCE",
    "is_active": true
  }
]
```

---

### 4. enrich_domain_rdap
**Live WHOIS domain ownership verification**

**Inputs:**
- `domain` (string): Domain name (e.g., "nvidia.com")

**Example:**
```
Claude: "Verify nvidia.com domain ownership"
→ enrich_domain_rdap("nvidia.com")
```

**Returns:**
```json
{
  "domain": "nvidia.com",
  "registrar": "MarkMonitor Inc.",
  "registrar_email": "abusecomplaints@markmonitor.com",
  "registrar_phone": "+1.2083895740",
  "created_date": "1995-05-22T00:00:00Z",
  "nameservers": [
    "ns1.nvidia.com",
    "ns2.nvidia.com"
  ],
  "tech_contact_name": "Domain Administrator",
  "tech_contact_email": "domain-admin@nvidia.com",
  "status": "clientUpdateProhibited"
}
```

---

### 5. enrich_wikipedia_summary
**Fetch corporate history from Wikipedia**

**Inputs:**
- `company_name` (string): Company name (e.g., "NVIDIA")

**Example:**
```
Claude: "Tell me about NVIDIA's history"
→ enrich_wikipedia_summary("NVIDIA")
```

**Returns:**
```json
{
  "title": "Nvidia",
  "summary": "Nvidia Corporation is an American technology company...",
  "description": "American technology company",
  "url": "https://en.wikipedia.org/wiki/Nvidia"
}
```

---

## Example Use Cases

### Use Case 1: Sales Intelligence
```
User: "Find 10 tech CEOs in California with public info"

Claude (with MCP):
1. search_companies(industry="tech", state="CA", limit=10)
2. get_csuite_executives(company_id=each_result)
3. enrich_domain_rdap(domain=each_company_domain)

Result: 10 verified tech CEOs with domain info
```

### Use Case 2: Company Research
```
User: "Give me a complete profile of Microsoft including history"

Claude (with MCP):
1. search_companies(query="Microsoft", limit=1)
2. get_company_details(company_id=result)
3. enrich_wikipedia_summary(company_name="Microsoft")

Result: Full company profile + Wikipedia history
```

### Use Case 3: Executive Verification
```
User: "Verify Satya Nadella is CEO of Microsoft"

Claude (with MCP):
1. search_companies(query="Microsoft", limit=1)
2. get_csuite_executives(company_id=result)
3. Check if "Satya Nadella" in results with "CEO" title

Result: ✅ Verified
```

### Use Case 4: Lead Qualification
```
User: "Is nvidia.com owned by NVIDIA Corporation?"

Claude (with MCP):
1. enrich_domain_rdap(domain="nvidia.com")
2. Check registrant name matches "NVIDIA"

Result: ✅ Domain verified
```

---

## Configuration Files Summary

### File: `.kiro/settings/mcp.json` (Kiro IDE)
- **Location**: `d:\Data Scraping Project POC\OneExtraction\.kiro\settings\mcp.json`
- **Purpose**: Kiro IDE MCP server configuration
- **Status**: ✅ Already created
- **Requires Restart**: Yes (restart Kiro)

### File: `claude_desktop_config.json` (Claude Desktop)
- **Location**: `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- **Purpose**: Claude Desktop MCP server configuration
- **Template**: `claude_desktop_config.json` in project root
- **Status**: ⚠️ Template created, needs manual copy
- **Requires Restart**: Yes (restart Claude)

### File: `mcp_server.py` (Original)
- **Location**: `src/us_b2b/mcp_server.py`
- **Purpose**: MCP server entry point with CLI test mode
- **Status**: ✅ Updated to support --test and --stdio
- **Commands**: `python -m src.us_b2b.mcp_server --test`

### File: `mcp_server_stdio.py` (Stdio Implementation)
- **Location**: `src/us_b2b/mcp_server_stdio.py`
- **Purpose**: Full MCP protocol implementation
- **Status**: ✅ Created and tested
- **Commands**: `python -m src.us_b2b.mcp_server_stdio`

### File: `test_mcp_server.py` (Testing)
- **Location**: `botasaurus/test_mcp_server.py`
- **Purpose**: Verify MCP server functionality
- **Status**: ✅ Created and passing
- **Commands**: `python test_mcp_server.py`

---

## Verification Checklist

- [ ] Ran `python test_mcp_server.py` - All tests pass ✅
- [ ] Verified database files exist: `output/us/api/companies/us_companies.json`
- [ ] Verified database files exist: `output/us/api/people/us_people.json`
- [ ] For Kiro: Checked `.kiro/settings/mcp.json` exists
- [ ] For Claude: Created `claude_desktop_config.json` in Claude config directory
- [ ] For Kiro: Restarted Kiro IDE
- [ ] For Claude: Restarted Claude Desktop
- [ ] Tested tool in IDE/App: Asked for company search
- [ ] Verified connection indicator shows 🟢 green

---

## Troubleshooting Guide

### Error: "Module not found"
```
ModuleNotFoundError: No module named 'src.us_b2b'
```

**Solution:**
```bash
# Make sure you're in the botasaurus directory
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"

# Verify Python path
echo $env:PYTHONPATH  # Should show botasaurus path

# Test import
python -c "from src.us_b2b.mcp_server import search_companies_tool; print('✅ OK')"
```

---

### Error: "Database not loaded"
```
Loaded Database Records: 0 Companies, 0 Executives
```

**Solution:**
```bash
# Check if files exist
ls output/us/api/companies/us_companies.json
ls output/us/api/people/us_people.json

# If missing, run ingestion
python scripts/us_bulk_ingest.py
```

---

### Error: "Tool not found"
```
Error: Tool 'search_companies' not found
```

**Solution:**
1. Restart the MCP server
2. Verify tool name spelling
3. Run test: `python test_mcp_server.py`
4. Check server logs

---

### Error: "Connection timeout"
```
Claude: [Error connecting to MCP server]
```

**Solution:**
1. Test directly: `python -m src.us_b2b.mcp_server --test`
2. Verify config file path
3. Check Python is in system PATH: `python --version`
4. Verify PYTHONPATH environment variable

---

### Error: "Invalid JSON config"
```
ParseError: Invalid JSON in claude_desktop_config.json
```

**Solution:**
1. Validate JSON: https://jsonlint.com/
2. Check for unescaped backslashes (should be `\\`)
3. Ensure all quotes are double quotes (`"`)
4. Copy from provided template and modify paths only

---

## Support & Next Steps

### What Works Now ✅
- 5 MCP tools fully functional
- Database loaded with 1,185 companies + 2,370 executives
- All tests passing
- Ready for Kiro IDE integration
- Ready for Claude Desktop integration

### What You Can Do Next
1. **For Kiro IDE**: Restart Kiro and start asking questions
2. **For Claude Desktop**: Copy config and restart Claude
3. **Test Tools**: Run provided test suite
4. **Customize**: Add more tools or data sources

### Questions?
- Check logs: `stderr` for debugging info
- Test directly: `python test_mcp_server.py`
- Review example queries in "Use Cases" section
- Inspect MCP protocol specs at: https://spec.modelcontextprotocol.io/

---

## File Structure

```
OneExtraction/botasaurus/
├── .kiro/
│   └── settings/
│       └── mcp.json                    ✅ Kiro config
├── src/us_b2b/
│   ├── mcp_server.py                   ✅ Main entry point
│   ├── mcp_server_stdio.py             ✅ Stdio implementation
│   └── connectors/
│       ├── rdap_client.py
│       └── wikipedia_client.py
├── CLAUDE_DESKTOP_CONFIG.md            📖 Setup guide
├── claude_desktop_config.json          📋 Claude config template
├── MCP_INTEGRATION_GUIDE.md            📖 This file
├── test_mcp_server.py                  ✅ Test script
└── output/us/api/
    ├── companies/
    │   └── us_companies.json           📊 Database
    └── people/
        └── us_people.json              📊 Database
```

---

*Last Updated: September 22, 2026*  
*Status: ✅ All systems operational*  
*Tests Passing: 5/5*