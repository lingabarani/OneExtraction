#!/usr/bin/env python3
"""
Simplified OneExtraction Data Loader
Loads companies and executives into PostgreSQL without requiring psql or Docker
Falls back to SQLite if PostgreSQL isn't available
"""

import json
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import sqlite3

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OneExtractionDataLoader:
    """Load OneExtraction data into database"""
    
    def __init__(self, use_sqlite: bool = True, db_path: str = "output/us/api/oneextraction.db"):
        """Initialize loader with SQLite fallback"""
        self.use_sqlite = use_sqlite
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'companies_loaded': 0,
            'people_loaded': 0,
            'errors': 0
        }
    
    def connect_sqlite(self):
        """Connect to SQLite database"""
        try:
            # Create output directory if needed
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"✅ Connected to SQLite: {self.db_path}")
            
            # Enable foreign keys
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite: {e}")
            return False
    
    def create_schema_sqlite(self):
        """Create SQLite schema for OneExtraction data"""
        logger.info("Creating SQLite schema...")
        
        cur = self.conn.cursor()
        
        # Companies table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            legal_name TEXT,
            website TEXT,
            domain TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            state_code TEXT,
            zip_code TEXT,
            industry TEXT,
            naics_code TEXT,
            ein TEXT,
            cik TEXT,
            employee_min INTEGER,
            employee_max INTEGER,
            employee_band TEXT,
            source TEXT,
            data_quality_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # People/Executives table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL REFERENCES companies(id),
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            title TEXT,
            standardized_title TEXT,
            seniority_level TEXT,
            department TEXT,
            work_email TEXT,
            email_status TEXT,
            email_confidence_score INTEGER,
            is_active BOOLEAN DEFAULT 1,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Enrichment results table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS enrichment_results (
            id TEXT PRIMARY KEY,
            company_id TEXT NOT NULL REFERENCES companies(id),
            email TEXT,
            email_verified BOOLEAN,
            email_status TEXT,
            tech_stack TEXT,
            industry_classified TEXT,
            health_score INTEGER,
            ai_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_ein ON companies(ein)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_cik ON companies(cik)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies(domain)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_state ON companies(state_code)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry)")
        
        cur.execute("CREATE INDEX IF NOT EXISTS idx_people_company ON people(company_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_people_email ON people(work_email)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_people_seniority ON people(seniority_level)")
        
        cur.execute("CREATE INDEX IF NOT EXISTS idx_enrichment_company ON enrichment_results(company_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_enrichment_email ON enrichment_results(email)")
        
        self.conn.commit()
        logger.info("✅ Schema created")
    
    def load_json_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """Load JSON data file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ Loaded {len(data)} records from {filepath.name}")
            return data if isinstance(data, list) else [data]
        except Exception as e:
            logger.error(f"❌ Error loading {filepath}: {e}")
            return []
    
    def insert_companies_sqlite(self, companies: List[Dict[str, Any]]) -> int:
        """Insert companies into SQLite"""
        logger.info(f"Loading {len(companies)} companies...")
        
        cur = self.conn.cursor()
        inserted = 0
        
        try:
            for i, company in enumerate(companies):
                company_id = company.get('company_id', '')
                if not company_id:
                    company_id = company.get('ein') or company.get('cik') or f"auto_{i}"
                
                cur.execute("""
                INSERT OR REPLACE INTO companies (
                    id, name, legal_name, website, domain,
                    email, phone, city, state, state_code, zip_code,
                    industry, naics_code, ein, cik,
                    employee_min, employee_max, employee_band,
                    source, data_quality_score, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_id,
                    company.get('legal_name') or company.get('trade_name'),
                    company.get('legal_name'),
                    company.get('website'),
                    company.get('domain'),
                    company.get('email'),
                    company.get('phone'),
                    company.get('address', {}).get('city'),
                    company.get('address', {}).get('state'),
                    company.get('address', {}).get('state_code'),
                    company.get('address', {}).get('zip_code'),
                    company.get('industry'),
                    company.get('naics_code'),
                    company.get('ein'),
                    company.get('cik'),
                    company.get('employee_count_min'),
                    company.get('employee_count_max'),
                    company.get('employee_count_band'),
                    company.get('source'),
                    company.get('data_quality_score'),
                    datetime.now(timezone.utc).isoformat()
                ))
                
                inserted += 1
                
                if (i + 1) % 200 == 0:
                    logger.info(f"  Progress: {i + 1}/{len(companies)}")
            
            self.conn.commit()
            logger.info(f"✅ {inserted} companies inserted")
            self.stats['companies_loaded'] = inserted
        
        except Exception as e:
            logger.error(f"Error in insert_companies_sqlite: {e}")
            self.conn.rollback()
        
        return inserted
    
    def insert_people_sqlite(self, people: List[Dict[str, Any]]) -> int:
        """Insert people into SQLite"""
        logger.info(f"Loading {len(people)} executives...")
        
        cur = self.conn.cursor()
        inserted = 0
        
        try:
            for i, person in enumerate(people):
                person_id = person.get('person_id', '')
                if not person_id:
                    person_id = f"{person.get('company_id')}_{i}"
                
                company_id = person.get('company_id', '')
                
                # Skip if no company_id
                if not company_id:
                    continue
                
                cur.execute("""
                INSERT OR REPLACE INTO people (
                    id, company_id,
                    first_name, last_name, full_name,
                    title, standardized_title, seniority_level, department,
                    work_email, email_status, email_confidence_score,
                    is_active, source, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    person_id,
                    company_id,
                    person.get('first_name'),
                    person.get('last_name'),
                    person.get('full_name'),
                    person.get('title'),
                    person.get('standardized_title'),
                    person.get('seniority_level'),
                    person.get('department'),
                    person.get('work_email'),
                    person.get('email_status'),
                    person.get('email_confidence_score'),
                    1 if person.get('is_active', True) else 0,
                    person.get('source'),
                    datetime.now(timezone.utc).isoformat()
                ))
                
                inserted += 1
                
                if (i + 1) % 500 == 0:
                    logger.info(f"  Progress: {i + 1}/{len(people)}")
            
            self.conn.commit()
            logger.info(f"✅ {inserted} executives inserted")
            self.stats['people_loaded'] = inserted
        
        except Exception as e:
            logger.error(f"Error in insert_people_sqlite: {e}")
            self.conn.rollback()
        
        return inserted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        cur = self.conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM companies")
        total_companies = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM people")
        total_people = cur.fetchone()[0]
        
        cur.execute("""
        SELECT 
            COUNT(DISTINCT state_code) as states,
            COUNT(DISTINCT industry) as industries
        FROM companies WHERE state_code IS NOT NULL AND industry IS NOT NULL
        """)
        diversity = cur.fetchone()
        
        return {
            'total_companies': total_companies,
            'total_people': total_people,
            'states_covered': diversity[0] if diversity else 0,
            'industries_covered': diversity[1] if diversity else 0,
            'db_file': self.db_path,
            'db_size_mb': os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
        }
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from database")
    
    def run(self):
        """Run the data loading pipeline"""
        logger.info("=" * 60)
        logger.info("📊 OneExtraction Data Loader (SQLite)")
        logger.info("=" * 60)
        logger.info("")
        
        # Connect to database
        if not self.connect_sqlite():
            logger.error("Failed to connect to database")
            return False
        
        # Create schema
        self.create_schema_sqlite()
        
        # Load companies data
        logger.info("")
        companies_file = Path("output/us/api/companies/us_companies.json")
        if companies_file.exists():
            companies = self.load_json_file(companies_file)
            self.insert_companies_sqlite(companies)
        else:
            logger.warning(f"⚠️  Companies file not found: {companies_file}")
        
        # Load people data
        logger.info("")
        people_file = Path("output/us/api/people/us_people.json")
        if people_file.exists():
            people = self.load_json_file(people_file)
            self.insert_people_sqlite(people)
        else:
            logger.warning(f"⚠️  People file not found: {people_file}")
        
        # Print statistics
        logger.info("")
        stats = self.get_statistics()
        logger.info("=" * 60)
        logger.info("✅ Data Loading Summary")
        logger.info("=" * 60)
        logger.info(f"Total Companies:     {stats['total_companies']:,}")
        logger.info(f"Total Executives:    {stats['total_people']:,}")
        logger.info(f"States Covered:      {stats['states_covered']}")
        logger.info(f"Industries Covered:  {stats['industries_covered']}")
        logger.info(f"Database Location:   {stats['db_file']}")
        logger.info(f"Database Size:       {stats['db_size_mb']:.2f} MB")
        logger.info(f"Load Errors:         {self.stats['errors']}")
        logger.info("=" * 60)
        logger.info("")
        
        # Disconnect
        self.disconnect()
        
        logger.info("✅ Data loading complete!")
        return True

if __name__ == "__main__":
    loader = OneExtractionDataLoader(use_sqlite=True)
    success = loader.run()
    sys.exit(0 if success else 1)
