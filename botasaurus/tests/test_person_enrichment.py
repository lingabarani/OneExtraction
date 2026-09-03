"""
Unit tests for Person & Executive Decision-Maker enrichment.
"""

import pytest
from mexico_b2b.models.company import CanonicalCompany, Address
from mexico_b2b.models.source_record import SourceProvenanceRecord
from mexico_b2b.utils.name_utils import parse_mexican_full_name, clean_name_string
from mexico_b2b.pipeline.person_enrichment import classify_title, person_enrichment_engine


def test_name_parsing_spanish():
    # Compound given name
    first, last, full = parse_mexican_full_name("Lic. Juan Carlos Pérez López")
    assert first == "Juan Carlos"
    assert last == "Pérez López"
    assert full == "Juan Carlos Pérez López"

    # Single surname
    first2, last2, full2 = parse_mexican_full_name("Ing. Carlos Slim")
    assert first2 == "Carlos"
    assert last2 == "Slim"

    # With professional title prefix
    first3, last3, full3 = parse_mexican_full_name("Dr. Jorge Luis González")
    assert first3 == "Jorge Luis"
    assert last3 == "González"


def test_title_classification():
    title1, sen1, dept1 = classify_title("Director General")
    assert title1 == "Chief Executive Officer (CEO)"
    assert sen1 == "C_SUITE"
    assert dept1 == "EXECUTIVE"

    title2, sen2, dept2 = classify_title("Director de Tecnología (CTO)")
    assert title2 == "Chief Technology Officer (CTO)"
    assert sen2 == "C_SUITE"
    assert dept2 == "ENGINEERING_IT"

    title3, sen3, dept3 = classify_title("Director de Finanzas")
    assert title3 == "Chief Financial Officer (CFO)"
    assert sen3 == "C_SUITE"
    assert dept3 == "FINANCE"

    title4, sen4, dept4 = classify_title("Gerente de Recursos Humanos")
    assert title4 == "HR Manager"
    assert sen4 == "MANAGER"
    assert dept4 == "HR_PEOPLE"

    title5, sen5, dept5 = classify_title("Socio Fundador")
    assert title5 == "Founder"
    assert sen5 == "FOUNDER"
    assert dept5 == "EXECUTIVE"

    title6, sen6, dept6 = classify_title("Representante Legal")
    assert title6 == "Chief Legal Officer (CLO)"
    assert sen6 == "C_SUITE"
    assert dept6 == "LEGAL_COMPLIANCE"


def test_decision_maker_extraction():
    comp = CanonicalCompany(
        company_id="mx_test123",
        legal_name="TECNOLOGIAS DE MEXICO SA DE CV",
        domain="tec-mexico.com.mx",
        phone="+525555123456",
        source_records=[SourceProvenanceRecord("SIEM", "siem_1", "http://siem", "2023-01-01")],
    )

    candidates = [
        {"name": "Carlos González", "title": "Director General", "correo": "carlos.gonzalez@tec-mexico.com.mx"},
        {"name": "Ana María Torres", "title": "Directora de Recursos Humanos"},
    ]

    executives = person_enrichment_engine.extract_and_enrich_decision_makers(comp, candidates)
    assert len(executives) == 2

    ceo = executives[0]
    assert ceo.standardized_title == "Chief Executive Officer (CEO)"
    assert ceo.seniority_level == "C_SUITE"
    assert ceo.first_name == "Carlos"
    assert ceo.last_name == "González"
    assert ceo.work_email == "carlos.gonzalez@tec-mexico.com.mx"

    hr = executives[1]
    assert hr.standardized_title == "Chief Human Resources Officer (CHRO)"
    assert hr.department == "HR_PEOPLE"
    assert hr.first_name == "Ana María"
    assert hr.work_email == "ana.torres@tec-mexico.com.mx"
