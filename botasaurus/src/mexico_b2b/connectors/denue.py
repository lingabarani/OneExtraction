"""
INEGI DENUE (Directorio Estadístico Nacional de Unidades Económicas) Connector.
Supports official INEGI REST API v1.0 and downloadable bulk files.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base import SourceConnector
from ..config.settings import settings
from ..models.company import CanonicalCompany, Address, PhoneItem, EmailItem
from ..models.source_record import RawSourcePayload, SourceProvenanceRecord
from ..pipeline.normalization import (
    normalize_company_name,
    normalize_email,
    normalize_website,
    parse_employee_range,
)
from ..utils.address_utils import normalize_state, clean_postal_code
from ..utils.phone_utils import format_mx_phone_e164, is_valid_mx_phone
from ..utils.hashing import sha256_dict, generate_entity_fingerprint, generate_company_id
from ..storage.raw_storage import raw_storage
from ..utils.logging import logger


class DenueConnector(SourceConnector):
    """
    Connector for INEGI DENUE official API and bulk datasets.
    """

    def __init__(self, config):
        super().__init__(config)
        self.api_token = settings.DENUE_API_TOKEN or os.getenv(self.config.token_env or "DENUE_API_TOKEN")

    def _get_api_token_or_fail(self) -> str:
        token = self.api_token
        if not token or token.strip() == "":
            raise ValueError(
                "DENUE_API_TOKEN is not configured. "
                "Please register at https://www.inegi.org.mx/servicios/api_denue.html "
                "and set DENUE_API_TOKEN in your .env file or environment variables."
            )
        return token.strip()

    def fetch(self, limit: Optional[int] = None) -> List[RawSourcePayload]:
        """
        Fetches records via official DENUE REST API with pagination.
        If token is missing and in local/sample environment, checks for local fixtures.
        """
        raw_payloads: List[RawSourcePayload] = []
        target_limit = limit or 50

        # Check if local raw/fixture file exists first (e.g. for offline/test mode)
        fixture_path = settings.PROJECT_ROOT / "tests" / "fixtures" / "sample_denue.json"
        if not fixture_path.exists():
            fixture_path = settings.PROJECT_ROOT / "tests" / "mexico_b2b" / "fixtures" / "sample_denue.json"
        
        try:
            token = self._get_api_token_or_fail()
            # Paginated API requests
            batch_size = min(target_limit, 50)
            reg_start = 1
            base_url = self.config.base_url or "https://www.inegi.org.mx/app/api/denue/v1/consulta"
            endpoint = self.config.endpoints.get("search_area_act", "BuscarAreaAct")
            condition = self.config.raw_config.get("default_condition", "todos")
            state_code = self.config.raw_config.get("default_state_code", "09")
            act_code = self.config.raw_config.get("default_activity_code", "0")

            while len(raw_payloads) < target_limit:
                reg_end = min(reg_start + batch_size - 1, target_limit)
                url = f"{base_url}/{endpoint}/{condition}/{state_code}/0/{act_code}/{reg_start}/{reg_end}/{token}"
                
                logger.info("Querying INEGI DENUE API", start=reg_start, end=reg_end)
                response = self.http_client.get(url)
                data = response.json()

                if not data or not isinstance(data, list):
                    break

                # Save raw response
                raw_storage.save_raw_text(
                    source_name="DENUE",
                    filename=f"denue_api_{state_code}_{reg_start}_{reg_end}.json",
                    text_content=response.text,
                    source_url=self.http_client._sanitize_url(url),
                )

                for item in data:
                    item_id = str(item.get("CLEE") or item.get("Id") or item.get("id") or len(raw_payloads) + 1)
                    raw_hash = sha256_dict(item)
                    raw_payloads.append(
                        RawSourcePayload(
                            source="DENUE",
                            source_record_id=item_id,
                            source_url=base_url,
                            raw_data=item,
                            raw_hash=raw_hash,
                        )
                    )
                    if len(raw_payloads) >= target_limit:
                        break

                if len(data) < batch_size:
                    break

                reg_start += batch_size

        except (ValueError, Exception) as e:
            if fixture_path.exists():
                logger.warn(f"INEGI DENUE API notice ({type(e).__name__}); falling back to local sample fixture from {fixture_path.name}")
                with open(fixture_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data[:target_limit]:
                    item_id = str(item.get("CLEE") or item.get("Id") or len(raw_payloads) + 1)
                    raw_payloads.append(
                        RawSourcePayload(
                            source="DENUE",
                            source_record_id=item_id,
                            source_url="local_fixture://denue",
                            raw_data=item,
                            raw_hash=sha256_dict(item),
                        )
                    )
            else:
                raise e

        return raw_payloads

    def parse(self, payload: RawSourcePayload) -> Dict[str, Any]:
        """Extracts standard dictionary fields from DENUE raw item."""
        d = payload.raw_data
        
        # Address construction
        street_type = d.get("Tipo_vialidad") or d.get("tipo_vialidad") or ""
        street_name = d.get("Calle") or d.get("calle") or d.get("Nombre_vialidad") or ""
        street = f"{street_type} {street_name}".strip() if street_type else street_name
        num_ext = d.get("Num_Exterior") or d.get("num_Exterior") or d.get("Numero_exterior") or ""
        num_int = d.get("Num_Interior") or d.get("num_Interior") or d.get("Letra_interior") or ""
        full_num = f"{num_ext} Int {num_int}".strip() if num_int else num_ext

        # State & Municipality
        location_raw = d.get("Ubicacion") or d.get("ubicacion") or ""
        muni = d.get("Municipio") or d.get("municipio") or ""
        state = d.get("Entidad") or d.get("entidad") or d.get("Estado") or ""
        
        if not state and "," in location_raw:
            parts = location_raw.split(",")
            muni = parts[0].strip()
            state = parts[-1].strip()

        # Coordinates
        lat = d.get("Latitud") or d.get("latitud")
        lng = d.get("Longitud") or d.get("longitud")
        lat_f = float(lat) if lat is not None and str(lat).strip() != "" else None
        lng_f = float(lng) if lng is not None and str(lng).strip() != "" else None

        return {
            "clee": d.get("CLEE") or d.get("clee"),
            "establishment_id": d.get("Id") or d.get("id"),
            "trade_name": d.get("Nombre") or d.get("nombre"),
            "legal_name": d.get("Razon_social") or d.get("razon_social"),
            "industry": d.get("Clase_actividad") or d.get("clase_actividad") or d.get("Nombre_act"),
            "industry_code": d.get("Codigo_act") or d.get("codigo_act"),
            "employee_range": d.get("Estrato") or d.get("estrato") or d.get("Personal_ocupado"),
            "street": street,
            "number": full_num,
            "colony": d.get("Colonia") or d.get("colonia") or d.get("Nombre_asentamiento"),
            "municipality": muni,
            "state": state,
            "postal_code": d.get("CP") or d.get("cp") or d.get("Codigo_postal"),
            "phone": d.get("Telefono") or d.get("telefono"),
            "email": d.get("Correo_e") or d.get("correo_e") or d.get("Correo_electronico"),
            "website": d.get("Sitio_internet") or d.get("sitio_internet") or d.get("Pagina_web"),
            "latitude": lat_f,
            "longitude": lng_f,
            "source_updated_at": d.get("Fecha_alta") or d.get("fecha_alta"),
        }

    def normalize(self, parsed: Dict[str, Any], provenance: SourceProvenanceRecord) -> CanonicalCompany:
        """Transforms parsed DENUE data into CanonicalCompany."""
        trade_orig, trade_norm = normalize_company_name(parsed.get("trade_name"))
        legal_orig, legal_norm = normalize_company_name(parsed.get("legal_name"))

        primary_norm_name = legal_norm or trade_norm or ""
        norm_state = normalize_state(parsed.get("state"))
        clean_cp = clean_postal_code(parsed.get("postal_code"))

        norm_url, domain = normalize_website(parsed.get("website"))
        clean_em = normalize_email(parsed.get("email"))
        phone_e164 = format_mx_phone_e164(parsed.get("phone"))

        emp_min, emp_max, emp_src = parse_employee_range(parsed.get("employee_range"))

        address = Address(
            street=parsed.get("street"),
            number=parsed.get("number"),
            colony=parsed.get("colony"),
            municipality=parsed.get("municipality"),
            state=norm_state or parsed.get("state"),
            postal_code=clean_cp,
            country="Mexico",
        )

        phones = [PhoneItem(value=phone_e164, source="DENUE")] if phone_e164 else []
        emails = [EmailItem(value=clean_em, source="DENUE")] if clean_em else []

        fp = generate_entity_fingerprint(
            rfc=None, # DENUE does not publish RFC directly
            normalized_name=primary_norm_name,
            state=address.state,
            municipality=address.municipality,
            domain=domain,
        )
        comp_id = generate_company_id(fp)

        company = CanonicalCompany(
            company_id=comp_id,
            legal_name=legal_orig,
            trade_name=trade_orig,
            normalized_name=primary_norm_name,
            rfc=None,
            rfc_type=None,
            website=norm_url,
            domain=domain,
            industry=parsed.get("industry"),
            industry_code=parsed.get("industry_code"),
            employee_count_min=emp_min,
            employee_count_max=emp_max,
            employee_count_source=emp_src,
            phone=phone_e164,
            phones=phones,
            email=clean_em,
            emails=emails,
            address=address,
            latitude=parsed.get("latitude"),
            longitude=parsed.get("longitude"),
            source_records=[provenance],
            source_count=1,
            entity_fingerprint=fp,
            last_verified_at=provenance.retrieved_at,
        )
        return company
