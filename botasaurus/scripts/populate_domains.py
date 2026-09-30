"""
Generate placeholder domains for US companies based on company names.
This allows email extraction to work with pattern-based generation.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_domain_from_name(company_name: str) -> Optional[str]:
    """
    Generate a plausible domain from company name.
    
    Examples:
    - "APPLE INC" -> "apple.com"
    - "MICROSOFT CORPORATION" -> "microsoft.com"
    - "TECH SOLUTIONS LLC" -> "techsolutions.com"
    """
    if not company_name:
        return None
    
    # Convert to lowercase and remove non-alphanumeric
    cleaned = company_name.lower().strip()
    
    # Remove common suffixes
    cleaned = re.sub(r'\b(inc|corp|corp|corporation|llc|ltd|llp|pllc|s\.a|s\.a\.c|s\.a\.c\.v|de c\.v|a\.c)\b', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    if not cleaned:
        return None
    
    # Take first 2-3 words max for domain
    words = cleaned.split()[:3]
    domain_base = ''.join(words)
    
    # Remove any remaining special characters
    domain_base = re.sub(r'[^a-z0-9]', '', domain_base)
    
    if len(domain_base) < 3:
        # Too short, try to use full name
        domain_base = re.sub(r'[^a-z0-9]', '', cleaned)
    
    if len(domain_base) < 3:
        return None
    
    # Cap at reasonable length
    domain_base = domain_base[:30]
    
    return f"{domain_base}.com"


def populate_domains(db_path: str = "output/us/api/oneextraction.db") -> bool:
    """Populate domain field for companies missing it."""
    
    try:
        logger.info("=" * 60)
        logger.info("🌐 Domain Population Pipeline")
        logger.info("=" * 60)
        logger.info("")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        logger.info(f"✅ Connected to SQLite: {db_path}")
        logger.info("")
        
        # Get companies without domains
        cursor.execute("""
            SELECT id, name, domain
            FROM companies
            WHERE domain IS NULL
        """)
        
        companies_needing_domain = cursor.fetchall()
        total = len(companies_needing_domain)
        
        logger.info(f"Found {total} companies without domains")
        logger.info("")
        
        # Generate domains
        domains_generated = 0
        update_cursor = conn.cursor()
        
        for idx, company in enumerate(companies_needing_domain):
            company_id = company['id']
            company_name = company['name']
            
            # Generate domain
            generated_domain = generate_domain_from_name(company_name)
            
            if generated_domain:
                # Update database
                update_cursor.execute("""
                    UPDATE companies
                    SET domain = ?
                    WHERE id = ?
                """, (generated_domain, company_id))
                domains_generated += 1
            
            # Progress logging
            if (idx + 1) % 200 == 0:
                logger.info(f"  Progress: {idx + 1}/{total} - Domains generated: {domains_generated}")
        
        conn.commit()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Domain Population Summary")
        logger.info("=" * 60)
        logger.info(f"Companies processed:    {total}")
        logger.info(f"Domains generated:      {domains_generated}")
        logger.info(f"Coverage:               {(domains_generated/total*100):.1f}%")
        logger.info("=" * 60)
        logger.info("")
        
        # Verify
        cursor.execute("SELECT COUNT(*) as count FROM companies WHERE domain IS NOT NULL")
        with_domain = cursor.fetchone()['count']
        logger.info(f"Verification: {with_domain} companies now have domains")
        logger.info("")
        
        conn.close()
        
        logger.info("✅ Domain population complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = populate_domains()
    exit(0 if success else 1)
