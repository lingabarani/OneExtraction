#!/usr/bin/env python3
"""
Batch Email Validator
Validates extracted emails using multiple methods
"""

import sqlite3
import dns.resolver
import socket
import smtplib
import time
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailValidator:
    """Validate emails using multiple methods"""
    
    def __init__(self, db_path: str = "output/us/api/oneextraction.db"):
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'total_validated': 0,
            'valid_syntax': 0,
            'valid_mx': 0,
            'verified_safe': 0,
            'risky': 0,
            'invalid': 0,
            'errors': 0
        }
        
        # Disposable email domains
        self.disposable_domains = {
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'temp-mail.org', 'throwaway.email',
            'maildrop.cc', 'sharklasers.com'
        }
        
        # Common role accounts
        self.role_accounts = {
            'noreply', 'no-reply', 'donotreply', 'info', 'contact',
            'support', 'help', 'admin', 'webmaster', 'postmaster'
        }
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_emails_to_validate(self, limit: int = 1000) -> List[Dict]:
        """Get extracted emails that haven't been validated"""
        cur = self.conn.cursor()
        
        # First, try to get emails from enrichment_results with EXTRACTED status
        cur.execute("""
        SELECT er.company_id, er.email, c.domain
        FROM enrichment_results er
        JOIN companies c ON er.company_id = c.id
        WHERE er.email IS NOT NULL
        AND er.email_status = 'EXTRACTED'
        AND er.email_verified = 0
        LIMIT ?
        """, (limit,))
        
        emails = []
        for row in cur.fetchall():
            emails.append({
                'company_id': row['company_id'],
                'email': row['email'],
                'domain': row['domain']
            })
        
        # If no EXTRACTED emails, fall back to companies with emails
        if not emails:
            cur.execute("""
            SELECT c.id, c.email, c.domain
            FROM companies c
            WHERE c.email IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 FROM enrichment_results 
                WHERE company_id = c.id AND email = c.email
            )
            LIMIT ?
            """, (limit,))
            
            for row in cur.fetchall():
                emails.append({
                    'company_id': row['id'],
                    'email': row['email'],
                    'domain': row['domain']
                })
        
        return emails
    
    def validate_email_syntax(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def is_disposable_email(self, email: str) -> bool:
        """Check if email is from disposable domain"""
        domain = email.split('@')[1].lower()
        return domain in self.disposable_domains
    
    def is_role_account(self, email: str) -> bool:
        """Check if email is a role account"""
        local = email.split('@')[0].lower()
        return any(role in local for role in self.role_accounts)
    
    def check_mx_records(self, email: str) -> bool:
        """Check if MX records exist for domain"""
        try:
            domain = email.split('@')[1]
            mx_records = dns.resolver.resolve(domain, 'MX')
            return len(mx_records) > 0
        except Exception:
            return False
    
    def check_smtp_connection(self, email: str) -> Optional[str]:
        """
        Check if SMTP server accepts the email
        Returns: 'safe', 'risky', or None
        """
        try:
            domain = email.split('@')[1]
            
            # Get MX records
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_host = str(mx_records[0].exchange)
            
            # Connect to SMTP server
            with smtplib.SMTP(mx_host, 25, timeout=10) as server:
                server.set_debuglevel(0)
                server.ehlo()
                
                # Check if email exists using RCPT TO
                code, message = server.rcpt_to(email)
                
                if code == 250:
                    return 'safe'  # Email accepted
                elif code == 550:
                    return 'invalid'  # User unknown
                else:
                    return 'risky'  # Uncertain
        
        except Exception as e:
            logger.debug(f"SMTP check failed for {email}: {e}")
            return None
    
    def validate_email(self, email: str, domain: str = "") -> Dict:
        """Validate email using multiple methods"""
        result = {
            'email': email,
            'syntax_valid': False,
            'mx_valid': False,
            'smtp_verified': None,
            'is_disposable': False,
            'is_role_account': False,
            'status': 'INVALID',
            'confidence': 0
        }
        
        # 1. Syntax check
        if self.validate_email_syntax(email):
            result['syntax_valid'] = True
            result['confidence'] += 20
        else:
            result['status'] = 'INVALID'
            return result
        
        # 2. Disposable check
        result['is_disposable'] = self.is_disposable_email(email)
        if result['is_disposable']:
            result['status'] = 'RISKY'
            result['confidence'] += 10
            return result
        
        # 3. Role account check
        result['is_role_account'] = self.is_role_account(email)
        if result['is_role_account']:
            result['confidence'] += 10
        else:
            result['confidence'] += 20
        
        # 4. MX record check
        if self.check_mx_records(email):
            result['mx_valid'] = True
            result['confidence'] += 20
        else:
            result['status'] = 'INVALID'
            return result
        
        # 5. SMTP verification (if available)
        smtp_result = self.check_smtp_connection(email)
        if smtp_result:
            result['smtp_verified'] = (smtp_result == 'safe')
            if smtp_result == 'safe':
                result['status'] = 'VERIFIED_SAFE'
                result['confidence'] += 30
            elif smtp_result == 'risky':
                result['status'] = 'RISKY'
                result['confidence'] += 15
            else:
                result['status'] = 'INVALID'
        else:
            # Assume safe if MX valid and syntax good
            if result['mx_valid'] and result['syntax_valid']:
                result['status'] = 'LIKELY_VALID'
                result['confidence'] += 25
        
        # Cap confidence at 100
        result['confidence'] = min(100, result['confidence'])
        
        return result
    
    def save_validation_result(self, company_id: str, email_data: Dict):
        """Save validation result to database"""
        cur = self.conn.cursor()
        
        try:
            # Update company if status is good
            if email_data['status'] in ['VERIFIED_SAFE', 'LIKELY_VALID']:
                cur.execute("""
                UPDATE companies
                SET updated_at = ?
                WHERE id = ?
                """, (
                    datetime.now(timezone.utc).isoformat(),
                    company_id
                ))
            
            # Save enrichment result
            cur.execute("""
            INSERT OR REPLACE INTO enrichment_results (
                id, company_id, email, email_verified, email_status
            ) VALUES (?, ?, ?, ?, ?)
            """, (
                f"{company_id}_validated",
                company_id,
                email_data['email'],
                email_data['status'] in ['VERIFIED_SAFE', 'LIKELY_VALID'],
                email_data['status']
            ))
            
            self.conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Error saving validation for {company_id}: {e}")
            return False
    
    def run_validation(self, limit: int = 1000, batch_size: int = 50):
        """Run batch email validation"""
        logger.info("=" * 60)
        logger.info("✉️  Email Validation Pipeline")
        logger.info("=" * 60)
        logger.info("")
        
        self.connect()
        
        try:
            emails = self.get_emails_to_validate(limit)
            total = len(emails)
            
            logger.info(f"Validating {total} emails...")
            logger.info("")
            
            for i, item in enumerate(emails):
                try:
                    # Validate email
                    result = self.validate_email(item['email'], item['domain'])
                    
                    # Save result
                    self.save_validation_result(item['company_id'], result)
                    
                    # Update stats
                    self.stats['total_validated'] += 1
                    
                    if result['syntax_valid']:
                        self.stats['valid_syntax'] += 1
                    
                    if result['mx_valid']:
                        self.stats['valid_mx'] += 1
                    
                    if result['status'] == 'VERIFIED_SAFE':
                        self.stats['verified_safe'] += 1
                    elif result['status'] == 'RISKY':
                        self.stats['risky'] += 1
                    elif result['status'] == 'INVALID':
                        self.stats['invalid'] += 1
                    
                    # Progress indicator
                    if (i + 1) % batch_size == 0:
                        logger.info(f"  Progress: {i + 1}/{total}")
                        # Rate limiting between batches
                        time.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error validating {item['email']}: {e}")
                    self.stats['errors'] += 1
                    continue
            
            # Print summary
            logger.info("")
            logger.info("=" * 60)
            logger.info("✅ Validation Summary")
            logger.info("=" * 60)
            logger.info(f"Total validated:          {self.stats['total_validated']:,}")
            logger.info(f"Valid syntax:             {self.stats['valid_syntax']:,}")
            logger.info(f"Valid MX records:         {self.stats['valid_mx']:,}")
            logger.info(f"Verified safe:            {self.stats['verified_safe']:,}")
            logger.info(f"Risky emails:             {self.stats['risky']:,}")
            logger.info(f"Invalid emails:           {self.stats['invalid']:,}")
            logger.info(f"Errors:                   {self.stats['errors']}")
            logger.info("")
            
            if self.stats['total_validated'] > 0:
                safe_rate = 100 * self.stats['verified_safe'] / self.stats['total_validated']
                logger.info(f"Safe email rate:          {safe_rate:.1f}%")
            
            logger.info("=" * 60)
        
        finally:
            self.disconnect()

if __name__ == "__main__":
    validator = EmailValidator()
    validator.run_validation(limit=1000, batch_size=50)
