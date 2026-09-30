# 🧪 API Key Testing & Validation Commands

Quick reference guide to test each API key individually.

## Overview

| API | Test Command | Expected Result | Status |
|-----|-------|---------|--------|
| **Census** | `curl {url}` | 200 OK | ✅ Working |
| **BLS** | `POST /timeseries/data` | REQUEST_SUCCEEDED | ❌ Failed |
| **OpenFDA** | `GET /drug/event.json` | 400 Bad Request | ❌ Invalid |
| **BEA** | `GET /api/data` | 200 (empty) | ❌ Invalid |
| **EIA** | `GET /v2/electricity/...` | 200 OK | ⚠️ v2 works |
| **USGS** | `GET /nwis/iv/` | 200 OK | ✅ Works (no key needed) |
| **Data.gov** | `GET /api/3/action/...` | 404 Not Found | ❌ 404 Error |
| **DENUE** | `GET /consulta/BuscarActividad` | Timeout | ❌ Timeout |

---

## Quick Test: All APIs at Once

### Using Python Script (Recommended)

```bash
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"

# Full validation report
python scripts/validate_api_keys.py

# Deep analysis with root causes
python scripts/deep_api_analysis.py
```

### Using PowerShell

```powershell
# Set working directory
cd "d:\Data Scraping Project POC\OneExtraction\botasaurus"

# Quick test all keys
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); [print(f'{k}: {v[:20]}...') for k, v in os.environ.items() if 'API' in k or 'TOKEN' in k]"
```

---

## Individual API Tests

### 1. Census Data API ✅ WORKING

#### Test with curl
```bash
$apiKey = "cb6683ac6176d2a4a41bca4f45c6b78e8c7387da"

curl -X GET "https://api.census.gov/data/2019/acs/acs5?get=NAME,B01003_001E&for=state:01&key=$apiKey"
```

**Expected Response:**
```json
[
  ["NAME", "B01003_001E", "state"],
  ["Alabama", "5024279", "01"]
]
```

**Success Indicators:**
- ✅ Status Code: 200
- ✅ Returns JSON array with data
- ✅ No 401/403 errors

---

### 2. BLS API ❌ INVALID KEY

#### Test with curl
```bash
$apiKey = "ddeaff94eb0c444897b6e41af7aead1a"

$body = @{
    seriesid = @("LAUCN040010000000005")
    registrationKey = $apiKey
} | ConvertTo-Json

curl -X POST "https://api.bls.gov/publicAPI/v2/timeseries/data" `
  -H "Content-Type: application/json" `
  -d $body
```

**Expected Response (FAILED):**
```json
{
  "status": "REQUEST_NOT_PROCESSED",
  "message": ["The key:ddeaff94eb0c444897b6e41af7aead1a provided by the User is invalid..."]
}
```

**Problem:** API explicitly rejects the key
**Solution:** Generate new key at https://data.bls.gov/registrationEngine/

---

### 3. OpenFDA API ❌ INVALID FORMAT

#### Test with curl
```bash
$apiKey = "AX6Nh9Xb6krpzg9phodb6ogZ9aq2WzAzqjkgV2sd"

curl -X GET "https://api.fda.gov/drug/event.json?limit=1&apikey=$apiKey"
```

**Expected Response (FAILED):**
```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid parameter: apikey"
  }
}
```

**Status Code:** 400 Bad Request

**Problem:** API key format invalid or not registered
**Solution (A):** Generate at https://open.fda.gov/apis/
**Solution (B):** Use without key (recommended):
```bash
curl -X GET "https://api.fda.gov/drug/event.json?limit=1"
```

---

### 4. BEA API ❌ EMPTY RESPONSE

#### Test with curl
```bash
$apiKey = "240FF73B-E43E-48B0-ACBF-1876ACF8C51A"

curl -X GET "https://apps.bea.gov/api/data?method=NIPA&datasetname=NIPA&tablename=T10101&frequency=A&year=2020&apikey=$apiKey&resultformat=json"
```

**Expected Response (FAILED):**
- Status Code: 200 (looks successful)
- Body: Empty (no JSON data)

**Problem:** Server returns 200 but no content
**Solution:** Verify account at https://apps.bea.gov/api/_login/

---

### 5. EIA API ❌ v1 DEPRECATED (but v2 works!)

#### Test v1 (DEPRECATED)
```bash
$apiKey = "ItCVOdtJMSdwLGY2leDJH3U8s3LU4N1JxaJBK77A"

curl -X GET "https://api.eia.gov/series/?series_id=ELEC.GEN.ALL-US.A&api_key=$apiKey"
```

**Expected Response (FAILED):**
```json
{
  "error": "EIA retired APIv1 on March 13th, 2023. Please use an APIv2 call...",
  "code": 404
}
```

#### Test v2 (WORKS!)
```bash
$apiKey = "ItCVOdtJMSdwLGY2leDJH3U8s3LU4N1JxaJBK77A"

curl -X GET "https://api.eia.gov/v2/electricity/rto/region-data/data/?api_key=$apiKey&length=1"
```

**Expected Response (SUCCESS):**
```json
{
  "response": {
    "total": 100,
    "data": [...]
  }
}
```

**Status Code:** 200 OK

**Solution:** Update endpoint from v1 to v2 in code

---

### 6. USGS Water API ⚠️ SERVICE DOWN

#### Test with curl
```bash
curl -I "https://waterservices.usgs.gov/nwis/iv/"
```

**Expected Response:**
- Current: 503 Service Unavailable
- Should return: 200 OK when service is back

#### Note: USGS doesn't require API key
```bash
# This works without key
curl -X GET "https://waterservices.usgs.gov/nwis/iv/?sites=01646500&format=json"
```

**Solution:** Wait for service to come back online, check status at https://waterservices.usgs.gov/

---

### 7. Data.gov API ❌ 404 NOT FOUND

#### Test with curl
```bash
$apiKey = "dWqhICx4uOPUbUvySbaAqoR1kJBFsah73yUkEYkw"

curl -X GET "https://catalog.data.gov/api/3/action/package_search?q=test&api_key=$apiKey"
```

**Expected Response (FAILED):**
```json
{
  "detail": {},
  "message": "Not Found"
}
```

**Status Code:** 404 Not Found

**Problem:** Endpoint doesn't exist or was moved
**Solution:** Check if Data.gov API moved or use public endpoint without key:
```bash
curl -X GET "https://catalog.data.gov/api/3/action/package_search?q=test"
```

---

### 8. DENUE API (Mexico) ❌ TIMEOUT

#### Test with curl
```bash
$token = "9725a7e7-1508-4dde-45ef-48720161f979"

curl -X GET "https://www.inegi.org.mx/servicios/api/denue/v1/consulta/BuscarActividad?token=$token&actividad=010000" --connect-timeout 10
```

**Expected Response (FAILED):**
- Timeout after ~10 seconds
- Connection refused or no response

**Problem:** 
- Server not responding (might be down)
- Geographic IP blocking (Mexico API from US)
- Network connectivity issue

**Solution:** 
- Wait and retry with longer timeout
- Use VPN if outside Mexico
- Contact INEGI support

---

## Batch Testing

### PowerShell Script: Test All APIs

```powershell
# Save as: test_all_apis.ps1

$APIs = @{
    "Census" = @{
        url = "https://api.census.gov/data/2019/acs/acs5"
        key = "cb6683ac6176d2a4a41bca4f45c6b78e8c7387da"
        params = "?get=NAME,B01003_001E&for=state:01&key="
    }
    "BLS" = @{
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        method = "POST"
        key = "ddeaff94eb0c444897b6e41af7aead1a"
    }
    "EIA-v2" = @{
        url = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
        key = "ItCVOdtJMSdwLGY2leDJH3U8s3LU4N1JxaJBK77A"
        params = "?api_key=&length=1"
    }
}

foreach ($api in $APIs.GetEnumerator()) {
    Write-Host "Testing $($api.Name)..." -ForegroundColor Cyan
    
    try {
        $fullUrl = $api.Value.url + $api.Value.params + $api.Value.key
        $response = Invoke-WebRequest -Uri $fullUrl -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ $($api.Name): $($response.StatusCode)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $($api.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}
```

Run it:
```bash
powershell -ExecutionPolicy Bypass -File test_all_apis.ps1
```

---

## Python Script: Test and Report

```python
# Save as: quick_api_test.py

import requests
from datetime import datetime

APIs = {
    "Census": {
        "url": "https://api.census.gov/data/2019/acs/acs5",
        "params": {"get": "NAME,B01003_001E", "for": "state:01", "key": "cb6683ac6176d2a4a41bca4f45c6b78e8c7387da"},
        "method": "GET"
    },
    "EIA-v2": {
        "url": "https://api.eia.gov/v2/electricity/rto/region-data/data/",
        "params": {"api_key": "ItCVOdtJMSdwLGY2leDJH3U8s3LU4N1JxaJBK77A", "length": 1},
        "method": "GET"
    },
    "OpenFDA": {
        "url": "https://api.fda.gov/drug/event.json",
        "params": {"limit": 1},
        "method": "GET"
    }
}

print(f"\n{'='*70}")
print(f"API Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*70}\n")

for name, config in APIs.items():
    try:
        if config["method"] == "GET":
            r = requests.get(config["url"], params=config["params"], timeout=10)
        else:
            r = requests.post(config["url"], json=config["params"], timeout=10)
        
        status = "✅ OK" if r.status_code == 200 else f"⚠️  {r.status_code}"
        print(f"{name:<15} {status}")
    except Exception as e:
        print(f"{name:<15} ❌ {str(e)[:50]}")

print(f"\n{'='*70}\n")
```

Run it:
```bash
python quick_api_test.py
```

---

## Recommendations by Test Result

### If API Returns 200 OK
✅ **API is working!**
- Do nothing
- Keep using this key

### If API Returns 401/403
❌ **Authentication failed - Key invalid**
- Regenerate new key from API provider
- Make sure key has required permissions
- Check if key has expired

### If API Returns 400
❌ **Bad request - Check parameters**
- Verify parameter names and format
- Check required vs optional params
- Review API documentation

### If API Returns 404
❌ **Endpoint not found**
- Endpoint URL might be wrong
- API might have moved or deprecated
- Check if there's a new version (v1 vs v2)

### If API Returns 503/504
⚠️ **Server error - Temporary issue**
- API service might be down
- Try again in 5-10 minutes
- Check service status page

### If Connection Timeout
⚠️ **Network connectivity issue**
- Server not responding
- Might be geographic blocking
- Try from different network/VPN

---

## Quick Summary: How to Use These Commands

1. **Quick check all keys:**
   ```bash
   python scripts/validate_api_keys.py
   ```

2. **Deep analysis (why they fail):**
   ```bash
   python scripts/deep_api_analysis.py
   ```

3. **Test specific API:**
   - Pick one from Section "Individual API Tests" above
   - Copy the curl command
   - Run in PowerShell
   - Check expected response

4. **Monitor over time:**
   - Run validation script daily
   - Track which APIs start/stop working
   - Update .env when keys change

---

## Troubleshooting

### Command Not Found: "python"
```powershell
# Use python3 instead
python3 scripts/validate_api_keys.py

# Or use full path
C:\Python39\python.exe scripts/validate_api_keys.py
```

### SSL Certificate Error
```powershell
# Ignore SSL (for testing only, not for production)
curl -k -X GET "https://api.example.com/..."
```

### Invalid JSON Response
```powershell
# Check if response is actually JSON
curl -I "https://api.example.com/"  # Check headers first
curl -X GET "https://api.example.com/" | ConvertFrom-Json
```

### Rate Limiting (429 Too Many Requests)
```powershell
# Add delay between requests
Start-Sleep -Seconds 5
curl -X GET "https://api.example.com/..."
```

---

## For Future Reference

Save these test commands for monitoring:

```bash
# Weekly API check
*/0 * * * * cd /path/to/project && python scripts/validate_api_keys.py

# Monthly deep analysis
*/0 0 1 * * cd /path/to/project && python scripts/deep_api_analysis.py > /tmp/api-analysis-$(date +\%Y-\%m-\%d).txt
```

---

## Next Steps

1. **Run validation:** `python scripts/validate_api_keys.py`
2. **Review results:** See which ones fail
3. **Fix priority ones:** Follow the regeneration guide
4. **Test fixes:** Re-run validation after changes
5. **Monitor:** Check periodically (weekly/monthly)

Your pipeline works with or without these fixes! ✅
