"""
Unit tests for 6-stage entity resolution engine.
"""

import pytest
from mexico_b2b.models.company import CanonicalCompany, Address
from mexico_b2b.models.source_record import SourceProvenanceRecord
from mexico_b2b.pipeline.entity_resolution import entity_resolver


def test_stage_1_exact_rfc_match():
    c1 = CanonicalCompany(
        company_id="c1",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        rfc="TME150115AB1",
    )
    c2 = CanonicalCompany(
        company_id="c2",
        legal_name="TEC MEXICO",
        rfc="TME150115AB1",
    )
    result = entity_resolver.match(c1, c2)
    assert result.score == 1.0
    assert result.decision == "AUTO_MERGE"
    assert "EXACT_RFC_MATCH" in result.reasons


def test_stage_3_exact_domain_match():
    c1 = CanonicalCompany(
        company_id="c1",
        trade_name="DENUE EMPRESA TECH",
        domain="tec-mexico.com.mx",
        address=Address(state="Ciudad de México"),
    )
    c2 = CanonicalCompany(
        company_id="c2",
        trade_name="SIEM EMPRESA TECH",
        domain="tec-mexico.com.mx",
        address=Address(state="Ciudad de México"),
    )
    result = entity_resolver.match(c1, c2)
    assert result.score >= 0.95
    assert result.decision == "AUTO_MERGE"
    assert "EXACT_DOMAIN_MATCH" in result.reasons


def test_stage_4_normalized_name_and_location_match():
    c1 = CanonicalCompany(
        company_id="c1",
        legal_name="LOGISTICA OCCIDENTE SA DE CV",
        normalized_name="LOGISTICA OCCIDENTE",
        address=Address(state="Jalisco", municipality="Guadalajara"),
    )
    c2 = CanonicalCompany(
        company_id="c2",
        legal_name="LOGISTICA OCCIDENTE S DE RL DE CV",
        normalized_name="LOGISTICA OCCIDENTE",
        address=Address(state="Jalisco", municipality="Guadalajara"),
    )
    result = entity_resolver.match(c1, c2)
    assert result.score >= 0.95
    assert result.decision == "AUTO_MERGE"


def test_different_companies_separate():
    c1 = CanonicalCompany(
        company_id="c1",
        legal_name="FARMACIAS DE OCCIDENTE SA DE CV",
        normalized_name="FARMACIAS DE OCCIDENTE",
        address=Address(state="Jalisco"),
    )
    c2 = CanonicalCompany(
        company_id="c2",
        legal_name="CONSTRUCTORA DEL NORTE SA DE CV",
        normalized_name="CONSTRUCTORA DEL NORTE",
        address=Address(state="Nuevo León"),
    )
    result = entity_resolver.match(c1, c2)
    assert result.decision == "SEPARATE_ENTITIES"
    assert result.score < 0.80
