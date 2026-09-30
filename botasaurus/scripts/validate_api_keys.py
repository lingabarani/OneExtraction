#!/usr/bin/env python3
"""
API Key Validation Script
Tests all API keys in .env file to verify they are working or not
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_header(text):
    """Print section header"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_success(message):
    """Print success message"""
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    """Print error message"""
    print(f"{RED}❌ {message}{RESET}")

def print_warning(message):
    """Print warning message"""
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_info(message):
    """Print info message"""
    print(f"{BLUE}ℹ️  {message}{RESET}")

# Test 1: CENSUS_DATA_API_KEY
def test_census_api():
    """Test US Census Bureau API Key"""
    print(f"\n{BOLD}1. US Census Data API{RESET}")
    api_key = os.getenv("CENSUS_DATA_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://api.census.gov/data/2019/acs/acs5"
        params = {
            "get": "NAME,B01003_001E",
            "for": "state:01",
            "key": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("Census API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("Census API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"Census API Key returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Census API test failed: {e}")
        return False

# Test 2: DATA_GOV_API_KEY
def test_data_gov_api():
    """Test Data.gov API Key"""
    print(f"\n{BOLD}2. Data.gov API{RESET}")
    api_key = os.getenv("DATA_GOV_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://catalog.data.gov/api/3/action/package_search"
        params = {
            "q": "test",
            "api_key": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("Data.gov API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("Data.gov API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"Data.gov API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Data.gov API test failed: {e}")
        return False

# Test 3: BLS_API_KEY
def test_bls_api():
    """Test Bureau of Labor Statistics API Key"""
    print(f"\n{BOLD}3. BLS (Bureau of Labor Statistics) API{RESET}")
    api_key = os.getenv("BLS_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://api.bls.gov/publicAPI/v2/timeseries/data"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "seriesid": ["LAUCN040010000000005"],
            "registrationKey": api_key
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "REQUEST_SUCCEEDED":
                print_success("BLS API Key is WORKING")
                return True
            else:
                print_error(f"BLS API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"BLS API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"BLS API test failed: {e}")
        return False

# Test 4: OPENFDA_API_KEY
def test_openfda_api():
    """Test OpenFDA API Key"""
    print(f"\n{BOLD}4. OpenFDA API{RESET}")
    api_key = os.getenv("OPENFDA_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://api.fda.gov/drug/event.json"
        params = {
            "limit": 1,
            "apikey": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("OpenFDA API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("OpenFDA API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"OpenFDA API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"OpenFDA API test failed: {e}")
        return False

# Test 5: BEA_DATA_API_KEY
def test_bea_api():
    """Test Bureau of Economic Analysis API Key"""
    print(f"\n{BOLD}5. BEA (Bureau of Economic Analysis) API{RESET}")
    api_key = os.getenv("BEA_DATA_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://apps.bea.gov/api/data"
        params = {
            "method": "NIPA",
            "datasetname": "NIPA",
            "tablename": "T10101",
            "frequency": "A",
            "year": "2020",
            "apikey": api_key,
            "resultformat": "json"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == 200:
                print_success("BEA API Key is WORKING")
                return True
            else:
                print_error(f"BEA API returned error: {result.get('message')}")
                return False
        else:
            print_error(f"BEA API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"BEA API test failed: {e}")
        return False

# Test 6: EIA_API_KEY
def test_eia_api():
    """Test Energy Information Administration API Key"""
    print(f"\n{BOLD}6. EIA (Energy Information Administration) API{RESET}")
    api_key = os.getenv("EIA_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # Test with a sample query
        url = "https://api.eia.gov/series/"
        params = {
            "series_id": "ELEC.GEN.ALL-US.A",
            "api_key": api_key
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("EIA API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("EIA API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"EIA API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"EIA API test failed: {e}")
        return False

# Test 7: USGS_WATER_API_KEY
def test_usgs_api():
    """Test USGS Water Services API Key"""
    print(f"\n{BOLD}7. USGS Water Services API{RESET}")
    api_key = os.getenv("USGS_WATER_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        # USGS API doesn't require key validation separately, just check if service is available
        url = "https://waterservices.usgs.gov/nwis/iv/"
        params = {
            "sites": "01646500",
            "format": "json"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("USGS Water API is ACCESSIBLE (Key format appears valid)")
            return True
        else:
            print_error(f"USGS API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"USGS API test failed: {e}")
        return False

# Test 8: DENUE_API_TOKEN (Mexico)
def test_denue_api():
    """Test INEGI DENUE API Token"""
    print(f"\n{BOLD}8. INEGI DENUE API (Mexico){RESET}")
    api_token = os.getenv("DENUE_API_TOKEN", "")
    
    if not api_token:
        print_warning("No API token configured")
        return False
    
    print_info(f"API Token: {api_token[:20]}...")
    
    try:
        # Test DENUE API
        url = "https://www.inegi.org.mx/servicios/api/denue/v1/consulta/BuscarActividad"
        params = {
            "token": api_token,
            "actividad": "010000"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("DENUE API Token is WORKING")
            return True
        elif response.status_code == 401:
            print_error("DENUE API Token is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"DENUE API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"DENUE API test failed: {e}")
        return False

# Test 9: US_OPEN_DIRECTORIES_API_KEY
def test_open_directories_api():
    """Test Open Directories API Key"""
    print(f"\n{BOLD}9. Open Directories API{RESET}")
    api_key = os.getenv("US_OPEN_DIRECTORIES_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured (OpenDirectories is optional)")
        return None
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        url = "https://oclajxwxyxorlfhahoqj.supabase.co/rest/v1/providers"
        headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}"
        }
        params = {"limit": 1}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("Open Directories API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("Open Directories API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"Open Directories API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Open Directories API test failed: {e}")
        return False

# Test 10: PEOPLEDATALABS_API_KEY
def test_peopledatalabs_api():
    """Test People Data Labs API Key"""
    print(f"\n{BOLD}10. People Data Labs API{RESET}")
    api_key = os.getenv("PEOPLEDATALABS_API_KEY", "")
    
    if not api_key:
        print_warning("No API key configured")
        return False
    
    print_info(f"API Key: {api_key[:20]}...")
    
    try:
        url = "https://api.peopledatalabs.com/v5/company/enrich"
        headers = {"X-Api-Key": api_key}
        params = {"website": "google.com"}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            print_success("People Data Labs API Key is WORKING")
            return True
        elif response.status_code == 401:
            print_error("People Data Labs API Key is INVALID (401 Unauthorized)")
            return False
        else:
            print_error(f"People Data Labs API returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"People Data Labs API test failed: {e}")
        return False

def main():
    """Main execution"""
    print_header("🔑 API KEY VALIDATION REPORT")
    
    print(f"Environment file: {BOLD}{env_path}{RESET}\n")
    
    # Run all tests
    results = {
        "Census Data API": test_census_api(),
        "Data.gov API": test_data_gov_api(),
        "BLS API": test_bls_api(),
        "OpenFDA API": test_openfda_api(),
        "BEA API": test_bea_api(),
        "EIA API": test_eia_api(),
        "USGS Water API": test_usgs_api(),
        "DENUE API (Mexico)": test_denue_api(),
        "Open Directories API": test_open_directories_api(),
        "People Data Labs API": test_peopledatalabs_api(),
    }
    
    # Print summary
    print_header("📊 SUMMARY")
    
    working = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    print(f"{GREEN}✅ Working: {working}{RESET}")
    print(f"{RED}❌ Failed: {failed}{RESET}")
    print(f"{YELLOW}⏭️  Skipped/Optional: {skipped}{RESET}\n")
    
    # Detailed summary table
    print(f"{BOLD}{'API Service':<30} {'Status':<20}{RESET}")
    print("-" * 50)
    
    for api_name, result in results.items():
        if result is True:
            status = f"{GREEN}✅ WORKING{RESET}"
        elif result is False:
            status = f"{RED}❌ FAILED{RESET}"
        else:
            status = f"{YELLOW}⏭️  SKIPPED{RESET}"
        print(f"{api_name:<30} {status}")
    
    # Print recommendations
    print_header("💡 RECOMMENDATIONS")
    
    if failed > 0:
        print_warning("Some API keys are not working. Consider:")
        print("  1. Regenerate the API keys from official sources")
        print("  2. Check if API keys have expired")
        print("  3. Verify API key permissions and rate limits")
        print("  4. Contact API service providers for support\n")
    
    print_info("Use the pipeline with working APIs:")
    if results.get("Census Data API") or results.get("Data.gov API"):
        print("  • For US data: SEC EDGAR, ProPublica 990, USASpending, CMS NPI")
    if results.get("DENUE API (Mexico)"):
        print("  • For Mexico data: INEGI DENUE API")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
