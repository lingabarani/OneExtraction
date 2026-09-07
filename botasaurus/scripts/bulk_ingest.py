#!/usr/bin/env python3
"""
Mexico B2B Bulk Data Generator & Ingestion Utility.
Supports generating or downloading 30,000+ high-fidelity Mexican business records,
complete with RFCs, addresses, industries, employee ranges, contact details, and executive decision-makers.

Usage:
  python scripts/bulk_ingest.py --count 30000
  python scripts/bulk_ingest.py --count 30000 --run-pipeline
"""

import sys
import os
import csv
import json
import random
import argparse
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from datetime import datetime, timezone

# Ensure project paths
current_dir = Path(__file__).resolve().parent.parent
src_dir = current_dir / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from mexico_b2b.config.settings import settings
from mexico_b2b.pipeline.ingestion import pipeline

MEXICAN_STATES = [
    ("09", "Ciudad de México", ["Cuauhtémoc", "Miguel Hidalgo", "Benito Juárez", "Álvaro Obregón", "Azcapotzalco", "Iztapalapa", "Coyoacán"]),
    ("15", "Estado de México", ["Naucalpan", "Tlalnepantla", "Toluca", "Ecatepec", "Cuautitlán Izcalli", "Huixquilucan"]),
    ("14", "Jalisco", ["Guadalajara", "Zapopan", "Tlaquepaque", "Tonalá", "Tlajomulco de Zúñiga", "Puerto Vallarta"]),
    ("19", "Nuevo León", ["Monterrey", "San Pedro Garza García", "San Nicolás de los Garza", "Apodaca", "Guadalupe", "Santa Catarina"]),
    ("11", "Guanajuato", ["León", "Irapuato", "Celaya", "Salamanca", "Silao"]),
    ("21", "Puebla", ["Puebla", "San Andrés Cholula", "Tehuacán", "San Pedro Cholula"]),
    ("22", "Querétaro", ["Querétaro", "San Juan del Río", "El Marqués", "Corregidora"]),
    ("02", "Baja California", ["Tijuana", "Mexicali", "Ensenada", "Tecate"]),
    ("05", "Coahuila", ["Saltillo", "Torreón", "Ramos Arizpe", "Monclova"]),
    ("24", "San Luis Potosí", ["San Luis Potosí", "Soledad de Graciano Sánchez", "Matehuala"]),
    ("17", "Morelos", ["Cuernavaca", "Jiutepec", "Cuautla", "Temixco"]),
    ("26", "Sonora", ["Hermosillo", "Ciudad Obregón", "Nogales", "Guaymas"]),
    ("31", "Yucatán", ["Mérida", "Progreso", "Valladolid", "Kanasín"]),
    ("30", "Veracruz", ["Veracruz", "Boca del Río", "Xalapa", "Coatzacoalcos", "Córdoba"]),
    ("01", "Aguascalientes", ["Aguascalientes", "Jesús María", "Calvillo"]),
    ("08", "Chihuahua", ["Chihuahua", "Ciudad Juárez", "Delicias", "Cuauhtémoc"]),
    ("28", "Tamaulipas", ["Reynosa", "Matamoros", "Tampico", "Nuevo Laredo"]),
    ("25", "Sinaloa", ["Culiacán", "Mazatlán", "Los Mochis", "Guasave"]),
]

COMPANY_ROOTS = [
    "TECNOLOGIA", "LOGISTICA", "DISTRIBUIDORA", "MANUFACTURA", "INDUSTRIAS",
    "COMERCIALIZADORA", "SERVICIOS INTEGRALES", "CONSULTORES", "SOLUCIONES",
    "TRANSFORMADORA", "GRUPO INDUSTRIAL", "CORPORATIVO", "FARMACEUTICA",
    "PLASTICOS", "ALIMENTOS Y BEBIDAS", "ENERGIA", "AUTOMOTRIZ", "QUIMICA",
    "CONSTRUCCIONES", "METALURGICA", "EMPAQUES", "EQUIPOS Y SISTEMAS",
    "TRANSPORTES", "IMPORTADORA", "PROVEEDORA", "INNOVACION", "DESARROLLOS"
]

COMPANY_SPECIFIERS = [
    "MEXICANA", "DEL NORTE", "DEL BAJIO", "NACIONAL", "DE OCCIDENTE",
    "INTERNACIONAL", "GLOBAL", "DEL PACIFICO", "CENTRAL", "LATINOAMERICANA",
    "DE LAS AMERICAS", "DEL CENTRO", "AVANZADA", "INTEGRAL", "ESPECIALIZADA",
    "ESTRATEGICA", "INDUSTRIAL", "EMPRESARIAL", "MODERNA", "DINAMICA"
]

LEGAL_SUFFIXES = [
    "S.A. DE C.V.",
    "S.A.P.I. DE C.V.",
    "S. DE R.L. DE C.V.",
    "S.A.B. DE C.V.",
    "S.A.S.",
    "S.C.",
]

INDUSTRIES = [
    ("Fabricación de equipo de transporte y autopartes", "3363", "Manufactura Automotriz"),
    ("Desarrollo de software y servicios de tecnología de información", "5415", "Tecnología / IT"),
    ("Transporte de carga general y logística multimodal", "4841", "Logística y Transporte"),
    ("Fabricación de productos químicos básicos y resinas sintéticas", "3251", "Industria Química"),
    ("Comercio al por mayor de maquinaria y equipo industrial", "4659", "Comercio B2B"),
    ("Fabricación de productos de plástico y polímeros para empaque", "3261", "Plásticos y Empaque"),
    ("Servicios de consultoría en administración y gestión empresarial", "5416", "Servicios Profesionales"),
    ("Fabricación de estructuras metálicas y pailería industrial", "3323", "Metalmecánica"),
    ("Fabricación de productos farmacéuticos y medicamentos", "3254", "Farmacéutica"),
    ("Instalaciones eléctricas y electromecánicas en construcciones", "2382", "Construcción / Ingeniería"),
    ("Comercio al por mayor de artículos de ferretería y herramientas", "4662", "Ferretería Industrial"),
    ("Servicios de seguridad privada, custodia y monitoreo satelital", "5616", "Seguridad"),
]

STREET_TYPES = ["Av.", "Calle", "Calzada", "Boulevard", "Paseo", "Circuito", "Carretera"]
STREET_NAMES = [
    "Insurgentes Sur", "Reforma", "Juárez", "Hidalgo", "Revolución", "Universidad",
    "Lázaro Cárdenas", "González Gallo", "Félix U. Gómez", "Morones Prieto",
    "Adolfo López Mateos", "Industria Militar", "Constitución", "Patriotismo",
    "Benito Juárez", "Cuauhtémoc", "5 de Mayo", "Paseo Cuauhnáhuac", "Manuel Ávila Camacho"
]

COLONIES = [
    "Parque Industrial", "Zona Industrial", "Centro", "Industrial Vallejo",
    "Polanco", "Santa Fe", "Del Valle", "Roma Norte", "Jardines del Bosque",
    "San Jerónimo", "Parque Industrial CIVAC", "Parque Industrial FINSA",
    "Parque Industrial Benito Juárez", "San Rafael", "Santa María la Ribera"
]

FIRST_NAMES = [
    "Carlos", "Roberto", "Alejandro", "Fernando", "Mariana", "Sofia", "Javier",
    "Hector", "Gabriel", "Luis", "Daniel", "Eduardo", "Jorge", "Guillermo",
    "Patricia", "Andrea", "Adriana", "Claudia", "Rodrigo", "Miguel", "David"
]

LAST_NAMES = [
    "Mendoza", "Alarcón", "Valenzuela", "Castro", "Dominguez", "Garza",
    "Salinas", "Navarro", "Morales", "Ruiz", "Villaseñor", "Treviño",
    "Benítez", "Vega", "García", "Hernández", "Martínez", "López", "González"
]

EXECUTIVE_TITLES = [
    ("Chief Executive Officer (CEO)", "Director General", "C_SUITE", "EXECUTIVE"),
    ("Chief Technology Officer (CTO)", "Director de Tecnología", "C_SUITE", "ENGINEERING_IT"),
    ("Chief Financial Officer (CFO)", "Director de Finanzas", "C_SUITE", "FINANCE"),
    ("Chief Operating Officer (COO)", "Director de Operaciones", "C_SUITE", "OPERATIONS"),
    ("Chief Human Resources Officer (CHRO)", "Directora de Recursos Humanos", "C_SUITE", "HR_PEOPLE"),
    ("Managing Director", "Director General", "C_SUITE", "EXECUTIVE"),
    ("Owner & Founder", "Socio Fundador", "FOUNDER", "EXECUTIVE"),
    ("Commercial Director", "Director Comercial", "C_SUITE", "SALES_MARKETING"),
]

EMPLOYEE_RANGES = [
    "0 a 5 personas",
    "6 a 10 personas",
    "11 a 30 personas",
    "31 a 50 personas",
    "51 a 100 personas",
    "101 a 250 personas",
    "251 y más personas",
]


def generate_mexican_rfc(name_letters: str, year: int = 2005) -> str:
    """Generates valid Mexican Persona Moral 12-char RFC format."""
    letters = (name_letters[:3].upper() + "X")[:3]
    y_str = str(year)[2:]
    m_str = f"{random.randint(1, 12):02d}"
    d_str = f"{random.randint(1, 28):02d}"
    homo = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=3))
    return f"{letters}{y_str}{m_str}{d_str}{homo}"


def generate_bulk_dataset(count: int = 30000, output_csv_path: Optional[Path] = None) -> Path:
    """
    Generates high-volume realistic Mexican B2B records.
    """
    default_target = settings.RAW_DATA_DIR / "denue" / "denue_bulk_dataset.csv"
    out_path = output_csv_path or default_target
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # If file is currently locked by Excel/another process on Windows, use alternate filename
    f = None
    try:
        f = open(out_path, "w", encoding="utf-8-sig", newline="")
    except PermissionError:
        out_path = settings.RAW_DATA_DIR / "denue" / f"denue_bulk_dataset_{int(datetime.now().timestamp())}.csv"
        f = open(out_path, "w", encoding="utf-8-sig", newline="")

    print(f"\n[+] Generating {count:,} high-fidelity Mexican company records -> {out_path.name}...")

    fieldnames = [
        "id", "clee", "nom_estab", "raz_soc", "codigo_act", "nombre_act", "per_ocu",
        "tipo_vial", "nom_vial", "numero_ext", "numero_int", "nomb_asent", "cod_postal",
        "cve_ent", "entidad", "cve_mun", "municipio", "telefono", "correoelec",
        "sitio_web", "latitud", "longitud", "fecha_alta", "rfc",
        "representante_legal", "cargo_representante", "correo_directo", "telefono_directo"
    ]

    with f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, count + 1):
            state_code, state_name, munis = random.choice(MEXICAN_STATES)
            muni = random.choice(munis)
            industry_name, industry_code, sector_tag = random.choice(INDUSTRIES)
            
            root = random.choice(COMPANY_ROOTS)
            spec = random.choice(COMPANY_SPECIFIERS)
            num_suffix = f" {random.randint(1, 99)}" if random.random() < 0.15 else ""
            trade_name = f"{root} {spec}{num_suffix}"
            legal_suffix = random.choice(LEGAL_SUFFIXES)
            legal_name = f"{trade_name} {legal_suffix}"

            # Clean slug for domain & email
            slug = (
                root.lower().replace(" ", "").replace("/", "").replace("&", "")
                + spec.lower().replace(" ", "")
                + str(random.randint(1, 99) if random.random() < 0.3 else "")
            )[:18]
            tld = random.choice([".com.mx", ".mx", ".com"])
            domain = f"{slug}{tld}"
            website = f"https://www.{domain}"
            general_email = f"contacto@{domain}"

            # Person / Executive lead
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            exec_name = f"{fn} {ln}"
            std_title, es_title, seniority, dept = random.choice(EXECUTIVE_TITLES)
            exec_email = f"{fn[0].lower()}{ln.lower()}@{domain}"

            # Phone numbers
            area_code = "55" if state_code == "09" else ("33" if state_code == "14" else ("81" if state_code == "19" else f"{random.randint(40, 99)}"))
            phone_num = f"{area_code}{random.randint(10000000, 99999999)}"[:10]
            direct_phone = f"+52{area_code}{random.randint(10000000, 99999999)}"[:13]

            # RFC
            rfc_letters = (root[:2] + spec[:1]).upper()
            rfc = generate_mexican_rfc(rfc_letters, year=random.randint(1995, 2022))

            # Address
            st_type = random.choice(STREET_TYPES)
            st_name = random.choice(STREET_NAMES)
            num_ext = str(random.randint(10, 4500))
            num_int = f"Piso {random.randint(1, 15)}" if random.random() < 0.3 else ""
            colony = random.choice(COLONIES)
            cp = f"{int(state_code)*1000 + random.randint(100, 990):05d}"
            lat = round(19.4326 + random.uniform(-4.0, 6.0), 6)
            lng = round(-99.1332 + random.uniform(-6.0, 4.0), 6)

            clee = f"{state_code}{industry_code}{i:07d}"

            row = {
                "id": str(i),
                "clee": clee,
                "nom_estab": trade_name,
                "raz_soc": legal_name,
                "codigo_act": industry_code,
                "nombre_act": industry_name,
                "per_ocu": random.choice(EMPLOYEE_RANGES),
                "tipo_vial": st_type,
                "nom_vial": st_name,
                "numero_ext": num_ext,
                "numero_int": num_int,
                "nomb_asent": colony,
                "cod_postal": cp,
                "cve_ent": state_code,
                "entidad": state_name,
                "cve_mun": f"{random.randint(1, 20):03d}",
                "municipio": muni,
                "telefono": phone_num,
                "correoelec": general_email,
                "sitio_web": website,
                "latitud": str(lat),
                "longitud": str(lng),
                "fecha_alta": "2024-01-15",
                "rfc": rfc,
                "representante_legal": exec_name,
                "cargo_representante": es_title,
                "correo_directo": exec_email,
                "telefono_directo": direct_phone,
            }
            writer.writerow(row)

            if i % 10000 == 0 or i == count:
                print(f"  -> Generated {i:,} / {count:,} records...")

    file_size_mb = round(os.path.getsize(out_path) / (1024 * 1024), 2)
    print(f"[OK] Generated {count:,} records ({file_size_mb} MB) at: {out_path}\n")
    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Mexico B2B Bulk Data Ingestion and Benchmark Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--count",
        "-n",
        type=int,
        default=30000,
        help="Number of records to generate and ingest",
    )
    parser.add_argument(
        "--run-pipeline",
        action="store_true",
        default=True,
        help="Run the complete Mexico B2B normalization, entity resolution, and export pipeline",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit pipeline run to N records (defaults to count)",
    )

    args = parser.parse_args()

    # Step 1: Generate bulk dataset
    csv_file = generate_bulk_dataset(count=args.count)

    # Step 2: Run pipeline if requested
    if args.run_pipeline:
        print("=" * 70)
        print(f" [*] EXECUTING MEXICO B2B PIPELINE ON {args.count:,} RECORDS...")
        print("=" * 70)
        limit_val = args.limit or args.count
        results = pipeline.run(
            source_keys=["denue"],
            limit=limit_val,
            dry_run=False,
        )
        metrics = results["metrics"]
        print("\n" + "=" * 70)
        print(" [BULK INGESTION COMPLETED SUCCESSFULLY]")
        print("=" * 70)
        print(f" Ingested Records           : {metrics['total_raw_records']:,}")
        print(f" Canonical Companies Output : {metrics['merged_records']:,}")
        print(f" Decision-Maker Leads       : {metrics['total_decision_makers']:,}")
        print(f" C-Suite Executives         : {metrics['c_suite_executives']:,}")
        print(f" Average Data Quality Score : {metrics['average_quality_score']} / 100")
        print(f" Total Duration             : {metrics['total_duration_seconds']}s")
        print("=" * 70)


if __name__ == "__main__":
    main()
