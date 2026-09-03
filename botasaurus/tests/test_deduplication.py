"""
Unit tests for deduplication and source-priority merging.
"""

import pytest
from mexico_b2b.models.company import CanonicalCompany, Address, PhoneItem, EmailItem
from mexico_b2b.models.source_record import SourceProvenanceRecord
from mexico_b2b.pipeline.deduplication import deduplication_engine
from mexico_b2b.pipeline.merger import merge_engine


def test_deduplication_clusters():
    c1 = CanonicalCompany(
        company_id="c1",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        normalized_name="TECNOLOGIAS DE MEXICO",
        rfc="TME150115AB1",
        address=Address(state="Ciudad de México"),
        source_records=[SourceProvenanceRecord("DENUE", "den_1", "http://denue", "2023-01-01")],
    )
    c2 = CanonicalCompany(
        company_id="c2",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        normalized_name="TECNOLOGIAS DE MEXICO",
        rfc="TME150115AB1",
        address=Address(state="Ciudad de México"),
        source_records=[SourceProvenanceRecord("SIEM", "siem_1", "http://siem", "2023-01-02")],
    )
    c3 = CanonicalCompany(
        company_id="c3",
        legal_name="OTRA EMPRESA DISTINTA SA DE CV",
        normalized_name="OTRA EMPRESA DISTINTA",
        rfc="OED190101XYZ",
        address=Address(state="Puebla"),
        source_records=[SourceProvenanceRecord("SIEM", "siem_2", "http://siem", "2023-01-03")],
    )

    clusters, review_queue, dups = deduplication_engine.deduplicate([c1, c2, c3])
    assert len(clusters) == 2
    assert dups == 1


def test_merge_priority_and_provenance():
    denue_rec = CanonicalCompany(
        company_id="c1",
        trade_name="TEC MEXICO",
        legal_name="TEC MEXICO SA DE CV",
        normalized_name="TEC MEXICO",
        phone="+525555123456",
        latitude=19.362145,
        longitude=-99.182312,
        address=Address(street="Insurgentes Sur", number="1602", state="Ciudad de México"),
        source_records=[SourceProvenanceRecord("DENUE", "den_1", "http://denue", "2023-01-01")],
    )
    siem_rec = CanonicalCompany(
        company_id="c2",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        normalized_name="TEC MEXICO",
        rfc="TME150115AB1",
        email="contacto@tec-mexico.com.mx",
        address=Address(state="Ciudad de México", postal_code="03940"),
        source_records=[SourceProvenanceRecord("SIEM", "siem_1", "http://siem", "2023-01-02")],
    )

    merged = merge_engine.merge_cluster([denue_rec, siem_rec])
    # Verify RFC preserved from SIEM
    assert merged.rfc == "TME150115AB1"
    # Coordinates preserved from DENUE
    assert merged.latitude == 19.362145
    # Provenance aggregated
    assert len(merged.source_records) == 2
    assert merged.source_count == 2
    assert merged.phone == "+525555123456"
    assert merged.email == "contacto@tec-mexico.com.mx"
    assert merged.data_quality_score > 70
