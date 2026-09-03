"""
Unit tests for DNS, MX inspection, and email deliverability verification.
"""

import pytest
from mexico_b2b.utils.dns_utils import (
    detect_mail_provider,
    generate_email_permutations,
    verify_email_deliverability,
)


def test_mail_provider_detection():
    outlook_mx = ["tec-mexico-com-mx.mail.protection.outlook.com"]
    assert detect_mail_provider(outlook_mx) == "MICROSOFT_365_OUTLOOK"

    google_mx = ["aspmx.l.google.com", "alt1.aspmx.l.google.com"]
    assert detect_mail_provider(google_mx) == "GOOGLE_WORKSPACE"

    custom_mx = ["mail.empresa.com.mx"]
    assert detect_mail_provider(custom_mx) == "CUSTOM_SMTP"

    assert detect_mail_provider([]) == "UNKNOWN"


def test_email_permutations():
    perms = generate_email_permutations("Carlos", "González Rodríguez", "empresa.com.mx")
    emails = [p[0] for p in perms]
    assert "carlos.gonzalez@empresa.com.mx" in emails
    assert "cgonzalez@empresa.com.mx" in emails
    assert "carlos@empresa.com.mx" in emails


def test_email_deliverability_scoring():
    # Valid syntax with mock MX
    mock_mx = ["mail.protection.outlook.com"]
    status, score = verify_email_deliverability(
        "carlos.gonzalez@empresa.com.mx",
        mx_records=mock_mx,
        perform_smtp_handshake=False,
    )
    assert status == "PROBABLE"
    assert score >= 70

    # Invalid email syntax
    status_inv, score_inv = verify_email_deliverability("notanemail")
    assert status_inv == "INVALID"
    assert score_inv == 0
