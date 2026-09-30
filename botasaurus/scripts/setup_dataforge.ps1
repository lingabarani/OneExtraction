# OneExtraction Dataforge Setup Script (PowerShell)
# Installs and configures Dataforge for email extraction and enrichment

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🔧 OneExtraction Dataforge Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "✓ Checking Python version..." -ForegroundColor Green
$pythonVersion = python --version 2>&1
Write-Host "  Python: $pythonVersion" -ForegroundColor Gray

# Upgrade pip
Write-Host "✓ Upgrading pip..." -ForegroundColor Green
pip install --upgrade pip setuptools wheel | Out-Null

# Install Dataforge
Write-Host "✓ Installing forge-enrichment..." -ForegroundColor Green
pip install forge-enrichment==2.0.0

# Verify installation
Write-Host "✓ Verifying Dataforge installation..." -ForegroundColor Green
forge --version

# Create config directory
Write-Host "✓ Creating configuration directory..." -ForegroundColor Green
New-Item -ItemType Directory -Path "config" -Force | Out-Null

# Create Dataforge config
$forgeConfig = @"
# Dataforge Configuration for OneExtraction
database:
  host: localhost
  port: 5432
  user: forge
  password: oneextraction_secure_2026
  database: oneextraction
  pool_size: 10
  max_overflow: 20

enrichment:
  email_extraction: true
  tech_detection: true
  industry_classification: true
  health_scoring: true
  skip_enriched: true

workers:
  web_scraping: 4
  smtp_verification: 10
  ai_enrichment: 2

ai:
  enabled: false
  provider: ollama
  model: gemma4:26b
  base_url: http://localhost:11434
  temperature: 0.7
  summarize_businesses: true
  classify_industry: true
  calculate_health_score: true
  identify_pain_points: true

processing:
  batch_size: 100
  checkpoint_interval: 100
  checkpoint_dir: ./checkpoints
  rollback_on_error: true
  rate_limit_requests_per_second: 10
  rate_limit_concurrent: 20

smtp:
  from_email: noreply@oneextraction.io
  ehlo_domain: oneextraction.io
  timeout: 10
  retry_count: 2

output:
  format: json
  directory: ./output/us/api
  include_validation_details: true

logging:
  level: INFO
  file: ./output/us/api/logs/dataforge.log
  console: true

monitoring:
  enabled: true
  health_check_interval: 60
  metrics_port: 8003
"@

Set-Content -Path "config\forge_config.yaml" -Value $forgeConfig
Write-Host "✓ Created config\forge_config.yaml" -ForegroundColor Green

# Create requirements file
$requirements = @"
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
"@

Set-Content -Path "requirements_dataforge.txt" -Value $requirements
Write-Host "✓ Created requirements_dataforge.txt" -ForegroundColor Green

# Create startup batch file for Windows
$batchScript = @"
@echo off
REM Start Dataforge enrichment pipeline

echo Loading environment...
for /f "tokens=*" %%a in ('type .env.integration ^| findstr /v "^#"') do (
    set %%a
)

echo.
echo 🚀 Starting Dataforge email extraction...
echo    Workers: %FORGE_WORKERS%
echo    Database: %FORGE_DB_HOST%:%FORGE_DB_PORT%/%FORGE_DB_NAME%
echo.

forge enrich ^
    --mode email ^
    --workers %FORGE_WORKERS% ^
    --resume ^
    --config config/forge_config.yaml

echo.
echo ✅ Dataforge enrichment complete
pause
"@

Set-Content -Path "scripts\start_dataforge.bat" -Value $batchScript
Write-Host "✓ Created scripts\start_dataforge.bat" -ForegroundColor Green

# Create PowerShell startup script
$psScript = @"
# Start Dataforge enrichment pipeline

# Load environment
if (Test-Path ".env.integration") {
    Get-Content ".env.integration" | Where-Object { `$_ -notmatch "^#" } | ForEach-Object {
        `$name, `$value = `$_ -split "=", 2
        if (`$name -and `$value) {
            Set-Item -Path "env:\`$name" -Value `$value
        }
    }
}

Write-Host "🚀 Starting Dataforge email extraction..." -ForegroundColor Cyan
Write-Host "   Workers: `$env:FORGE_WORKERS"
Write-Host "   Database: `$env:FORGE_DB_HOST:`$env:FORGE_DB_PORT/`$env:FORGE_DB_NAME"
Write-Host ""

forge enrich `
    --mode email `
    --workers `$env:FORGE_WORKERS `
    --resume `
    --config config/forge_config.yaml

Write-Host ""
Write-Host "✅ Dataforge enrichment complete" -ForegroundColor Green
"@

Set-Content -Path "scripts\start_dataforge.ps1" -Value $psScript
Write-Host "✓ Created scripts\start_dataforge.ps1" -ForegroundColor Green

# Create status check script
$statusScript = @"
# Check Dataforge status and database stats

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "📊 Dataforge Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Load environment
if (Test-Path ".env.integration") {
    Get-Content ".env.integration" | Where-Object { `$_ -notmatch "^#" } | ForEach-Object {
        `$name, `$value = `$_ -split "=", 2
        if (`$name -and `$value) {
            Set-Item -Path "env:\`$name" -Value `$value
        }
    }
}

# Try connecting to database
try {
    `$connString = "Host=`$env:FORGE_DB_HOST;Port=`$env:FORGE_DB_PORT;Username=`$env:FORGE_DB_USER;Password=`$env:FORGE_DB_PASSWORD;Database=`$env:FORGE_DB_NAME"
    
    # Using psql if available
    if (Get-Command psql -ErrorAction SilentlyContinue) {
        `$env:PGPASSWORD = `$env:FORGE_DB_PASSWORD
        psql -h `$env:FORGE_DB_HOST -U `$env:FORGE_DB_USER -d `$env:FORGE_DB_NAME -c "
            SELECT 'Total Companies' as metric, COUNT(*) as count FROM businesses
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
        "
    }
    else {
        Write-Host "psql not found. Install PostgreSQL tools to see database stats." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Error connecting to database: `$_" -ForegroundColor Red
}

Write-Host ""
"@

Set-Content -Path "scripts\dataforge_status.ps1" -Value $statusScript
Write-Host "✓ Created scripts\dataforge_status.ps1" -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "✅ Dataforge Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start Docker containers:" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verify database connection:" -ForegroundColor White
Write-Host "   .\scripts\dataforge_status.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Load OneExtraction data:" -ForegroundColor White
Write-Host "   python scripts/dataforge_loader.py" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Start enrichment:" -ForegroundColor White
Write-Host "   .\scripts\start_dataforge.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "   - Dataforge: https://github.com/ghealysr/forge" -ForegroundColor Gray
Write-Host "   - Config: config/forge_config.yaml" -ForegroundColor Gray
Write-Host "   - Monitor: .\scripts\dataforge_status.ps1" -ForegroundColor Gray
Write-Host ""
