"""
Pipeline Orchestrator for Mexico B2B Open-Data Ingestion & Decision-Maker Enrichment.
Coordinates connector execution, deduplication, resolution, merging, executive lead extraction, and exports.
"""

import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from ..config.sources import sources_registry, SourceConfig
from ..connectors import get_connector
from ..models.company import CanonicalCompany
from ..models.person import DecisionMaker
from .deduplication import deduplication_engine
from .merger import merge_engine
from .person_enrichment import person_enrichment_engine
from ..storage.output import output_manager
from ..utils.logging import logger


class IngestionPipeline:
    """
    Main pipeline orchestrator for ingesting, validating, resolving, merging,
    and enriching Mexican business & executive decision-maker data.
    """

    def __init__(self):
        self.sources_registry = sources_registry
        self.dedup_engine = deduplication_engine
        self.merger = merge_engine
        self.person_engine = person_enrichment_engine
        self.output_mgr = output_manager

    def run(
        self,
        source_keys: Optional[List[str]] = None,
        limit: Optional[int] = None,
        dry_run: bool = False,
        verify_emails: bool = False,
    ) -> Dict[str, Any]:
        """
        Executes the ingestion pipeline.
        
        Args:
            source_keys: List of source keys to run (e.g. ['denue', 'siem']). If None or ['all'], runs all enabled.
            limit: Record limit per source (useful for sampling / POC).
            dry_run: If True, validates configuration and runs sample without writing full files to disk.
            verify_emails: If True, performs active MX inspection on executive email permutations.
        """
        start_time = time.time()
        logger.info(
            "Starting Mexico B2B Ingestion & Executive Enrichment Pipeline",
            sources=source_keys or "all",
            limit=limit,
            dry_run=dry_run,
        )

        enabled_sources = self.sources_registry.get_enabled_sources()
        if source_keys and "all" not in [s.lower() for s in source_keys]:
            selected_sources = {
                k: cfg for k, cfg in enabled_sources.items()
                if k.lower() in [s.lower() for s in source_keys]
            }
        else:
            selected_sources = enabled_sources

        all_valid_records: List[CanonicalCompany] = []
        all_invalid_reports: List[Dict[str, Any]] = []
        source_statuses: Dict[str, Any] = {}
        records_per_source: Dict[str, int] = {}

        # Stage 1: Ingest each selected source independently (fault-tolerant)
        for key, config in selected_sources.items():
            src_start = time.time()
            try:
                connector = get_connector(key, config)
                valid_recs, invalid_recs = connector.ingest(limit=limit)

                all_valid_records.extend(valid_recs)
                all_invalid_reports.extend(invalid_recs)
                records_per_source[config.name] = len(valid_recs)

                duration = round(time.time() - src_start, 2)
                source_statuses[config.name] = {
                    "status": "SUCCESS",
                    "records_ingested": len(valid_recs),
                    "invalid_records": len(invalid_recs),
                    "duration_seconds": duration,
                    "error": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            except Exception as e:
                duration = round(time.time() - src_start, 2)
                logger.error(
                    f"Source {config.name} encountered an error but pipeline will continue",
                    source=config.name,
                    error=str(e),
                )
                source_statuses[config.name] = {
                    "status": "FAILED",
                    "records_ingested": 0,
                    "invalid_records": 0,
                    "duration_seconds": duration,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

        # Stage 2: Deduplication and Entity Resolution
        clusters, review_queue, duplicate_count = self.dedup_engine.deduplicate(all_valid_records)

        # Stage 3: Source-Priority Merging
        merged_companies = self.merger.merge_all_clusters(clusters)

        # Stage 4: Decision-Maker & Executive Enrichment Layer (Layer 2)
        all_decision_makers: List[DecisionMaker] = []
        for company in merged_companies:
            executives = self.person_engine.extract_and_enrich_decision_makers(company)
            company.decision_makers = executives
            all_decision_makers.extend(executives)

        # Stage 5: Calculate Quality and Summary Metrics
        total_score = sum(c.data_quality_score for c in merged_companies)
        avg_quality_score = round(total_score / len(merged_companies), 2) if merged_companies else 0.0

        c_suite_count = sum(1 for dm in all_decision_makers if dm.seniority_level == "C_SUITE")
        founder_count = sum(1 for dm in all_decision_makers if dm.seniority_level == "FOUNDER")
        hr_count = sum(1 for dm in all_decision_makers if dm.department == "HR_PEOPLE")
        verified_emails = sum(1 for dm in all_decision_makers if dm.email_status in ("VERIFIED", "PROBABLE"))
        outlook_count = sum(1 for dm in all_decision_makers if dm.mail_provider == "MICROSOFT_365_OUTLOOK")
        google_count = sum(1 for dm in all_decision_makers if dm.mail_provider == "GOOGLE_WORKSPACE")

        metrics = {
            "total_raw_records": len(all_valid_records) + len(all_invalid_reports),
            "valid_records": len(all_valid_records),
            "invalid_records": len(all_invalid_reports),
            "duplicates": duplicate_count,
            "merged_records": len(merged_companies),
            "total_decision_makers": len(all_decision_makers),
            "c_suite_executives": c_suite_count,
            "founders_and_owners": founder_count,
            "hr_and_people_leads": hr_count,
            "deliverable_work_emails": verified_emails,
            "microsoft_365_outlook_domains": outlook_count,
            "google_workspace_domains": google_count,
            "records_in_review_queue": len(review_queue),
            "records_per_source": records_per_source,
            "records_with_email": sum(1 for c in merged_companies if c.email),
            "records_with_phone": sum(1 for c in merged_companies if c.phone),
            "records_with_website": sum(1 for c in merged_companies if c.website),
            "records_with_rfc": sum(1 for c in merged_companies if c.rfc),
            "records_with_coordinates": sum(1 for c in merged_companies if c.latitude is not None),
            "average_quality_score": avg_quality_score,
            "total_duration_seconds": round(time.time() - start_time, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        validation_report = {
            "summary_metrics": metrics,
            "source_statuses": source_statuses,
            "invalid_records_sample": all_invalid_reports[:100],
        }

        # Stage 6: Output Generation (Unless dry_run)
        if not dry_run:
            self.output_mgr.write_json(merged_companies)
            self.output_mgr.write_csv(merged_companies)
            self.output_mgr.write_xlsx(merged_companies)
            self.output_mgr.write_people_json(all_decision_makers)
            self.output_mgr.write_people_csv(all_decision_makers)
            self.output_mgr.write_people_xlsx(all_decision_makers)
            self.output_mgr.write_validation_report(validation_report)
            self.output_mgr.write_source_status(source_statuses)
        else:
            logger.info("Dry run mode active: validation report prepared without overwriting production exports.")

        logger.info(
            "Pipeline finished",
            merged_companies=metrics["merged_records"],
            decision_makers=metrics["total_decision_makers"],
            c_suite=metrics["c_suite_executives"],
            avg_score=metrics["average_quality_score"],
            duplicates=metrics["duplicates"],
            duration=metrics["total_duration_seconds"],
        )

        return {
            "metrics": metrics,
            "source_statuses": source_statuses,
            "merged_companies": merged_companies,
            "decision_makers": all_decision_makers,
            "validation_report": validation_report,
        }


pipeline = IngestionPipeline()
