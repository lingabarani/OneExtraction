# MCP Quick Start (30 Seconds)

## Step 1: Verify It Works
```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"
python test_mcp_server.py
```

**Expected**: ✅ `ALL TESTS PASSED`

---

## Step 2: Choose Integration

### Option A: Kiro IDE (Just Restart) ⭐
1. Restart Kiro IDE
2. Done! MCP ready to use
3. Ask questions in chat

### Option B: Claude Desktop (5 min)
1. Open: `%APPDATA%\Claude\`
2. Create `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "oneextraction-b2b": {
      "command": "python",
      "args": ["-m", "src.us_b2b.mcp_server_stdio"],
      "cwd": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus",
      "env": {"PYTHONPATH": "d:\\Data Scraping Project POC\\OneExtraction\\botasaurus"}
    }
  }
}
```
3. Restart Claude Desktop
4. Done!

### Option C: Test Only
```bash
python -m src.us_b2b.mcp_server --test
```

---

## Step 3: Start Using

Once integrated, ask your AI:

```
"Find tech companies in California"
"Get NVIDIA executives"
"Verify nvidia.com ownership"
"Tell me about Microsoft"
```

AI automatically uses MCP tools to answer with real data from your database!

---

## Database Status
✅ 1,185 Companies  
✅ 2,370 Executives  
✅ 100% Real Data  

---

## Need Help?
- **Full Guide**: Read `MCP_INTEGRATION_GUIDE.md`
- **Issues**: Run `python test_mcp_server.py` to debug
- **Config Help**: See `CLAUDE_DESKTOP_CONFIG.md`

---

## What You Get (5 Tools)

| Tool | Does |
|------|------|
| search_companies | Find companies |
| get_company_details | Full company profile |
| get_csuite_executives | Get execs |
| enrich_domain_rdap | Domain verification |
| enrich_wikipedia_summary | Company history |

---

**Status**: ✅ Ready to Use  
**Tests**: 5/5 Passing  
**Setup Time**: < 5 minutes  

---

That's it! You're done. 🎉
