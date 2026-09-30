"""
Unit tests for RDAP WHOIS connector, Wikipedia summary connector, and MCP Server.
"""

import unittest
from src.us_b2b.connectors.rdap_client import RDAPClient, rdap_client
from src.us_b2b.connectors.wikipedia_client import WikipediaClient, wikipedia_client
from src.us_b2b.mcp_server import search_companies_tool, get_company_details_tool


class TestMCPAndRDAP(unittest.TestCase):
    def test_rdap_parser(self):
        sample_rdap = {
            "handle": "DOMAIN_123",
            "status": ["active", "clientTransferProhibited"],
            "events": [
                {"eventAction": "registration", "eventDate": "1997-09-15T04:00:00Z"},
                {"eventAction": "expiration", "eventDate": "2028-09-13T04:00:00Z"},
            ],
            "entities": [
                {
                    "roles": ["registrant"],
                    "vcardArray": ["vcard", [["fn", {}, "text", "Apple Inc."]]],
                }
            ],
        }
        parsed = rdap_client.parse_rdap_response(sample_rdap, "apple.com")
        self.assertEqual(parsed["domain"], "apple.com")
        self.assertEqual(parsed["registrant_organization"], "Apple Inc.")
        self.assertEqual(parsed["creation_date"], "1997-09-15T04:00:00Z")

    def test_mcp_search_tool(self):
        # Test company search on existing output database
        results = search_companies_tool(query="", limit=5)
        self.assertIsInstance(results, list)


if __name__ == "__main__":
    unittest.main()
