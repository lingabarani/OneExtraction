#!/usr/bin/env python3
"""
Load OneExtraction data into Dataforge PostgreSQL database.
Transfers companies and executives data, prepares for enrichment.
"""

import json
import os
import sys
import psycopg2
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging
from datetime import datetime, timezone
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataforgeLoader:
    """Load OneExtraction data into Dataforge PostgreSQL"""
    
    def __init__(self, db_host: str = "localhost", db_port: int = 5432,
                 db_user: str = "forge", db_password: str = None,
                 db_name: str = "oneextraction"):
        """Initialize database connection parameters"""
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password or os.getenv("FORGE_DB_PASSWORD")
        self.db_name = db_name
        self.conn = None
        self.stats = {
            'companies_loaded': 0,
            'companies_updated': 0,
            'companies_skipped': 0,
            'people_loaded': 0,
            'people_updated': 0,
            'errors': 0
        }
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name
            )
            logger.info(f"✅ Connected to PostgreSQL: {self.db_host}:{self.db_port}/{self.db_name}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def load_json_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load JSON data file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ Loaded {len(data)} records from {filepath.name}")
            return data
        except Exception as e:
            logger.error(f"❌ Error loading {filepath}: {e}")
            return []
    
    def insert_companies(self, companies: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Insert companies into businesses table"""
        logger.info(f"Loading {len(companies)} companies...")
        
        cur = self.conn.cursor()
        inserted = 0
        updated = 0
        skipped = 0
        
        for i, company in enumerate(companies):
            try:
                # Extract fields
                company_id = company.get('company_id')
                legal_name = company.get('legal_name') or company.get('trade_name')
                website = company.get('website')
                domain = company.get('domain')
                ein = company.get('ein')
                cik = company.get('cik')
                cage_code = company.get('cage_code')
                uei = company.get('uei')
                industry = company.get('industry')
                naics_code = company.get('naics_code')
                sic_code = company.get('sic_code')
                
                # Location
                address = company.get('address', {})
                city = address.get('city')
                state = address.get('state')
                state_code = address.get('state_code')
                zip_code = address.get('zip_code')
                
                # Phone/email
                phone = company.get('phone')
                email = company.get('email')
                
                # Employee count
                employee_min = company.get('employee_count_min')
                employee_max = company.get('employee_count_max')
                employee_band = company.get('employee_count_band')
                
                # Metadata
                source = company.get('source')
                data_quality = company.get('data_quality_score')
                
                # Insert or update
                cur.execute("""
                INSERT INTO businesses (
                    company_id, name, legal_name, website_url, domain,
                    ein, cik, cage_code, uei,
                    industry, naics_code, sic_code,
                    city, state, state_code, zip_code,
                    phone, email,
                    employee_count_min, employee_count_max, employee_count_band,
                    source, data_quality_score,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s
                )
                ON CONFLICT (company_id) DO UPDATE SET
                    website_url = EXCLUDED.website_url,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    industry = EXCLUDED.industry,
                    data_quality_score = EXCLUDED.data_quality_score,
                    updated_at = NOW()
                RETURNING xmax
                """, (
                    company_id, legal_name, legal_name, website, domain,
                    ein, cik, cage_code, uei,
                    industry, naics_code, sic_code,
                    city, state, state_code, zip_code,
                    phone, email,
                    employee_min, employee_max, employee_band,
                    source, data_quality,
                    datetime.now(timezone.utc), datetime.now(timezone.utc)
                ))
                
                result = cur.fetchone()
                if result and result[0] == 0:
                    inserted += 1
                else:
                    updated += 1
                
                if (i + 1) % 100 == 0:
                    logger.info(f"  Progress: {i + 1}/{len(companies)} (Inserted: {inserted}, Updated: {updated})")
            
            except Exception as e:
                logger.error(f"Error inserting company {company.get('company_id')}: {e}")
                self.stats['errors'] += 1
                skipped += 1
                continue
        
        self.conn.commit()
        cur.close()
        
        logger.info(f"✅ Companies loaded: {inserted} inserted, {updated} updated, {skipped} skipped")
        self.stats['companies_loaded'] = inserted
        self.stats['companies_updated'] = updated
        self.stats['companies_skipped'] = skipped
        
        return inserted, updated
    
    def insert_people(self, people: List[Dict[str, Any]]) -> int:
        """Insert people/executives into people table"""
        logger.info(f"Loading {len(people)} executives...")
        
        cur = self.conn.cursor()
        inserted = 0
        updated = 0
        
        for i, person in enumerate(people):
            try:
                person_id = person.get('person_id')
                company_id = person.get('company_id')
                first_name = person.get('first_name')
                last_name = person.get('last_name')
                full_name = person.get('full_name')
                title = person.get('title')
                standardized_title = person.get('standardized_title')
                seniority = person.get('seniority_level')
                department = person.get('department')
                work_email = person.get('work_email')
                email_status = person.get('email_status')
                email_confidence = person.get('email_confidence_score')
                direct_phone = person.get('direct_phone')
                phone_type = person.get('phone_type')
                is_active = person.get('is_active', True)
                source = person.get('source')
                
                # Insert or update
                cur.execute("""
                INSERT INTO people (
                    person_id, company_id,
                    first_name, last_name, full_name,
                    title, standardized_title, seniority_level, department,
                    work_email, email_status, email_confidence_score,
                    direct_phone, phone_type,
                    is_active, source,
                    created_at, updated_at
                ) VALUES (
                    %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s
                )
                ON CONFLICT (person_id) DO UPDATE SET
                    work_email = EXCLUDED.work_email,
                    title = EXCLUDED.title,
                    is_active = EXCLUDED.is_active,
                    updated_at = NOW()
                RETURNING xmax
                """, (
                    person_id, company_id,
                    first_name, last_name, full_name,
                    title, standardized_title, seniority, department,
                    work_email, email_status, email_confidence,
                    direct_phone, phone_type,
                    is_active, source,
                    datetime.now(timezone.utc), datetime.now(timezone.utc)
                ))
                
                result = cur.fetchone()
                if result and result[0] == 0:
                    inserted += 1
                else:
                    updated += 1
                
                if (i + 1) % 500 == 0:
                    logger.info(f"  Progress: {i + 1}/{len(people)} (Inserted: {inserted}, Updated: {updated})")
            
            except Exception as e:
                logger.error(f"Error inserting person {person.get('person_id')}: {e}")
                self.stats['errors'] += 1
                continue
        
        self.conn.commit()
        cur.close()
        
        logger.info(f"✅ People loaded: {inserted} inserted, {updated} updated")
        self.stats['people_loaded'] = inserted
        self.stats['people_updated'] = updated
        
        return inserted
    
    def generate_report(self):
        """Generate loading report"""
        logger.info("")
        logger.info("=" * 50)
        logger.info("📊 Data Loading Report")
        logger.info("=" * 50)
        logger.info(f"Companies loaded:    {self.stats['companies_loaded']}")
        logger.info(f"Companies updated:   {self.stats['companies_updated']}")
        logger.info(f"Companies skipped:   {self.stats['companies_skipped']}")
        logger.info(f"People loaded:       {self.stats['people_loaded']}")
        logger.info(f"People updated:      {self.stats['people_updated']}")
        logger.info(f"Errors:              {self.stats['errors']}")
        logger.info("=" * 50)
        logger.info("")
    
    def run(self):
        """Run the data loading pipeline"""
        logger.info("Starting OneExtraction data loading...")
        logger.info("")
        
        # Connect to database
        self.connect()
        
        # Load companies data
        companies_file = Path("output/us/api/companies/us_companies.json")
        if companies_file.exists():
            companies = self.load_json_file(companies_file)
            self.insert_companies(companies)
        else:
            logger.warning(f"⚠️  Companies file not found: {companies_file}")
        
        # Load people data
        people_file = Path("output/us/api/people/us_people.json")
        if people_file.exists():
            people = self.load_json_file(people_file)
            self.insert_people(people)
        else:
            logger.warning(f"⚠️  People file not found: {people_file}")
        
        # Generate report
        self.generate_report()
        
        # Disconnect
        self.disconnect()
        
        logger.info("✅ Data loading complete!")

if __name__ == "__main__":
    # Get database credentials from environment or use defaults
    loader = DataforgeLoader(
        db_host=os.getenv("FORGE_DB_HOST", "localhost"),
        db_port=int(os.getenv("FORGE_DB_PORT", 5432)),
        db_user=os.getenv("FORGE_DB_USER", "forge"),
        db_password=os.getenv("FORGE_DB_PASSWORD", "oneextraction_secure_2026"),
        db_name=os.getenv("FORGE_DB_NAME", "oneextraction")
    )
    
    loader.run()
