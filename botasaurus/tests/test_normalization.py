"""
Unit tests for data normalization utilities.
"""

import pytest
from mexico_b2b.pipeline.normalization import (
    normalize_company_name,
    normalize_email,
    normalize_website,
    parse_employee_range,
)
from mexico_b2b.utils.rfc_utils import clean_rfc, is_valid_rfc, get_rfc_type
from mexico_b2b.utils.phone_utils import clean_phone, is_valid_mx_phone, format_mx_phone_e164
from mexico_b2b.utils.address_utils import normalize_state, clean_postal_code


def test_company_name_normalization():
    # Legal suffix removal and casing
    orig, norm = normalize_company_name("ABC TECHNOLOGIES S.A. DE C.V.")
    assert orig == "ABC TECHNOLOGIES S.A. DE C.V."
    assert norm == "ABC TECHNOLOGIES"

    orig2, norm2 = normalize_company_name("Compañía Minera del Norte, S. de R.L. de C.V.")
    assert orig2 == "Compañía Minera del Norte, S. de R.L. de C.V."
    assert norm2 == "COMPANIA MINERA DEL NORTE"

    orig3, norm3 = normalize_company_name("Soluciones Digitales SAPI de CV")
    assert norm3 == "SOLUCIONES DIGITALES"


def test_rfc_validation():
    # Persona Moral (12 chars)
    assert is_valid_rfc("TME150115AB1") is True
    assert get_rfc_type("TME150115AB1") == "MORAL"

    # Persona Física (13 chars)
    assert is_valid_rfc("GARM850101XYZ") is True
    assert get_rfc_type("GARM850101XYZ") == "FISICA"

    # Invalid RFC
    assert is_valid_rfc("INVALID_RFC_123") is False
    assert is_valid_rfc("123") is False


def test_phone_normalization():
    # 10 digit standard
    assert format_mx_phone_e164("55 5512 3456") == "+525555123456"
    assert format_mx_phone_e164("+52 (33) 3612-3456") == "+523336123456"
    assert is_valid_mx_phone("5555123456") is True
    # Invalid
    assert is_valid_mx_phone("12345") is False


def test_email_normalization():
    assert normalize_email(" Contacto@Tec-Mexico.Com.MX ") == "contacto@tec-mexico.com.mx"
    assert normalize_email("no_tiene@correo.com") is None
    assert normalize_email("invalid-email-string") is None


def test_website_normalization():
    url, domain = normalize_website("http://www.tec-mexico.com.mx/contacto")
    assert url == "https://www.tec-mexico.com.mx/contacto"
    assert domain == "tec-mexico.com.mx"

    url2, domain2 = normalize_website("empresas.com.mx")
    assert url2 == "https://empresas.com.mx"
    assert domain2 == "empresas.com.mx"


def test_state_and_postal_code_normalization():
    assert normalize_state("CDMX") == "Ciudad de México"
    assert normalize_state("Distrito Federal") == "Ciudad de México"
    assert normalize_state("JAL") == "Jalisco"
    assert normalize_state("NUEVO LEON") == "Nuevo León"
    assert normalize_state("Edo Mex") == "México"

    assert clean_postal_code("03940") == "03940"
    assert clean_postal_code("3940") == "03940"


def test_employee_range_parser():
    min_c, max_c, src = parse_employee_range("11 a 30 personas")
    assert min_c == 11
    assert max_c == 30

    min_c2, max_c2, src2 = parse_employee_range("251 y más personas")
    assert min_c2 == 251
    assert max_c2 is None
