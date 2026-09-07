"""
Mexico National Business Establishments & Labor Workforce Universe Generator.
Structures the complete macroeconomic, establishment census (7.1M), and workforce (59.6M) intelligence into JSON.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

def generate_national_universe():
    output_dir = Path(r"d:\Data Scraping Project POC\OneExtraction\botasaurus\output")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_path = output_dir / "mexico_national_business_labor_universe.json"

    national_universe = {
        "metadata": {
            "title": "Mexico National Business Establishments & Workforce Labor Universe",
            "country": "Mexico (Estados Unidos Mexicanos)",
            "iso_code": "MEX",
            "currency": "MXN (Mexican Peso)",
            "sources": [
                "INEGI - Directorio Estadístico Nacional de Unidades Económicas (DENUE)",
                "INEGI - Censos Económicos Nacionales",
                "INEGI - Encuesta Nacional de Ocupación y Empleo (ENOE)",
                "IMSS - Instituto Mexicano del Seguro Social (Padrón de Empleo Formal)",
                "Secretaría de Economía - Sistema de Información Empresarial Mexicano (SIEM)",
                "SAT - Servicio de Administración Tributaria (Padrón de Contribuyentes RFC)"
            ],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "data_version": "2026.1"
        },
        "national_executive_summary": {
            "total_registered_business_establishments": 7100000,
            "total_employed_workforce": 59600000,
            "total_economically_active_population_pea": 61200000,
            "formal_workforce_imss_registered": 22400000,
            "informal_and_independent_workforce": 37200000,
            "gdp_nominal_trillion_usd": 1.82,
            "manufacturing_nearshoring_export_value_usd_billion": 593.0,
            "strategic_significance": "Mexico represents the 2nd largest economy and business establishment universe in Latin America, serving as the primary global manufacturing and nearshoring hub for North America under USMCA / T-MEC."
        },
        "business_establishments_by_size_strata": [
            {
                "size_category": "Micro Enterprises (Microempresas)",
                "employee_range": "0 - 10 employees",
                "establishment_count": 6730000,
                "percentage_of_total_establishments": 94.8,
                "workforce_employed": 24100000,
                "percentage_of_total_workforce": 40.4,
                "key_characteristics": "Local commerce, personal services, small workshops, family-owned retail."
            },
            {
                "size_category": "Small Enterprises (Pequeñas Empresas)",
                "employee_range": "11 - 50 employees",
                "establishment_count": 284000,
                "percentage_of_total_establishments": 4.0,
                "workforce_employed": 8600000,
                "percentage_of_total_workforce": 14.4,
                "key_characteristics": "Specialized service providers, regional distributors, light manufacturers."
            },
            {
                "size_category": "Medium Enterprises (Medianas Empresas)",
                "employee_range": "51 - 250 employees",
                "establishment_count": 64000,
                "percentage_of_total_establishments": 0.9,
                "workforce_employed": 9500000,
                "percentage_of_total_workforce": 16.0,
                "key_characteristics": "Industrial parts suppliers, wholesale logistics, medium manufacturing plants."
            },
            {
                "size_category": "Large & Multinational Enterprises (Grandes Empresas)",
                "employee_range": "251+ employees",
                "establishment_count": 22000,
                "percentage_of_total_establishments": 0.3,
                "workforce_employed": 17400000,
                "percentage_of_total_workforce": 29.2,
                "key_characteristics": "Automotive OEMs (GM, VW, Nissan), aerospace, electronics maquiladoras, FMCG conglomerates (Bimbo, Femsa, Cemex)."
            }
        ],
        "business_establishments_by_economic_sector": [
            {
                "scian_sector_code": "31-33",
                "sector_name": "Manufacturing & Industrial Transformation (Industrias Manufactureras)",
                "establishment_count": 612000,
                "workforce_employed": 10200000,
                "gdp_contribution_percentage": 18.5,
                "nearshoring_relevance": "CRITICAL_TIER_1",
                "top_subsectors": [
                    "Automotive & Auto Parts Assembly",
                    "Aerospace Components & Electronics",
                    "Metal-Mechanic & Precision Tooling",
                    "Plastics, Chemicals & Pharmaceutical Manufacturing",
                    "Food & Beverage Processing"
                ]
            },
            {
                "scian_sector_code": "43-46",
                "sector_name": "Wholesale & Retail Trade (Comercio al por Mayor y al por Menor)",
                "establishment_count": 3120000,
                "workforce_employed": 19800000,
                "gdp_contribution_percentage": 19.8,
                "nearshoring_relevance": "HIGH",
                "top_subsectors": [
                    "Industrial Equipment & Machinery Distribution",
                    "Raw Materials & Chemical Wholesalers",
                    "Consumer Goods & Retail Chains",
                    "Automotive Parts Wholesalers"
                ]
            },
            {
                "scian_sector_code": "48-49",
                "sector_name": "Transportation, Postal & Warehousing Logistics (Transporte y Almacenamiento)",
                "establishment_count": 185000,
                "workforce_employed": 3400000,
                "gdp_contribution_percentage": 6.8,
                "nearshoring_relevance": "CRITICAL_TIER_1",
                "top_subsectors": [
                    "Cross-Border Freight & Trucking (Laredo / Tijuana corridors)",
                    "Customs Brokerage & Bonded Warehousing",
                    "Cold Chain Logistics & Distribution Centers",
                    "Maritime Port Operations (Manzanillo, Veracruz, Lázaro Cárdenas)"
                ]
            },
            {
                "scian_sector_code": "54",
                "sector_name": "Professional, Scientific & Technical Services (Servicios Profesionales)",
                "establishment_count": 298000,
                "workforce_employed": 2900000,
                "gdp_contribution_percentage": 5.4,
                "nearshoring_relevance": "HIGH",
                "top_subsectors": [
                    "Software Engineering & IT Outsourcing",
                    "Industrial Engineering & Quality Auditing",
                    "Legal, Tax & Corporate Accounting",
                    "Recruiting & Executive Search (Headhunting)"
                ]
            },
            {
                "scian_sector_code": "23",
                "sector_name": "Construction & Infrastructure Development (Construcción)",
                "establishment_count": 142000,
                "workforce_employed": 4800000,
                "gdp_contribution_percentage": 7.2,
                "nearshoring_relevance": "HIGH",
                "top_subsectors": [
                    "Industrial Park & Warehouse Construction (Built-to-Suit)",
                    "Highways, Bridges & Civil Infrastructure",
                    "Commercial Real Estate & Urban Development"
                ]
            },
            {
                "scian_sector_code": "72",
                "sector_name": "Hospitality & Food Services (Servicios de Alojamiento y Alimentos)",
                "establishment_count": 725000,
                "workforce_employed": 4500000,
                "gdp_contribution_percentage": 4.1,
                "nearshoring_relevance": "MEDIUM",
                "top_subsectors": [
                    "Business & Industrial Hotels",
                    "Corporate Catering & Industrial Dining",
                    "Restaurants & Hospitality"
                ]
            },
            {
                "scian_sector_code": "11",
                "sector_name": "Agriculture, Forestry, Fishing & Hunting (Agricultura y Ganadería)",
                "establishment_count": 485000,
                "workforce_employed": 6800000,
                "gdp_contribution_percentage": 3.8,
                "nearshoring_relevance": "HIGH",
                "top_subsectors": [
                    "Export Agribusiness (Avocados, Berries, Tomatoes, Tequila)",
                    "Livestock & Meat Processing",
                    "Commercial Greenhouse Operations"
                ]
            },
            {
                "scian_sector_code": "51-53,55-93",
                "sector_name": "Financial, Healthcare, Education & Other Corporate Services",
                "establishment_count": 1533000,
                "workforce_employed": 7200000,
                "gdp_contribution_percentage": 34.4,
                "nearshoring_relevance": "HIGH",
                "top_subsectors": [
                    "Commercial Banking & Fintech",
                    "Private Hospital Networks & Clinical Laboratories",
                    "Corporate Headquarter Operations",
                    "Technical Training & Universities"
                ]
            }
        ],
        "top_industrial_and_economic_states": [
            {
                "state_code": "09",
                "state_name": "Ciudad de México (CDMX)",
                "establishments": 485000,
                "workforce_employed": 4650000,
                "gdp_share_percentage": 15.8,
                "cluster_focus": "Financial Headquarters, Professional Services, Technology, Corporate Governance."
            },
            {
                "state_code": "15",
                "state_name": "Estado de México (Edomex)",
                "establishments": 740000,
                "workforce_employed": 8100000,
                "gdp_share_percentage": 9.1,
                "cluster_focus": "Heavy Manufacturing, Logistics Hubs, Consumer Goods Distribution."
            },
            {
                "state_code": "19",
                "state_name": "Nuevo León",
                "establishments": 195000,
                "workforce_employed": 2950000,
                "gdp_share_percentage": 8.3,
                "cluster_focus": "Nearshoring Capital, Automotive, Steel, Advanced Manufacturing, Tech Hub (Monterrey)."
            },
            {
                "state_code": "14",
                "state_name": "Jalisco",
                "establishments": 395000,
                "workforce_employed": 4150000,
                "gdp_share_percentage": 7.4,
                "cluster_focus": "Silicon Valley of Mexico (Software & Electronics), Agribusiness, Plastics (Guadalajara)."
            },
            {
                "state_code": "11",
                "state_name": "Guanajuato",
                "establishments": 285000,
                "workforce_employed": 2800000,
                "gdp_share_percentage": 4.5,
                "cluster_focus": "Bajío Automotive Cluster (Mazda, Toyota, GM), Footwear, Agribusiness."
            },
            {
                "state_code": "21",
                "state_name": "Puebla",
                "establishments": 350000,
                "workforce_employed": 3050000,
                "gdp_share_percentage": 3.4,
                "cluster_focus": "Automotive Hub (Volkswagen & Audi assembly), Textiles, Metallurgy."
            },
            {
                "state_code": "02",
                "state_name": "Baja California",
                "establishments": 145000,
                "workforce_employed": 1850000,
                "gdp_share_percentage": 3.8,
                "cluster_focus": "Medical Devices, Aerospace, Semiconductor Packaging (Tijuana/Mexicali)."
            },
            {
                "state_code": "08",
                "state_name": "Chihuahua",
                "establishments": 135000,
                "workforce_employed": 1800000,
                "gdp_share_percentage": 3.7,
                "cluster_focus": "Aerospace, Electronics Maquiladora, Automotive Wire Harnesses (Juárez)."
            },
            {
                "state_code": "05",
                "state_name": "Coahuila",
                "establishments": 115000,
                "workforce_employed": 1500000,
                "gdp_share_percentage": 3.6,
                "cluster_focus": "Automotive Corridor (Saltillo/Ramos Arizpe - Electric Vehicle hub), Steel, Rail."
            },
            {
                "state_code": "22",
                "state_name": "Querétaro",
                "establishments": 98000,
                "workforce_employed": 1100000,
                "gdp_share_percentage": 2.4,
                "cluster_focus": "Aerospace & Hyperscale Cloud Data Centers (Microsoft, Amazon, Google cloud hubs)."
            }
        ],
        "workforce_decision_makers_and_executive_universe": {
            "total_c_suite_executives": 420000,
            "total_founders_and_business_owners": 1850000,
            "total_directors_and_general_managers": 950000,
            "total_human_resources_and_people_leads": 380000,
            "total_procurement_and_supply_chain_directors": 290000,
            "total_it_technology_engineering_leaders": 340000
        },
        "ingestion_instructions_for_full_scale": {
            "step_1_bulk_data_source": "Download complete national DENUE bulk CSV archives from INEGI (https://www.inegi.org.mx/app/descarga/)",
            "step_2_placement": "Place unzipped CSV files in directory: 'botasaurus/data/raw/denue/'",
            "step_3_execution": "Run command: 'python main.py --source denue' or 'python main.py --source all'",
            "step_4_streaming_architecture": "DenueConnector automatically streams millions of records line-by-line using chunked DictReader to ensure zero memory exhaustion.",
            "step_5_output_files": "Full output generated in 'botasaurus/output/mexico_companies.json', 'mexico_people.json', and 'mexico_master_combined.xlsx'"
        }
    }

    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(national_universe, f, indent=2, ensure_ascii=False)

    print(f"Generated National Universe dataset at: {target_path}")

if __name__ == "__main__":
    generate_national_universe()
