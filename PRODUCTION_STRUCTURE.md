# Production-Ready Repository Structure

## Desired Directory Layout

```
OneExtraction/
├── README.md                          # Main project readme
├── IMPLEMENTATION_PLAN.md             # 4-week implementation plan
├── LICENSE                            # Apache 2.0 or MIT
├── .gitignore                         # Production .gitignore
├── .env.example                       # Environment template
│
├── src/                               # Source code
│   ├── __init__.py
│   ├── core/                          # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py               # SQLite/PostgreSQL wrapper
│   │   ├── config.py                 # Configuration management
│   │   └── logger.py                 # Logging setup
│   │
│   ├── pipeline/                      # ETL Pipeline
│   │   ├── __init__.py
│   │   ├── extraction/               # Data extraction
│   │   │   ├── __init__.py
│   │   │   ├── email_extractor.py   # Email extraction
│   │   │   ├── domain_generator.py  # Domain generation
│   │   │   └── web_scraper.py       # Website content scraping
│   │   │
│   │   ├── validation/               # Data validation
│   │   │   ├── __init__.py
│   │   │   ├── email_validator.py   # Email verification
│   │   │   ├── smtp_checker.py      # SMTP validation
│   │   │   └── data_quality.py      # Quality scoring
│   │   │
│   │   ├── enrichment/               # Data enrichment
│   │   │   ├── __init__.py
│   │   │   ├── industry_classifier.py
│   │   │   ├── tech_detector.py
│   │   │   └── rdap_enricher.py
│   │   │
│   │   └── output/                   # Output formatting
│   │       ├── __init__.py
│   │       ├── csv_exporter.py
│   │       ├── json_exporter.py
│   │       └── report_generator.py
│   │
│   ├── models/                        # Data models
│   │   ├── __init__.py
│   │   ├── company.py                # Company model
│   │   ├── person.py                 # Person/Executive model
│   │   └── enrichment.py             # Enrichment result model
│   │
│   ├── connectors/                    # Data source connectors
│   │   ├── __init__.py
│   │   ├── base.py                   # Base connector class
│   │   ├── sec_edgar.py              # SEC EDGAR
│   │   ├── cms_npi.py                # CMS NPI data
│   │   ├── sam_gov.py                # SAM.gov data
│   │   ├── opencorporates.py         # OpenCorporates
│   │   └── pdl_connector.py          # PDL API connector
│   │
│   ├── utils/                         # Utilities
│   │   ├── __init__.py
│   │   ├── text_utils.py             # Text processing
│   │   ├── validators.py             # Validation helpers
│   │   ├── formatters.py             # Data formatting
│   │   └── email_patterns.py         # Email pattern generation
│   │
│   ├── api/                           # API/MCP Server
│   │   ├── __init__.py
│   │   ├── mcp_server.py             # MCP server implementation
│   │   ├── tools.py                  # MCP tools
│   │   └── schemas.py                # API schemas
│   │
│   └── cli/                           # CLI commands
│       ├── __init__.py
│       ├── main.py                   # Main CLI entry
│       ├── extract.py                # Extract command
│       ├── validate.py               # Validate command
│       ├── enrich.py                 # Enrich command
│       └── export.py                 # Export command
│
├── scripts/                           # Standalone scripts
│   ├── setup_database.py             # Database initialization
│   ├── load_data.py                  # Data loading
│   ├── run_pipeline.py               # Full pipeline execution
│   ├── batch_process.py              # Batch processing
│   └── cleanup.py                    # Cleanup utilities
│
├── tests/                             # Unit & integration tests
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── unit/
│   │   ├── test_email_extractor.py
│   │   ├── test_email_validator.py
│   │   ├── test_domain_generator.py
│   │   └── test_models.py
│   ├── integration/
│   │   ├── test_pipeline.py
│   │   ├── test_database.py
│   │   └── test_api.py
│   └── fixtures/
│       └── sample_data.py
│
├── config/                            # Configuration files
│   ├── development.yaml              # Dev config
│   ├── production.yaml               # Prod config
│   ├── testing.yaml                  # Test config
│   └── sources.yaml                  # Data source configs
│
├── data/                              # Data directory
│   ├── raw/                          # Raw input data
│   │   ├── us_companies/
│   │   └── us_executives/
│   ├── processed/                    # Processed data
│   │   └── us_companies.db           # SQLite database
│   └── exports/                      # Export outputs
│       ├── verified_emails.csv
│       ├── companies_by_industry/
│       └── reports/
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API.md                        # API documentation
│   ├── SETUP.md                      # Setup guide
│   ├── USAGE.md                      # Usage guide
│   ├── DEVELOPMENT.md                # Development guide
│   ├── DEPLOYMENT.md                 # Deployment guide
│   └── TROUBLESHOOTING.md            # Troubleshooting
│
├── docker/                            # Docker configuration
│   ├── Dockerfile                    # Main application image
│   ├── Dockerfile.postgres           # PostgreSQL image
│   ├── docker-compose.yml            # Multi-container setup
│   └── .dockerignore
│
├── .github/                           # GitHub config
│   ├── workflows/
│   │   ├── tests.yml                 # Test workflow
│   │   ├── build.yml                 # Build workflow
│   │   └── deploy.yml                # Deploy workflow
│   └── ISSUE_TEMPLATE/
│
├── requirements.txt                   # Python dependencies
├── setup.py                           # Setup configuration
├── pyproject.toml                     # Python project config
├── pytest.ini                         # Pytest configuration
├── Makefile                           # Make commands
└── .env.example                       # Environment template

```

## File Organization Rules

### Keep ✅
- Source code in `src/`
- Tests in `tests/`
- Configuration files in `config/`
- Documentation in `docs/`
- Scripts in `scripts/`
- Docker setup in `docker/`
- CI/CD workflows in `.github/`

### Remove ❌
- PDFs (.docx files)
- Excel files (.xlsx)
- Root-level temporary files
- Botasaurus project files (if using OneExtraction only)
- Cache directories (.pytest_cache, __pycache__)
- Generated reports in root
- Test outputs

### Gitignore Entries
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local

# Data (optional, use for sensitive data)
data/raw/
data/processed/
data/exports/private/

# Build
dist/
build/
*.egg-info/
```

## Migration Steps

1. Create new directory structure
2. Move source files to `src/`
3. Move scripts to `scripts/`
4. Move tests to `tests/`
5. Move config to `config/`
6. Move data to `data/`
7. Create documentation in `docs/`
8. Create docker configuration
9. Remove temporary files
10. Update .gitignore
11. Commit and push

