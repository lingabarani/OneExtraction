"""
Canonical company data model and associated nested structures.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from .source_record import SourceProvenanceRecord
from .person import DecisionMaker


@dataclass
class Address:
    street: Optional[str] = None
    number: Optional[str] = None
    colony: Optional[str] = None
    municipality: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "Mexico"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PhoneItem:
    value: str
    source: str
    type: str = "OFFICE"
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmailItem:
    value: str
    source: str
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CanonicalCompany:
    """
    Canonical Company Entity representing a single business in Mexico.
    Aggregates information from DENUE, SIEM, supplier registries, and official portals.
    """
    company_id: str
    legal_name: Optional[str] = None
    trade_name: Optional[str] = None
    normalized_name: Optional[str] = None
    rfc: Optional[str] = None
    rfc_type: Optional[str] = None
    website: Optional[str] = None
    domain: Optional[str] = None
    industry: Optional[str] = None
    industry_code: Optional[str] = None
    employee_count_min: Optional[int] = None
    employee_count_max: Optional[int] = None
    employee_count_source: Optional[str] = None
    phone: Optional[str] = None
    phones: List[PhoneItem] = field(default_factory=list)
    email: Optional[str] = None
    emails: List[EmailItem] = field(default_factory=list)
    address: Address = field(default_factory=Address)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    decision_makers: List[DecisionMaker] = field(default_factory=list)
    source_records: List[SourceProvenanceRecord] = field(default_factory=list)
    source_count: int = 0
    data_quality_score: int = 0
    entity_fingerprint: str = ""
    last_verified_at: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    privacy_classification: str = "B2B_PUBLIC"
    deletion_status: str = "ACTIVE"

    def to_dict(self, include_personal_contacts: bool = True) -> Dict[str, Any]:
        """Converts model to dictionary, applying privacy controls if needed."""
        d = {
            "company_id": self.company_id,
            "legal_name": self.legal_name,
            "trade_name": self.trade_name,
            "normalized_name": self.normalized_name,
            "rfc": self.rfc,
            "rfc_type": self.rfc_type,
            "website": self.website,
            "domain": self.domain,
            "industry": self.industry,
            "industry_code": self.industry_code,
            "employee_count_min": self.employee_count_min,
            "employee_count_max": self.employee_count_max,
            "employee_count_source": self.employee_count_source,
            "phone": self.phone if include_personal_contacts else None,
            "phones": [p.to_dict() for p in self.phones] if include_personal_contacts else [],
            "email": self.email if include_personal_contacts else None,
            "emails": [e.to_dict() for e in self.emails] if include_personal_contacts else [],
            "address": self.address.to_dict() if isinstance(self.address, Address) else self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "decision_makers": [dm.to_dict(include_personal_contacts=include_personal_contacts) for dm in self.decision_makers],
            "decision_maker_count": len(self.decision_makers),
            "source_records": [s.to_dict() for s in self.source_records],
            "source_count": self.source_count or len(self.source_records),
            "data_quality_score": self.data_quality_score,
            "entity_fingerprint": self.entity_fingerprint,
            "last_verified_at": self.last_verified_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "privacy_classification": self.privacy_classification,
            "deletion_status": self.deletion_status,
        }
        return d

    def to_flat_dict(self, include_personal_contacts: bool = True) -> Dict[str, Any]:
        """Flattened dictionary for CSV and Excel tabular export."""
        addr = self.address if isinstance(self.address, Address) else Address(**(self.address or {}))
        sources_str = ";".join([s.source for s in self.source_records])
        return {
            "company_id": self.company_id,
            "legal_name": self.legal_name or "",
            "trade_name": self.trade_name or "",
            "rfc": self.rfc or "",
            "rfc_type": self.rfc_type or "",
            "website": self.website or "",
            "domain": self.domain or "",
            "industry": self.industry or "",
            "industry_code": self.industry_code or "",
            "employee_count_min": self.employee_count_min if self.employee_count_min is not None else "",
            "employee_count_max": self.employee_count_max if self.employee_count_max is not None else "",
            "employee_count_source": self.employee_count_source or "",
            "phone": (self.phone or "") if include_personal_contacts else "",
            "email": (self.email or "") if include_personal_contacts else "",
            "street": addr.street or "",
            "number": addr.number or "",
            "colony": addr.colony or "",
            "municipality": addr.municipality or "",
            "state": addr.state or "",
            "postal_code": addr.postal_code or "",
            "country": addr.country or "Mexico",
            "latitude": self.latitude if self.latitude is not None else "",
            "longitude": self.longitude if self.longitude is not None else "",
            "source_count": self.source_count or len(self.source_records),
            "sources": sources_str,
            "data_quality_score": self.data_quality_score,
            "last_verified_at": self.last_verified_at or "",
            "created_at": self.created_at or "",
        }
