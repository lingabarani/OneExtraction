"""
Unit tests for data validation and quality scoring.
"""

import pytest
from mexico_b2b.models.company import CanonicalCompany, Address
from mexico_b2b.pipeline.validation import validate_company
from mexico_b2b.pipeline.quality import calculate_data_quality_score


def test_validation_valid_company():
    comp = CanonicalCompany(
        company_id="test_001",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        trade_name="TECNOLOGIAS DE MEXICO",
        rfc="TME150115AB1",
        phone="+525555123456",
        email="contacto@tec-mexico.com.mx",
        address=Address(state="Ciudad de México", postal_code="03940"),
        latitude=19.362145,
        longitude=-99.182312,
    )
    result = validate_company(comp)
    assert result.is_valid is True
    assert len(result.errors) == 0


def test_validation_missing_name_error():
    comp = CanonicalCompany(
        company_id="test_002",
        legal_name=None,
        trade_name=None,
        rfc="TME150115AB1",
    )
    result = validate_company(comp)
    assert result.is_valid is False
    assert any("MISSING_COMPANY_NAME" in e for e in result.errors)


def test_quality_scoring():
    full_comp = CanonicalCompany(
        company_id="test_001",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        trade_name="TECNOLOGIAS DE MEXICO",
        rfc="TME150115AB1",
        website="https://tec-mexico.com.mx",
        domain="tec-mexico.com.mx",
        industry="Software y TI",
        industry_code="541510",
        phone="+525555123456",
        email="contacto@tec-mexico.com.mx",
        address=Address(state="Ciudad de México", municipality="Benito Juárez", postal_code="03940"),
        latitude=19.362145,
        longitude=-99.182312,
    )
    score = calculate_data_quality_score(full_comp)
    assert score >= 80

    sparse_comp = CanonicalCompany(
        company_id="test_002",
        legal_name="EMPRESA MINIMA",
    )
    sparse_score = calculate_data_quality_score(sparse_comp)
    assert sparse_score < 40
