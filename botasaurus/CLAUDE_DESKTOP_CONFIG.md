# Claude Desktop MCP Configuration

This guide explains how to register the OneExtraction MCP server with Claude Desktop.

## Prerequisites

- Claude Desktop installed (https://claude.ai/download)
- Python 3.8+ installed
- OneExtraction project cloned

## Step 1: Find Your Claude Desktop Config Directory

### Windows
```
%APPDATA%\Claude\claude_desktop_config.json
```

Or open in PowerShell:
```powershell
$env:APPDATA + "\Claude\claude_desktop_config.json"
```

Full path example:
```
C:\Users\YourUsername\AppData\Roaming\Claude\claude_desktop_config.json
```

### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Linux
```
~/.config/Claude/claude_desktop_config.json
```

## Step 2: Edit or Create claude_desktop_config.json

If the file doesn't exist, create it. Add the following MCP server configuration:

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

### Important Notes:

- **Replace paths** with your actual OneExtraction installation path
- **Use forward slashes or escaped backslashes** in JSON paths
- **Keep the module name** as `src.us_b2b.mcp_server_stdio`
- **PYTHONPATH** must point to the botasaurus directory

### Example for Different OS:

**Windows (escaped backslashes)**:
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": ["-m", "src.us_b2b.mcp_server_stdio"],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
      "env": {
        "PYTHONPATH": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus"
      }
    }
  }
}
```

**macOS/Linux (forward slashes)**:
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": ["-m", "src.us_b2b.mcp_server_stdio"],
      "cwd": "/path/to/OneExtraction/botasaurus",
      "env": {
        "PYTHONPATH": "/path/to/OneExtraction/botasaurus"
      }
    }
  }
}
```

## Step 3: Restart Claude Desktop

1. Close Claude Desktop completely
2. Wait 5 seconds
3. Reopen Claude Desktop
4. The MCP server should now be connected

## Step 4: Verify MCP Connection

In Claude Desktop, look for the connection indicator:
- 🟢 **Green dot** = MCP server connected and ready
- 🔴 **Red dot** = MCP server connection failed
- ⚪ **Gray dot** = MCP server not configured

## Step 5: Start Using the Tools

Once connected, you can ask Claude:

### Example 1: Search Companies
```
"Find all tech companies in California with more than 5000 employees"
```

Claude will automatically call: `search_companies(industry="tech", state="CA", limit=20)`

### Example 2: Get Company Details
```
"Get complete details for NVIDIA including executives"
```

Claude will call:
1. `search_companies(query="NVIDIA", limit=1)`
2. `get_company_details(company_id=<result>)`

### Example 3: Verify Domain
```
"Verify that nvidia.com is owned by NVIDIA Corporation"
```

Claude will call: `enrich_domain_rdap(domain="nvidia.com")`

### Example 4: Company Research
```
"Research NVIDIA: Get their executives, domain info, and corporate history"
```

Claude will call multiple tools:
1. `get_company_details(company_id="...")`
2. `enrich_domain_rdap(domain="nvidia.com")`
3. `enrich_wikipedia_summary(company_name="NVIDIA")`

## Troubleshooting

### MCP Server Not Connecting

**Check 1: Python Path**
```powershell
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python -m src.us_b2b.mcp_server_stdio --test
```

Should show: `OneExtraction MCP Server started (stdio mode)`

**Check 2: Config Path**
Verify the config file exists at:
```powershell
$env:APPDATA + "\Claude\claude_desktop_config.json"
```

**Check 3: JSON Syntax**
Validate JSON at: https://jsonlint.com/

**Check 4: Python Installation**
```powershell
python --version
pip list | grep botasaurus
```

### Tools Not Appearing

1. Close Claude Desktop
2. Wait 10 seconds
3. Reopen Claude Desktop
4. Check connection indicator in settings

### Database Loading Error

**Error**: "Loaded Database Records: 0 Companies, 0 Executives"

**Solution**: Ensure output files exist:
```powershell
ls "d:\Data Scraping Project POC\OneExtraction\botasaurus\output\us\api\companies\us_companies.json"
ls "d:\Data Scraping Project POC\OneExtraction\botasaurus\output\us\api\people\us_people.json"
```

If missing, run data ingestion:
```bash
python scripts/us_bulk_ingest.py
```

## Available Tools in Claude

Once connected, Claude Desktop will have access to:

1. **search_companies** - Search by name, industry, state
2. **get_company_details** - Full company profile with executives
3. **get_csuite_executives** - C-suite contacts for a company
4. **enrich_domain_rdap** - Live WHOIS domain lookup
5. **enrich_wikipedia_summary** - Corporate history

## Advanced Configuration

### Add Multiple MCP Servers

You can register multiple servers in the same config:

```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": ["-m", "src.us_b2b.mcp_server_stdio"],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus"
    },
    "other-service": {
      "command": "node",
      "args": ["path/to/other/server.js"]
    }
  }
}
```

### Disable Server Temporarily

Add `"disabled": true` to temporarily turn off the server:

```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": ["-m", "src.us_b2b.mcp_server_stdio"],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
      "disabled": false
    }
  }
}
```

## Complete Example Config File

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

## Next Steps

- [ ] Copy the config to Claude Desktop
- [ ] Restart Claude Desktop
- [ ] Verify green connection indicator
- [ ] Try a test query with Claude
- [ ] Explore the tools in conversations

## Need Help?

1. Check logs: Claude Desktop logs are in `%APPDATA%\Claude\logs\`
2. Test directly: `python -m src.us_b2b.mcp_server_stdio --test`
3. Verify Python: `python --version` (should be 3.8+)
4. Check dependencies: `pip list` (verify botasaurus, requests installed)

---

*Last Updated: September 22, 2026*
