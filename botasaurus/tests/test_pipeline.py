"""
End-to-end tests for the complete Mexico B2B Ingestion Pipeline.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from mexico_b2b.pipeline.ingestion import IngestionPipeline
from mexico_b2b.config.settings import settings
from mexico_b2b.connectors.denue import DenueConnector


def test_full_pipeline_run():
    pipeline = IngestionPipeline()
    
    # Mock DenueConnector.fetch to return local fixture payload instantly during test suite
    with patch.object(DenueConnector, "fetch", autospec=True) as mock_denue_fetch:
        # Load fixture data
        fixture_path = settings.PROJECT_ROOT / "tests" / "fixtures" / "sample_denue.json"
        with open(fixture_path, "r", encoding="utf-8") as f:
            fixture_items = json.load(f)
        
        from mexico_b2b.models.source_record import RawSourcePayload
        from mexico_b2b.utils.hashing import sha256_dict
        
        mock_payloads = [
            RawSourcePayload(
                source="DENUE",
                source_record_id=str(item.get("CLEE") or item.get("Id")),
                source_url="local_fixture://denue",
                raw_data=item,
                raw_hash=sha256_dict(item),
            )
            for item in fixture_items
        ]
        mock_denue_fetch.return_value = mock_payloads

        results = pipeline.run(source_keys=["denue", "siem", "supplier", "sat"], limit=10, dry_run=False)

    metrics = results["metrics"]
    assert metrics["total_raw_records"] > 0
    assert metrics["valid_records"] > 0
    assert metrics["merged_records"] > 0
    assert metrics["average_quality_score"] > 0

    # Verify generated output files
    json_path = settings.OUTPUT_DIR / "mexico_companies.json"
    csv_path = settings.OUTPUT_DIR / "mexico_companies.csv"
    xlsx_path = settings.OUTPUT_DIR / "mexico_companies.xlsx"
    report_path = settings.OUTPUT_DIR / "validation_report.json"
    status_path = settings.OUTPUT_DIR / "source_status.json"

    assert json_path.exists()
    assert csv_path.exists()
    assert xlsx_path.exists()
    assert report_path.exists()
    assert status_path.exists()

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data) == metrics["merged_records"]
        first = data[0]
        assert "company_id" in first
        assert "source_records" in first
        assert "data_quality_score" in first
        assert "address" in first
        assert "country" in first["address"]
        assert first["address"]["country"] == "Mexico"

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
        assert "summary_metrics" in report
        assert "source_statuses" in report
