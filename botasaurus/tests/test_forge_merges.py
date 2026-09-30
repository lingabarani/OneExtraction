"""
Unit tests for FORGE merged components: CMS NPI Healthcare Registry & Tech Stack Detector.
"""

import unittest
from src.us_b2b.connectors.npi_client import NPIClient, npi_client
from src.us_b2b.connectors.fcc_uls_client import FCCULSClient, fcc_uls_client
from src.us_b2b.utils.tech_detector import detect_tech_stack
from src.us_b2b.models.source_record import RawSourcePayload


class TestForgeMerges(unittest.TestCase):
    def test_npi_client_normalize(self):
        raw = {
            "number": 1234567890,
            "enumeration_type": "NPI-2",
            "basic": {
                "organization_name": "COMMUNITY HEALTH CENTER LLC",
            },
            "addresses": [
                {
                    "address_purpose": "LOCATION",
                    "address_1": "100 MEDICAL WAY",
                    "city": "CHICAGO",
                    "state": "IL",
                    "postal_code": "606011234",
                    "telephone_number": "3125550199",
                }
            ],
            "taxonomies": [
                {"code": "282N00000X", "desc": "Hospitals & Medical Centers", "primary": True}
            ],
        }
        payload = RawSourcePayload(
            source="CMS_NPI",
            source_record_id="NPI_1234567890",
            source_url="https://npiregistry.cms.hhs.gov/provider-details/1234567890",
            raw_data=raw,
        )

        company = npi_client.normalize(payload)
        self.assertIsNotNone(company)
        self.assertEqual(company.legal_name, "COMMUNITY HEALTH CENTER LLC")
        self.assertEqual(company.address.city, "CHICAGO")
        self.assertEqual(company.address.state_code, "IL")
        self.assertEqual(company.phone, "+13125550199")

    def test_tech_detector(self):
        sample_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="/_next/static/css/styles.css">
            <script src="https://js.stripe.com/v3/"></script>
        </head>
        <body class="bg-gray-100 tailwind">
            <div id="__NEXT_DATA__"></div>
        </body>
        </html>
        """
        tech_list = detect_tech_stack(sample_html)
        self.assertIn("Next.js", tech_list)
        self.assertIn("React", tech_list)
        self.assertIn("Stripe", tech_list)
        self.assertIn("Tailwind CSS", tech_list)


if __name__ == "__main__":
    unittest.main()
