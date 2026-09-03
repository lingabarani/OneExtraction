"""
Unit tests for source connector ingestion and parsing.
"""

import pytest
from unittest.mock import MagicMock
from mexico_b2b.config.sources import sources_registry
from mexico_b2b.connectors import get_connector
from mexico_b2b.connectors.denue import DenueConnector
from mexico_b2b.connectors.siem import SiemConnector
from mexico_b2b.connectors.supplier_registry import SupplierRegistryConnector
from mexico_b2b.connectors.sat import SatConnector


def test_denue_connector_ingest():
    cfg = sources_registry.get_source("denue")
    connector = DenueConnector(cfg)
    connector.api_token = None # Test fixture parsing deterministically in unit test
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "DENUE"
    assert valid[0].address.state is not None


def test_siem_connector_ingest():
    cfg = sources_registry.get_source("siem")
    connector = SiemConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "SIEM"
    assert valid[0].rfc is not None


def test_supplier_connector_ingest():
    cfg = sources_registry.get_source("supplier_registry")
    connector = SupplierRegistryConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "SUPPLIER_REGISTRY"


def test_sat_connector_ingest():
    cfg = sources_registry.get_source("sat")
    connector = SatConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "SAT"
    assert valid[0].privacy_classification == "COMPLIANCE_PUBLIC"
