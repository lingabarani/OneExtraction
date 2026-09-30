#!/usr/bin/env python3
"""
Email Extraction Module
Extracts emails from companies using multiple detection methods
"""

import sqlite3
import re
import time
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime, timezone
import requests
from urllib.parse import urljoin, urlparse
import json

# ── DB connector: supports both SQLite and PostgreSQL ──────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from db_connector import get_connection, get_cursor, placeholder, db_info, DB_TYPE
    _USE_CONNECTOR = True
except ImportError:
    _USE_CONNECTOR = False
    DB_TYPE = "sqlite"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailExtractor:
    """Extract emails from company websites and data"""
    
    def __init__(self, db_path: str = "output/us/api/oneextraction.db"):
        self.db_path = db_path
        self.conn = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OneExtraction/1.0'
        })
        self.stats = {
            'companies_processed': 0,
            'emails_extracted': 0,
            'emails_from_website': 0,
            'emails_from_pattern': 0,
            'emails_from_contact_page': 0,
            'errors': 0
        }
    
    def connect(self):
        """Connect to database (PostgreSQL or SQLite via db_connector)"""
        if _USE_CONNECTOR:
            self.conn = get_connection()
            logger.info(f"Connected to {db_info()}")
        else:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to {self.db_path}")
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_companies_needing_emails(self, limit: int = 1000) -> List[Dict]:
        """Get companies without emails"""
        cur = self.conn.cursor()
        
        cur.execute("""
        SELECT id, name, website, domain, industry
        FROM companies
        WHERE email IS NULL
        LIMIT ?
        """, (limit,))
        
        companies = []
        for row in cur.fetchall():
            companies.append({
                'id': row['id'],
                'name': row['name'],
                'website': row['website'],
                'domain': row['domain'],
                'industry': row['industry']
            })
        
        return companies
    
    def extract_emails_from_website(self, url: str, company_name: str = "") -> Set[str]:
        """Extract emails from website"""
        emails = set()
        
        if not url:
            return emails
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            content = response.text
            
            # Extract mailto links
            mailto_pattern = r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            for match in re.finditer(mailto_pattern, content, re.IGNORECASE):
                email = match.group(1).lower()
                if self._is_valid_email(email):
                    emails.add(email)
            
            # Extract email addresses from text
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            for match in re.finditer(email_pattern, content):
                email = match.group(1).lower()
                # Filter common false positives
                if self._is_valid_email(email) and not self._is_false_positive(email):
                    emails.add(email)
            
            self.stats['emails_from_website'] += len(emails)
            
        except Exception as e:
            logger.debug(f"Error extracting from website {url}: {e}")
        
        return emails
    
    def extract_emails_from_patterns(self, domain: str, company_name: str = "") -> Set[str]:
        """Generate emails using common patterns"""
        emails = set()
        
        if not domain:
            return emails
        
        # Clean domain
        domain = domain.lower().strip()
        if not domain:
            return emails
        
        # Common email patterns
        patterns = [
            f"info@{domain}",
            f"contact@{domain}",
            f"hello@{domain}",
            f"support@{domain}",
            f"sales@{domain}",
            f"admin@{domain}",
            f"team@{domain}",
            f"help@{domain}",
        ]
        
        # If we have company name, generate name-based patterns
        if company_name:
            name_parts = company_name.lower().split()
            if len(name_parts) >= 2:
                first = name_parts[0]
                last = name_parts[-1]
                
                # Remove common words
                first = first.replace("inc", "").replace("llc", "").replace("corp", "").strip()
                last = last.replace("inc", "").replace("llc", "").replace("corp", "").strip()
                
                if first and last:
                    patterns.extend([
                        f"{first}.{last}@{domain}",
                        f"{first}@{domain}",
                        f"firstname.lastname@{domain}",
                    ])
        
        for email in patterns:
            if self._is_valid_email(email):
                emails.add(email)
        
        self.stats['emails_from_pattern'] += len(emails)
        return emails
    
    def _is_valid_email(self, email: str) -> bool:
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_false_positive(self, email: str) -> bool:
        """Detect common false positive emails"""
        false_positives = [
            'noreply@',
            'no-reply@',
            'donotreply@',
            'example@',
            'test@',
            'domain@',
            'placeholder@',
            'mail@',
            '[email',
            '@example',
        ]
        
        email_lower = email.lower()
        for fp in false_positives:
            if fp in email_lower:
                return True
        
        return False
    
    def extract_emails_for_company(self, company: Dict) -> Dict[str, any]:
        """Extract emails for a single company"""
        all_emails = {}
        sources = []
        
        # Try website
        if company['website']:
            website_emails = self.extract_emails_from_website(company['website'], company['name'])
            if website_emails:
                all_emails.update({email: 'website' for email in website_emails})
                sources.append('website')
        
        # Try domain
        if company['domain']:
            domain_emails = self.extract_emails_from_patterns(company['domain'], company['name'])
            if domain_emails:
                for email in domain_emails:
                    if email not in all_emails:
                        all_emails[email] = 'pattern'
                sources.append('pattern')
        
        # Pick best email
        best_email = None
        best_source = None
        
        if all_emails:
            # Prefer website over pattern
            for email, source in all_emails.items():
                if source == 'website':
                    best_email = email
                    best_source = source
                    break
            
            if not best_email:
                best_email = list(all_emails.keys())[0]
                best_source = all_emails[best_email]
        
        return {
            'email': best_email,
            'source': best_source,
            'all_emails': list(all_emails.keys()),
            'confidence': 80 if best_source == 'website' else 40
        }
    
    def save_extracted_email(self, company_id: str, email_data: Dict):
        """Save extracted email to database (PostgreSQL + SQLite compatible)"""
        if not email_data['email']:
            return False

        cur = self.conn.cursor()
        ph  = placeholder()

        try:
            cur.execute(
                f"UPDATE companies SET email = {ph}, updated_at = {ph} WHERE id = {ph}",
                (email_data['email'], datetime.now(timezone.utc).isoformat(), company_id)
            )

            if DB_TYPE == "postgresql":
                cur.execute(f"""
                    INSERT INTO enrichment_results
                        (id, company_id, email, email_verified, email_status)
                    VALUES ({ph},{ph},{ph},{ph},{ph})
                    ON CONFLICT (id) DO UPDATE SET
                        email        = EXCLUDED.email,
                        email_status = EXCLUDED.email_status,
                        updated_at   = NOW()
                """, (f"{company_id}_email", company_id, email_data['email'], False, 'EXTRACTED'))
            else:
                cur.execute(f"""
                    INSERT OR REPLACE INTO enrichment_results
                        (id, company_id, email, email_verified, email_status)
                    VALUES ({ph},{ph},{ph},{ph},{ph})
                """, (f"{company_id}_email", company_id, email_data['email'], False, 'EXTRACTED'))
            
            self.conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error saving email for {company_id}: {e}")
            return False
    
    def run_extraction(self, limit: int = 1000, batch_size: int = 100):
        """Run email extraction pipeline"""
        logger.info("=" * 60)
        logger.info("📧 Email Extraction Pipeline")
        logger.info("=" * 60)
        logger.info("")
        
        self.connect()
        
        try:
            companies = self.get_companies_needing_emails(limit)
            total = len(companies)
            
            logger.info(f"Processing {total} companies...")
            logger.info("")
            
            for i, company in enumerate(companies):
                try:
                    # Extract email
                    email_data = self.extract_emails_for_company(company)
                    
                    if email_data['email']:
                        self.save_extracted_email(company['id'], email_data)
                        self.stats['emails_extracted'] += 1
                    
                    self.stats['companies_processed'] += 1
                    
                    # Progress indicator
                    if (i + 1) % batch_size == 0:
                        logger.info(f"  Progress: {i + 1}/{total} - Emails found: {self.stats['emails_extracted']}")
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                except Exception as e:
                    logger.error(f"Error processing {company['name']}: {e}")
                    self.stats['errors'] += 1
                    continue
            
            # Print summary
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ Extraction Summary")
            logger.info("=" * 60)
            logger.info(f"Companies processed:      {self.stats['companies_processed']:,}")
            logger.info(f"Emails extracted:         {self.stats['emails_extracted']:,}")
            logger.info(f"  From websites:          {self.stats['emails_from_website']:,}")
            logger.info(f"  From patterns:          {self.stats['emails_from_pattern']:,}")
            logger.info(f"Errors:                   {self.stats['errors']}")
            logger.info("")
            
            if self.stats['companies_processed'] > 0:
                coverage = 100 * self.stats['emails_extracted'] / self.stats['companies_processed']
                logger.info(f"Email coverage:           {coverage:.1f}%")
            
            logger.info("=" * 60)
        
        finally:
            self.disconnect()

if __name__ == "__main__":
    extractor = EmailExtractor()
    extractor.run_extraction(limit=1000, batch_size=100)
