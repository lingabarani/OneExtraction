"""
Comprehensive tests for separated API vs Public-Directory Scraping ingestion channels.
Verifies complete physical separation, schema compliance, logging isolation, and optional combined golden resolution.
"""

import json
from pathlib import Path
import pytest
from mexico_b2b.pipeline.ingestion import IngestionPipeline
from mexico_b2b.config.settings import settings


@pytest.fixture
def pipeline():
    return IngestionPipeline()


def test_api_pipeline_isolation(pipeline):
    """Verifies that the API pipeline produces only API data with official_api source types."""
    results = pipeline.run_api_pipeline(limit=5, dry_run=False, sample=True)

    assert results["category"] == "api"
    assert len(results["companies"]) > 0
    assert len(results["people"]) > 0

    # 1. Output files must exist in output/api/
    comp_file = settings.API_COMPANIES_DIR / "api_companies.json"
    people_file = settings.API_PEOPLE_DIR / "api_people.json"
    summary_file = settings.API_LOGS_DIR / "api_summary.json"
    report_file = settings.API_REPORTS_DIR / "api_validation_report.json"
    ingestion_log = settings.API_LOGS_DIR / "api_ingestion.log"
    validation_log = settings.API_LOGS_DIR / "api_validation.log"

    assert comp_file.exists()
    assert people_file.exists()
    assert summary_file.exists()
    assert report_file.exists()
    assert ingestion_log.exists()
    assert validation_log.exists()

    # 2. Inspect company records
    with open(comp_file, "r", encoding="utf-8") as f:
        comp_records = json.load(f)

    for rec in comp_records:
        assert rec["source_type"] == "official_api"
        assert rec["ingestion_method"] == "api"
        assert rec["data_type"] == "company"
        assert str(rec["record_id"]).startswith("API-COMP-")
        assert "legal_name" in rec
        assert "source" in rec
        assert "validation" in rec
        assert "rfc_valid" in rec["validation"]
        assert "phone_valid" in rec["validation"]
        assert "quality_score" in rec

    # 3. Inspect people records
    with open(people_file, "r", encoding="utf-8") as f:
        people_records = json.load(f)

    for rec in people_records:
        assert rec["source_type"] == "official_api"
        assert rec["ingestion_method"] == "api"
        assert rec["data_type"] == "person"
        assert str(rec["record_id"]).startswith("API-PERS-")
        assert "company_name" in rec
        assert "full_name" in rec
        assert "validation" in rec
        assert "quality_score" in rec

    # 4. Summary and validation report checks
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
        assert summary["channel"] == "api"
        assert "totals" in summary
        assert "sources" in summary

    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)
        assert "source_statuses" in report
        assert "DENUE" in report["source_statuses"] or "SIEM" in report["source_statuses"]


def test_scraping_pipeline_isolation(pipeline):
    """Verifies that the Scraping pipeline produces only scraped directory data with public_directory source types."""
    results = pipeline.run_scraping_pipeline(limit=5, dry_run=False, sample=True)

    assert results["category"] == "scraping"
    assert len(results["companies"]) > 0
    assert len(results["people"]) > 0

    # 1. Output files must exist in output/scraping/
    comp_file = settings.SCRAPING_COMPANIES_DIR / "scraped_companies.json"
    people_file = settings.SCRAPING_PEOPLE_DIR / "scraped_people.json"
    summary_file = settings.SCRAPING_LOGS_DIR / "scraping_summary.json"
    report_file = settings.SCRAPING_REPORTS_DIR / "scraping_validation_report.json"
    ingestion_log = settings.SCRAPING_LOGS_DIR / "scraping_ingestion.log"
    validation_log = settings.SCRAPING_LOGS_DIR / "scraping_validation.log"

    assert comp_file.exists()
    assert people_file.exists()
    assert summary_file.exists()
    assert report_file.exists()
    assert ingestion_log.exists()
    assert validation_log.exists()

    # 2. Inspect company records
    with open(comp_file, "r", encoding="utf-8") as f:
        comp_records = json.load(f)

    for rec in comp_records:
        assert rec["source_type"] == "public_directory"
        assert rec["ingestion_method"] == "scraping"
        assert rec["data_type"] == "company"
        assert str(rec["record_id"]).startswith("SCRP-COMP-")
        assert "legal_name" in rec
        assert "source" in rec
        assert "validation" in rec
        assert "quality_score" in rec

    # 3. Inspect people records
    with open(people_file, "r", encoding="utf-8") as f:
        people_records = json.load(f)

    for rec in people_records:
        assert rec["source_type"] == "public_directory"
        assert rec["ingestion_method"] == "scraping"
        assert rec["data_type"] == "person"
        assert str(rec["record_id"]).startswith("SCRP-PERS-")
        assert "company_name" in rec
        assert "full_name" in rec
        assert "validation" in rec
        assert "quality_score" in rec

    # 4. Summary check
    with open(summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
        assert summary["channel"] == "scraping"
        assert "totals" in summary
        assert "sources" in summary


def test_combined_pipeline_golden_merge(pipeline):
    """Verifies that the Combined stage correctly resolves entities across both channels while preserving provenance."""
    api_res = pipeline.run_api_pipeline(limit=5, dry_run=False, sample=True)
    scraping_res = pipeline.run_scraping_pipeline(limit=5, dry_run=False, sample=True)

    combined_res = pipeline.run_combined_pipeline(
        api_companies=api_res["companies"],
        scraped_companies=scraping_res["companies"],
        api_people=api_res["people"],
        scraped_people=scraping_res["people"],
        dry_run=False,
    )

    assert "golden_companies" in combined_res
    assert "golden_people" in combined_res
    assert len(combined_res["golden_companies"]) > 0

    all_comp_file = settings.COMBINED_COMPANIES_DIR / "all_companies.json"
    all_people_file = settings.COMBINED_PEOPLE_DIR / "all_people.json"
    combined_summary_file = settings.COMBINED_REPORTS_DIR / "combined_summary.json"

    assert all_comp_file.exists()
    assert all_people_file.exists()
    assert combined_summary_file.exists()

    with open(combined_summary_file, "r", encoding="utf-8") as f:
        summary = json.load(f)
        assert summary["total_api_companies"] == len(api_res["companies"])
        assert summary["total_scraped_companies"] == len(scraping_res["companies"])
        assert summary["golden_company_profiles"] == len(combined_res["golden_companies"])
