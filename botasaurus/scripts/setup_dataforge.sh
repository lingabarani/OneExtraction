#!/bin/bash
# OneExtraction Dataforge Setup Script
# Installs and configures Dataforge for email extraction and enrichment

set -e

echo "========================================="
echo "🔧 OneExtraction Dataforge Setup"
echo "========================================="

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "  Python: $python_version"

if ! command -v python3.9 &> /dev/null && ! command -v python3.10 &> /dev/null && ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.9+ required"
    exit 1
fi

# Create virtual environment (optional but recommended)
echo "✓ Setting up Python environment..."
if [ ! -d "venv" ]; then
    python -m venv venv
    echo "  Created venv/"
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Dataforge
echo "✓ Installing forge-enrichment..."
pip install forge-enrichment==2.0.0

# Verify installation
echo "✓ Verifying Dataforge installation..."
forge --version

# Create config directory
echo "✓ Creating configuration directory..."
mkdir -p config

# Create Dataforge config
cat > config/forge_config.yaml << 'EOF'
# Dataforge Configuration for OneExtraction
# This configures email extraction, tech detection, and AI enrichment

database:
  host: ${FORGE_DB_HOST:-localhost}
  port: ${FORGE_DB_PORT:-5432}
  user: ${FORGE_DB_USER:-forge}
  password: ${FORGE_DB_PASSWORD:-oneextraction_secure_2026}
  database: ${FORGE_DB_NAME:-oneextraction}
  pool_size: 10
  max_overflow: 20

enrichment:
  # Email extraction using 6-layer detection
  email_extraction: true
  
  # Tech stack detection (30+ technologies)
  tech_detection: true
  
  # Industry classification (requires Ollama if local_ai enabled)
  industry_classification: true
  
  # Health scoring
  health_scoring: true
  
  # Skip already enriched records
  skip_enriched: true

workers:
  # Web scraping workers (email extraction, tech detection)
  web_scraping: 4
  
  # SMTP verification workers
  smtp_verification: 10
  
  # AI enrichment workers
  ai_enrichment: 2

# Local AI configuration (requires Ollama)
ai:
  enabled: false  # Set to true if Ollama is running
  provider: ollama
  model: gemma4:26b
  base_url: http://localhost:11434
  temperature: 0.7
  
  # AI enrichment tasks
  summarize_businesses: true
  classify_industry: true
  calculate_health_score: true
  identify_pain_points: true

# Processing configuration
processing:
  batch_size: 100
  checkpoint_interval: 100
  checkpoint_dir: ./checkpoints
  
  # Rollback on critical errors
  rollback_on_error: true
  
  # Rate limiting
  rate_limit_requests_per_second: 10
  rate_limit_concurrent: 20

# SMTP verification configuration
smtp:
  from_email: ${FORGE_SMTP_FROM:-noreply@oneextraction.io}
  ehlo_domain: ${FORGE_SMTP_EHLO:-oneextraction.io}
  timeout: 10
  retry_count: 2

# Proxy configuration (optional, for SMTP at scale)
proxy: null
  # host: ${SMTP_PROXY_HOST}
  # port: ${SMTP_PROXY_PORT}
  # username: ${SMTP_PROXY_USERNAME}
  # password: ${SMTP_PROXY_PASSWORD}

# Output configuration
output:
  format: json
  directory: ./output/us/api
  include_validation_details: true

# Logging
logging:
  level: INFO
  file: ./output/us/api/logs/dataforge.log
  console: true

# External APIs (optional)
apis:
  sam_gov_key: ${SAM_GOV_API_KEY}
  anthropic_key: ${ANTHROPIC_API_KEY}

# Monitoring
monitoring:
  enabled: true
  health_check_interval: 60
  metrics_port: 8003
EOF

echo "✓ Created config/forge_config.yaml"

# Create requirements file for reproducibility
cat > requirements_dataforge.txt << 'EOF'
forge-enrichment==2.0.0
psycopg2-binary>=2.9
aiohttp>=3.9
aiolimiter>=1.1
httpx>=0.25
dnspython>=2.4
anthropic>=0.25
duckdb>=1.0
fastapi>=0.115
uvicorn>=0.30
jinja2>=3.1
python-multipart>=0.0.9
sse-starlette>=2.0
requests>=2.31
EOF

echo "✓ Created requirements_dataforge.txt"

# Create Dataforge startup script
cat > scripts/start_dataforge.sh << 'EOF'
#!/bin/bash
# Start Dataforge enrichment pipeline

set -e

# Load environment
if [ -f .env.integration ]; then
    export $(cat .env.integration | grep -v '^#' | xargs)
fi

# Start email extraction track
echo "🚀 Starting Dataforge email extraction..."
echo "   Workers: $FORGE_WORKERS"
echo "   Database: $FORGE_DB_HOST:$FORGE_DB_PORT/$FORGE_DB_NAME"

forge enrich \
    --mode email \
    --workers ${FORGE_WORKERS:-4} \
    --resume \
    --config config/forge_config.yaml

echo "✅ Dataforge enrichment complete"
EOF

chmod +x scripts/start_dataforge.sh
echo "✓ Created scripts/start_dataforge.sh"

# Create Dataforge monitoring script
cat > scripts/dataforge_status.sh << 'EOF'
#!/bin/bash
# Check Dataforge status and database stats

echo "========================================="
echo "📊 Dataforge Status"
echo "========================================="

# Load environment
if [ -f .env.integration ]; then
    export $(cat .env.integration | grep -v '^#' | xargs)
fi

# Connect to database
PGPASSWORD="${FORGE_DB_PASSWORD}" psql -h "${FORGE_DB_HOST}" -U "${FORGE_DB_USER}" -d "${FORGE_DB_NAME}" << SQL
-- Display enrichment statistics
SELECT 
    'Total Companies' as metric,
    COUNT(*) as count
FROM businesses
UNION ALL
SELECT 'Companies with Email', COUNT(*) FROM businesses WHERE email IS NOT NULL
UNION ALL
SELECT 'Email Verification Status', COUNT(*) FROM businesses WHERE email_validation_status IS NOT NULL
UNION ALL
SELECT 'Verified Safe', COUNT(*) FROM businesses WHERE email_validation_status = 'VERIFIED_SAFE'
UNION ALL
SELECT 'With Tech Stack', COUNT(*) FROM businesses WHERE tech_stack IS NOT NULL
UNION ALL
SELECT 'With Industry', COUNT(*) FROM businesses WHERE industry IS NOT NULL
UNION ALL
SELECT 'With Health Score', COUNT(*) FROM businesses WHERE health_score IS NOT NULL;

-- Display recent enrichment jobs
SELECT job_name, job_type, status, processed_records, completed_at 
FROM enrichment_jobs 
ORDER BY created_at DESC 
LIMIT 5;
SQL

EOF

chmod +x scripts/dataforge_status.sh
echo "✓ Created scripts/dataforge_status.sh"

echo ""
echo "========================================="
echo "✅ Dataforge Setup Complete!"
echo "========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Start Docker containers:"
echo "   docker-compose up -d"
echo ""
echo "2. Verify database connection:"
echo "   ./scripts/dataforge_status.sh"
echo ""
echo "3. Load OneExtraction data:"
echo "   python scripts/dataforge_loader.py"
echo ""
echo "4. Start enrichment:"
echo "   ./scripts/start_dataforge.sh"
echo ""
echo "📖 Documentation:"
echo "   - Dataforge: https://github.com/ghealysr/forge"
echo "   - Config: config/forge_config.yaml"
echo "   - Monitor: ./scripts/dataforge_status.sh"
echo ""
