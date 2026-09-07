"""
Unit tests for source connector ingestion and parsing across all Mexican sources and directories.
"""

import pytest
from mexico_b2b.config.sources import sources_registry
from mexico_b2b.connectors import get_connector
from mexico_b2b.connectors.denue import DenueConnector
from mexico_b2b.connectors.siem import SiemConnector
from mexico_b2b.connectors.supplier_registry import SupplierRegistryConnector
from mexico_b2b.connectors.sat import SatConnector
from mexico_b2b.connectors.canacintra import CanacintraConnector
from mexico_b2b.connectors.amcham import AmchamConnector
from mexico_b2b.connectors.cosmos import CosmosConnector
from mexico_b2b.connectors.quiminet import QuiminetConnector
from mexico_b2b.connectors.seccion_amarilla import SeccionAmarillaConnector


def test_denue_connector_ingest():
    cfg = sources_registry.get_source("denue")
    connector = DenueConnector(cfg)
    connector.api_token = None  # Test fixture parsing deterministically in unit test
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


def test_canacintra_connector_ingest():
    cfg = sources_registry.get_source("canacintra")
    connector = CanacintraConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "CANACINTRA"
    assert valid[0].legal_name is not None
    assert valid[0].phone is not None
    assert valid[0].address.state in ("Morelos", "Ciudad de México", "CDMX")


def test_amcham_connector_ingest():
    cfg = sources_registry.get_source("amcham")
    connector = AmchamConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "AMCHAM"
    assert valid[0].website is not None
    assert valid[0].domain is not None


def test_cosmos_connector_ingest():
    cfg = sources_registry.get_source("cosmos")
    connector = CosmosConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "COSMOS"
    assert valid[0].legal_name is not None
    assert valid[0].phone is not None


def test_quiminet_connector_ingest():
    cfg = sources_registry.get_source("quiminet")
    connector = QuiminetConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "QUIMINET"
    assert valid[0].legal_name is not None
    assert valid[0].industry is not None


def test_seccion_amarilla_connector_ingest():
    cfg = sources_registry.get_source("seccion_amarilla")
    connector = SeccionAmarillaConnector(cfg)
    valid, invalid = connector.ingest(limit=5)
    assert len(valid) > 0
    assert valid[0].source_records[0].source == "SECCION_AMARILLA"
    assert valid[0].phone is not None
    assert valid[0].latitude is not None
