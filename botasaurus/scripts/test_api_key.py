#!/usr/bin/env python3
"""
INEGI DENUE API Key Health & Connectivity Verification Utility.
Run this script anytime to check if your DENUE_API_TOKEN is active, valid, and responding.

Usage:
  python scripts/test_api_key.py
  python scripts/test_api_key.py --token YOUR_TOKEN_HERE
"""

import sys
import os
import time
import json
import argparse
from pathlib import Path

# Add project paths
current_dir = Path(__file__).resolve().parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

import requests
from dotenv import load_dotenv

def test_inegi_api_token(token: str = None):
    # Load from .env if not explicitly passed
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    api_token = token or os.getenv("DENUE_API_TOKEN")
    
    print("=" * 70)
    print(" [INEGI DENUE API KEY VERIFICATION TOOL]")
    print("=" * 70)
    
    if not api_token or api_token.strip() == "":
        print("[ERROR] DENUE_API_TOKEN is NOT set!")
        print(f"Please set your token in: {env_path}")
        print("Register for a free token at: https://www.inegi.org.mx/servicios/api_denue.html")
        print("=" * 70)
        return False

    api_token = api_token.strip()
    masked_token = f"{api_token[:8]}...{api_token[-4:]}" if len(api_token) > 12 else api_token
    print(f" Token Checked     : {masked_token}")
    print(f" Testing Endpoint  : INEGI DENUE v1.0 (BuscarAreaAct / CDMX)")
    print(f" Connecting to     : https://www.inegi.org.mx/app/api/denue/v1/consulta/")
    print("-" * 70)

    # INEGI Query for first 5 records in State 09 (CDMX)
    test_url = f"https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaAct/todos/09/0/0/1/5/{api_token}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }

    start_time = time.time()
    try:
        response = requests.get(test_url, headers=headers, timeout=15)
        duration = round(time.time() - start_time, 2)
        
        print(f" Response Status   : HTTP {response.status_code}")
        print(f" Response Time     : {duration}s")
        print("-" * 70)

        if response.status_code == 200:
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print("[SUCCESS] API KEY IS ACTIVE, VALID & RETURNING LIVE DATA!")
                    print(f" Records Received  : {len(data)} live Mexican business establishments\n")
                    
                    print(" [SAMPLE LIVE RECORD RETURNED FROM INEGI]")
                    sample = data[0]
                    print(f"  • Business Name  : {sample.get('Nombre') or sample.get('Razon_social')}")
                    print(f"  • Legal Name     : {sample.get('Razon_social') or 'N/A'}")
                    print(f"  • Activity/SCIAN : {sample.get('Clase_actividad')}")
                    print(f"  • Location       : {sample.get('Municipio')}, {sample.get('Ubicacion')}")
                    print(f"  • Phone Number   : {sample.get('Telefono') or 'N/A'}")
                    print(f"  • Email Address  : {sample.get('Correo_e') or 'N/A'}")
                    print(f"  • Website        : {sample.get('Sitio_internet') or 'N/A'}")
                    print(f"  • Coordinates    : Lat {sample.get('Latitud')}, Lng {sample.get('Longitud')}")
                    print("=" * 70)
                    return True
                elif isinstance(data, dict) and "error" in str(data).lower():
                    print(f"[FAILED] INEGI returned error response: {data}")
                    print("Your token might be invalid or deactivated by INEGI.")
                    return False
                else:
                    print(f"[WARNING] Request succeeded but returned unexpected payload: {data}")
                    return False
            except Exception as json_err:
                print(f"[FAILED] Could not parse JSON response: {json_err}")
                print(f"Raw Response: {response.text[:300]}")
                return False
        elif response.status_code == 403 or response.status_code == 401:
            print("[FAILED] HTTP 401/403: UNAUTHORIZED / INVALID API TOKEN.")
            print("The token is not recognized by INEGI. Please check your token at https://www.inegi.org.mx/servicios/api_denue.html")
            return False
        else:
            print(f"[FAILED] HTTP Error {response.status_code}: {response.text[:300]}")
            return False

    except requests.exceptions.Timeout:
        print("[ERROR] Connection timed out after 15s. INEGI servers might be busy.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error connecting to INEGI: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test INEGI DENUE API Key Health")
    parser.add_argument("--token", "-t", type=str, default=None, help="Explicit API token to test")
    args = parser.parse_args()
    
    success = test_inegi_api_token(token=args.token)
    sys.exit(0 if success else 1)
