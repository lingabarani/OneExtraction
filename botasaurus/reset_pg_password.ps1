# reset_pg_password.ps1
# Run this in PowerShell AS ADMINISTRATOR to reset postgres password
# Right-click PowerShell → "Run as Administrator", then paste this script

$PG_BIN  = "C:\Program Files\PostgreSQL\18\bin"
$PG_DATA = "C:\Program Files\PostgreSQL\18\data"
$NEW_PWD = "oneextraction2026"

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Password Reset for OneExtraction"    -ForegroundColor Cyan  
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop PostgreSQL service
Write-Host "1. Stopping PostgreSQL service..." -ForegroundColor Yellow
Stop-Service -Name "postgresql-x64-18" -Force
Start-Sleep -Seconds 2
Write-Host "   Service stopped." -ForegroundColor Green

# Step 2: Start postgres in single-user mode to reset password
Write-Host "2. Resetting password to: $NEW_PWD" -ForegroundColor Yellow
$cmd = "ALTER USER postgres WITH PASSWORD '$NEW_PWD';"
echo $cmd | & "$PG_BIN\postgres.exe" --single -D "$PG_DATA" postgres
Write-Host "   Password updated." -ForegroundColor Green

# Step 3: Restart service
Write-Host "3. Restarting PostgreSQL service..." -ForegroundColor Yellow
Start-Service -Name "postgresql-x64-18"
Start-Sleep -Seconds 3
Write-Host "   Service started." -ForegroundColor Green

# Step 4: Verify
Write-Host "4. Testing connection..." -ForegroundColor Yellow
$env:PGPASSWORD = $NEW_PWD
$result = & "$PG_BIN\psql.exe" -U postgres -h 127.0.0.1 -p 5432 -d postgres -c "SELECT current_user, version();" 2>&1
Write-Host $result

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  DONE! New password: $NEW_PWD"                   -ForegroundColor Green
Write-Host "  Now run:"                                        -ForegroundColor White
Write-Host "  cd botasaurus"                                   -ForegroundColor White
Write-Host "  python setup_postgres.py --password $NEW_PWD"   -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
