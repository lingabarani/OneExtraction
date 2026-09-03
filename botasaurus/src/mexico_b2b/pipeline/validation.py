"""
Data validation engine for Mexican B2B company records.
"""

from typing import Dict, Any, List, Tuple
from ..models.company import CanonicalCompany, Address
from ..utils.rfc_utils import is_valid_rfc, is_generic_rfc
from ..utils.phone_utils import is_valid_mx_phone
from ..utils.address_utils import is_valid_postal_code, is_valid_coordinates, normalize_state


class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str], warnings: List[str]):
        self.is_valid = is_valid
        self.errors = errors
        self.warnings = warnings

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def validate_company(company: CanonicalCompany) -> ValidationResult:
    """
    Validates a canonical company record against strict business rules.
    """
    errors = []
    warnings = []

    # 1. Company Name check (Mandatory)
    if not company.legal_name and not company.trade_name:
        errors.append("MISSING_COMPANY_NAME: Record must have at least legal_name or trade_name")

    # 2. RFC check (Optional, but if present must be valid)
    if company.rfc:
        if not is_valid_rfc(company.rfc):
            warnings.append(f"INVALID_RFC_FORMAT: '{company.rfc}' is not a valid Mexican RFC")
        elif is_generic_rfc(company.rfc):
            warnings.append(f"GENERIC_RFC: '{company.rfc}' is a generic RFC")

    # 3. Address / State check
    addr = company.address
    if isinstance(addr, Address):
        if addr.state and not normalize_state(addr.state):
            warnings.append(f"UNRECOGNIZED_STATE: '{addr.state}' does not map to a recognized Mexican state")
        if addr.postal_code and not is_valid_postal_code(addr.postal_code):
            warnings.append(f"INVALID_POSTAL_CODE: '{addr.postal_code}' is not a valid 5-digit postal code")

    # 4. Coordinates check
    if company.latitude is not None or company.longitude is not None:
        if not is_valid_coordinates(company.latitude, company.longitude):
            warnings.append(
                f"OUT_OF_BOUNDS_COORDINATES: lat={company.latitude}, lng={company.longitude} is outside Mexico bounds"
            )

    # 5. Phone check
    if company.phone and not is_valid_mx_phone(company.phone):
        warnings.append(f"INVALID_PHONE_FORMAT: '{company.phone}' is not a valid 10-digit Mexican number")

    # Record is considered structurally valid if no fatal errors exist
    is_valid = len(errors) == 0

    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
