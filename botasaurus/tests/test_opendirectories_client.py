"""
Unit tests for OpenDirectories 12M+ Business REST API connector.
"""

import unittest
from src.us_b2b.connectors.opendirectories_client import OpenDirectoriesClient, opendirectories_client
from src.us_b2b.models.source_record import RawSourcePayload


class TestOpenDirectoriesClient(unittest.TestCase):
    def test_normalize(self):
        raw = {
            "id": 998877,
            "name": "METROPOLITAN HOSPITAL CENTER",
            "phone": "2125550199",
            "website": "https://www.metropolitan.org",
            "street_address": "1901 1ST AVE",
            "suburb": "NEW YORK",
            "state": "NY",
            "postcode": "10029",
            "country": "US",
            "google_rating": 4.5,
            "google_review_count": 320,
            "quality_score": 85,
        }
        payload = RawSourcePayload(
            source="OPENDIRECTORIES",
            source_record_id="OD_998877",
            source_url="https://www.metropolitan.org",
            raw_data=raw,
        )

        company = opendirectories_client.normalize(payload)
        self.assertIsNotNone(company)
        self.assertEqual(company.legal_name, "METROPOLITAN HOSPITAL CENTER")
        self.assertEqual(company.address.city, "NEW YORK")
        self.assertEqual(company.address.state_code, "NY")
        self.assertEqual(company.domain, "metropolitan.org")
        self.assertEqual(company.phone, "+12125550199")
        self.assertEqual(company.data_quality_score, 85)


if __name__ == "__main__":
    unittest.main()
