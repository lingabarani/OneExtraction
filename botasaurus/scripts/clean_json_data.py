#!/usr/bin/env python3
"""
Clean corrupted JSON data files
Fixes formatting issues and prepares for loading
"""

import json
import re
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_json_file(input_path: Path, output_path: Path = None):
    """Clean a corrupted JSON file"""
    if output_path is None:
        output_path = input_path
    
    logger.info(f"Cleaning {input_path.name}...")
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix common corruption patterns
        # Remove trailing 'k' after null values (e.g., null,k -> null,)
        content = re.sub(r'null,k', 'null,', content)
        
        # Remove any stray characters
        content = re.sub(r'([}])\s*([a-z])\s*([,\n])', r'\1\3', content)
        
        # Try to parse it
        data = json.loads(content)
        
        # Write cleaned version
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Cleaned: {len(data)} records")
        return True
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON Error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Clean companies file
    companies_file = Path("output/us/api/companies/us_companies.json")
    if companies_file.exists():
        clean_json_file(companies_file)
    
    # Clean people file
    people_file = Path("output/us/api/people/us_people.json")
    if people_file.exists():
        clean_json_file(people_file)
    
    logger.info("✅ Cleaning complete!")
