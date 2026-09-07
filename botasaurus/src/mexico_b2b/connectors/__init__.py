"""
Connectors package and connector registry factory.
Integrates official Mexican open-data portals, government registries, and B2B industrial directories.
"""

from typing import Dict, Type
from .base import SourceConnector
from .denue import DenueConnector
from .siem import SiemConnector
from .supplier_registry import SupplierRegistryConnector
from .datos_gob import DatosGobConnector
from .sat import SatConnector
from .rpc import RpcConnector
from .canacintra import CanacintraConnector
from .amcham import AmchamConnector
from .cosmos import CosmosConnector
from .quiminet import QuiminetConnector
from .seccion_amarilla import SeccionAmarillaConnector
from ..config.sources import SourceConfig


CONNECTOR_CLASSES: Dict[str, Type[SourceConnector]] = {
    "denue": DenueConnector,
    "denue_bulk": DenueConnector,
    "denue_map": DenueConnector,
    "inegi_datos_abiertos": DenueConnector,
    "siem": SiemConnector,
    "supplier_registry": SupplierRegistryConnector,
    "supplier": SupplierRegistryConnector,
    "datos_gob": DatosGobConnector,
    "sat": SatConnector,
    "sat_validator": SatConnector,
    "rpc": RpcConnector,
    "canacintra": CanacintraConnector,
    "amcham": AmchamConnector,
    "cosmos": CosmosConnector,
    "quiminet": QuiminetConnector,
    "seccion_amarilla": SeccionAmarillaConnector,
}


def get_connector(source_key: str, config: SourceConfig) -> SourceConnector:
    """Factory creating an initialized SourceConnector instance."""
    cls = CONNECTOR_CLASSES.get(source_key.lower())
    if not cls:
        raise ValueError(f"Unknown source connector '{source_key}'. Available: {list(CONNECTOR_CLASSES.keys())}")
    return cls(config)
