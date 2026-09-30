#!/usr/bin/env python3
"""
Week 1 Setup Verification Script
Verifies that all infrastructure is properly set up
"""

import sqlite3
import os
import sys
from pathlib import Path
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class Week1Verifier:
    """Verify Week 1 setup completion"""
    
    def __init__(self):
        self.checks = {}
        self.db_path = Path("output/us/api/oneextraction.db")
    
    def check_files(self):
        """Check that all required files exist"""
        logger.info("📋 Checking required files...")
        
        required_files = [
            ("Database", self.db_path),
            ("Docker Compose", Path("docker-compose.yml")),
            ("DB Init Schema", Path("init_db.sql")),
            ("Environment Config", Path(".env.integration")),
            ("Data Loader", Path("scripts/simple_data_loader.py")),
            ("Data Cleaner", Path("scripts/clean_json_data.py")),
            ("Dataforge Guide", Path("scripts/dataforge_integration_guide.md")),
            ("Week 1 Checklist", Path("WEEK1_SETUP_CHECKLIST.md")),
        ]
        
        all_exist = True
        for name, path in required_files:
            exists = path.exists()
            status = "✅" if exists else "❌"
            logger.info(f"  {status} {name}: {path}")
            self.checks[name] = exists
            if not exists:
                all_exist = False
        
        return all_exist
    
    def check_database(self):
        """Check database content"""
        logger.info("\n📊 Checking database content...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Check tables exist
            cur.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
            """)
            tables = cur.fetchall()
            logger.info(f"  ✅ Tables: {len(tables)}")
            for table in tables:
                logger.info(f"     - {table[0]}")
            
            # Check companies
            cur.execute("SELECT COUNT(*) FROM companies")
            company_count = cur.fetchone()[0]
            logger.info(f"  {'✅' if company_count == 1185 else '❌'} Companies: {company_count:,} (expected 1,185)")
            self.checks['Companies Count'] = company_count == 1185
            
            # Check people
            cur.execute("SELECT COUNT(*) FROM people")
            people_count = cur.fetchone()[0]
            logger.info(f"  {'✅' if people_count == 2370 else '❌'} Executives: {people_count:,} (expected 2,370)")
            self.checks['Executives Count'] = people_count == 2370
            
            # Check indexes
            cur.execute("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
            """)
            index_count = cur.fetchone()[0]
            logger.info(f"  ✅ Indexes: {index_count}")
            
            # Check data diversity
            cur.execute("SELECT COUNT(DISTINCT state_code) FROM companies WHERE state_code IS NOT NULL")
            states = cur.fetchone()[0]
            logger.info(f"  ✅ States covered: {states}")
            
            cur.execute("SELECT COUNT(DISTINCT industry) FROM companies WHERE industry IS NOT NULL")
            industries = cur.fetchone()[0]
            logger.info(f"  ✅ Industries covered: {industries}")
            
            # Check database file size
            db_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            logger.info(f"  ✅ Database size: {db_size_mb:.2f} MB")
            
            conn.close()
            return company_count == 1185 and people_count == 2370
        
        except Exception as e:
            logger.error(f"  ❌ Database check failed: {e}")
            return False
    
    def check_json_data(self):
        """Check that JSON data files are valid"""
        logger.info("\n📁 Checking JSON data files...")
        
        files_ok = True
        
        # Check companies JSON
        companies_file = Path("output/us/api/companies/us_companies.json")
        if companies_file.exists():
            try:
                with open(companies_file) as f:
                    companies = json.load(f)
                logger.info(f"  ✅ Companies JSON: {len(companies):,} records")
                self.checks['Companies JSON'] = len(companies) == 1185
            except Exception as e:
                logger.error(f"  ❌ Companies JSON invalid: {e}")
                files_ok = False
        else:
            logger.warning(f"  ⚠️  Companies JSON not found")
        
        # Check people JSON
        people_file = Path("output/us/api/people/us_people.json")
        if people_file.exists():
            try:
                with open(people_file) as f:
                    people = json.load(f)
                logger.info(f"  ✅ People JSON: {len(people):,} records")
                self.checks['People JSON'] = len(people) == 2370
            except Exception as e:
                logger.error(f"  ❌ People JSON invalid: {e}")
                files_ok = False
        else:
            logger.warning(f"  ⚠️  People JSON not found")
        
        return files_ok
    
    def check_config(self):
        """Check configuration files"""
        logger.info("\n⚙️  Checking configuration...")
        
        config_ok = True
        
        # Check .env.integration
        env_file = Path(".env.integration")
        if env_file.exists():
            with open(env_file) as f:
                content = f.read()
            
            required_keys = [
                "FORGE_DB_HOST",
                "FORGE_DB_PORT",
                "FORGE_DB_USER",
                "FORGE_DB_PASSWORD",
                "FORGE_DB_NAME"
            ]
            
            missing = [k for k in required_keys if k not in content]
            
            if not missing:
                logger.info(f"  ✅ .env.integration configured")
                self.checks['.env.integration'] = True
            else:
                logger.warning(f"  ⚠️  Missing keys: {', '.join(missing)}")
                self.checks['.env.integration'] = False
                config_ok = False
        else:
            logger.warning(f"  ⚠️  .env.integration not found")
            config_ok = False
        
        # Check docker-compose
        docker_file = Path("docker-compose.yml")
        if docker_file.exists():
            with open(docker_file) as f:
                content = f.read()
            
            has_postgres = "postgres" in content
            has_email_validator = "email-validator" in content
            
            if has_postgres and has_email_validator:
                logger.info(f"  ✅ docker-compose.yml configured")
                self.checks['docker-compose.yml'] = True
            else:
                logger.warning(f"  ⚠️  Missing services")
                self.checks['docker-compose.yml'] = False
                config_ok = False
        else:
            logger.warning(f"  ⚠️  docker-compose.yml not found")
            config_ok = False
        
        return config_ok
    
    def run_verification(self):
        """Run all verification checks"""
        logger.info("=" * 60)
        logger.info("🔍 WEEK 1 SETUP VERIFICATION")
        logger.info("=" * 60)
        logger.info("")
        
        # Run all checks
        files_ok = self.check_files()
        config_ok = self.check_config()
        json_ok = self.check_json_data()
        db_ok = self.check_database()
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 60)
        
        passed = sum(1 for v in self.checks.values() if v is True)
        failed = sum(1 for v in self.checks.values() if v is False)
        
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        
        all_ok = files_ok and config_ok and json_ok and db_ok
        
        logger.info("")
        if all_ok:
            logger.info("🎉 WEEK 1 VERIFICATION PASSED!")
            logger.info("")
            logger.info("✅ Infrastructure setup complete")
            logger.info("✅ Dataforge configured")
            logger.info("✅ Data loaded into database")
            logger.info("")
            logger.info("Ready for Week 2: Email Extraction & Validation")
            logger.info("")
            return 0
        else:
            logger.warning("⚠️  SOME CHECKS FAILED")
            logger.warning("Please review the errors above")
            logger.info("")
            return 1

if __name__ == "__main__":
    verifier = Week1Verifier()
    exit_code = verifier.run_verification()
    sys.exit(exit_code)
