from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List

from ryp_framework.automation.builder import SerieQBuilder
from ryp_framework.automation.ingest import DiscoveryIngestor
from ryp_framework.automation.registry import QSeriesRegistryStore
from ryp_framework.automation.contracts import utc_now_iso


@dataclass(slots=True)
class AutomationCycleRunner:
    store: QSeriesRegistryStore

    @classmethod
    def default(cls) -> "AutomationCycleRunner":
        return cls(store=QSeriesRegistryStore(SerieQBuilder.default_registry_path()))

    def run(
        self,
        discoveries_dir: Path | None = None,
        output_dir: Path | None = None,
        limit_files: int | None = None,
    ) -> Dict[str, Any]:
        builder = SerieQBuilder(self.store)
        discoveries_root = discoveries_dir or SerieQBuilder.default_discoveries_dir()
        output_root = output_dir or SerieQBuilder.default_output_dir()
        files = sorted(discoveries_root.glob("*.json"))
        if limit_files is not None:
            files = files[:limit_files]

        processed: List[Dict[str, Any]] = []
        for source_file in files:
            result = builder.scaffold_all_candidates_from_source(
                source=str(source_file),
                output_dir=output_root,
            )
            processed.append(
                {
                    "source": str(source_file),
                    "entry_count": result["entry_count"],
                    "entries": result["entries"],
                }
            )

        transition_report = self._apply_validation_gates()

        return {
            "ok": True,
            "discoveries_dir": str(discoveries_root),
            "output_dir": str(output_root),
            "processed_files": len(files),
            "created_entries": sum(item["entry_count"] for item in processed),
            "transitions": transition_report["transitions"],
            "status_counts": transition_report["status_counts"],
            "files": processed,
        }

    def run_all(
        self,
        input_txt_dir: Path | None = None,
        discoveries_dir: Path | None = None,
        output_dir: Path | None = None,
        pattern: str = "*.txt",
        limit_files: int | None = None,
        profile: str = "general",
    ) -> Dict[str, Any]:
        ingestor = DiscoveryIngestor()
        ingest_report = ingestor.ingest_directory(
            input_dir=input_txt_dir,
            output_dir=discoveries_dir,
            pattern=pattern,
            limit_files=limit_files,
            profile=profile,
        )
        cycle_report = self.run(
            discoveries_dir=Path(str(ingest_report["output_dir"])),
            output_dir=output_dir,
            limit_files=None,
        )
        return {
            "ok": True,
            "pipeline": "txt_to_q",
            "profile": profile,
            "ingest": ingest_report,
            "cycle": cycle_report,
        }

    def _apply_validation_gates(self) -> Dict[str, Any]:
        registry = self.store.load()
        transitions: List[Dict[str, str]] = []

        for entry in registry.entries:
            previous_status = entry.status
            decision = self._load_decision(entry)
            next_status = self._resolve_next_status(entry=entry, decision=decision)
            if next_status != previous_status:
                entry.status = next_status
                entry.updated_at = utc_now_iso()
                transitions.append(
                    {
                        "q_id": entry.q_id,
                        "from": previous_status,
                        "to": next_status,
                    }
                )

            entry.metadata["decision"] = decision
            entry.metadata["pipeline_stage"] = self._pipeline_stage_for_status(next_status)

            manifest_path = Path(str(entry.metadata.get("manifest_path") or ""))
            if manifest_path.exists():
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
                payload["status"] = entry.status
                payload["pipeline_stage"] = entry.metadata["pipeline_stage"]
                payload["updated_at"] = entry.updated_at
                payload["decision"] = decision
                manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        if transitions:
            self.store.save(registry)

        status_counts: Dict[str, int] = {}
        for entry in registry.entries:
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1

        return {
            "transitions": transitions,
            "status_counts": status_counts,
        }

    @staticmethod
    def _resolve_next_status(entry, decision: str) -> str:
        normalized = (decision or "").strip().upper()
        if normalized in {"REJECTED", "RECHAZA"}:
            return "REJECTED"
        if normalized in {"APPROVED", "VALIDO", "ACEPTA"}:
            return "READY_FOR_REVIEW"

        candidate_group = entry.metadata.get("candidate_group") or {}
        confidence = float(candidate_group.get("confianza") or 0.0)
        candidate_count = int(entry.metadata.get("candidate_count") or 0)
        if confidence >= 0.85 and candidate_count >= 2:
            return "READY_FOR_REVIEW"
        if confidence >= 0.70:
            return "UNDER_REVIEW"
        return "NEEDS_CURATION"

    @staticmethod
    def _pipeline_stage_for_status(status: str) -> str:
        mapping = {
            "DRAFT": "INGESTED",
            "UNDER_REVIEW": "VALIDATION_IN_PROGRESS",
            "READY_FOR_REVIEW": "PROMOTED",
            "REJECTED": "CLOSED",
            "NEEDS_CURATION": "CURATION_REQUIRED",
        }
        return mapping.get(status, "INGESTED")

    @staticmethod
    def _load_decision(entry) -> str:
        decision_path = Path(str(entry.metadata.get("decision_path") or ""))
        if not decision_path.exists():
            return "PENDING"
        try:
            payload = json.loads(decision_path.read_text(encoding="utf-8"))
        except Exception:
            return "PENDING"
        return str(payload.get("decision") or "PENDING")