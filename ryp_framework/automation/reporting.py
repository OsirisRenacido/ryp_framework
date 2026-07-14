from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from ryp_framework.automation.builder import SerieQBuilder
from ryp_framework.automation.registry import QSeriesRegistryStore
from ryp_framework.automation.contracts import utc_now_iso


class UniversalReportBuilder:
    def __init__(self, store: QSeriesRegistryStore) -> None:
        self.store = store

    @staticmethod
    def default_reports_dir() -> Path:
        return SerieQBuilder.default_registry_path().parent / "reports"

    def build_report(
        self,
        profile: str,
        discoveries_dir: Path | None = None,
        reports_dir: Path | None = None,
    ) -> Dict[str, Any]:
        registry = self.store.load()
        discoveries_root = discoveries_dir or SerieQBuilder.default_discoveries_dir()
        reports_root = reports_dir or self.default_reports_dir()
        reports_root.mkdir(parents=True, exist_ok=True)

        discovery_files = sorted(discoveries_root.glob("*_DESCUBRIMIENTOS.json"))
        latest_discovery = discovery_files[-1] if discovery_files else None
        latest_payload: Dict[str, Any] = {}
        if latest_discovery and latest_discovery.exists():
            latest_payload = json.loads(latest_discovery.read_text(encoding="utf-8"))

        status_counts: Dict[str, int] = {}
        for entry in registry.entries:
            status_counts[entry.status] = status_counts.get(entry.status, 0) + 1

        top_candidates = []
        for candidate in (latest_payload.get("propiedades_candidatas") or [])[:3]:
            top_candidates.append(
                {
                    "id": candidate.get("id"),
                    "label": candidate.get("label"),
                    "confidence": candidate.get("confianza"),
                    "recommendation": candidate.get("recomendacion_serie_q"),
                }
            )

        report_payload = {
            "ok": True,
            "generated_at": utc_now_iso(),
            "profile": profile,
            "entry_count": len(registry.entries),
            "next_q_number": registry.next_q_number(),
            "status_counts": status_counts,
            "latest_discovery": str(latest_discovery) if latest_discovery else None,
            "latest_source": latest_payload.get("source_txt"),
            "top_candidates": top_candidates,
        }

        report_name = f"UNIVERSAL_REPORT_{profile}_{utc_now_iso().replace(':', '').replace('-', '')}.md"
        report_path = reports_root / report_name
        report_path.write_text(self._build_markdown(report_payload), encoding="utf-8")

        report_payload["report_path"] = str(report_path)
        return report_payload

    @staticmethod
    def _build_markdown(payload: Dict[str, Any]) -> str:
        lines = [
            "# RYP Universal Report",
            "",
            f"- generated_at: {payload.get('generated_at')}",
            f"- profile: {payload.get('profile')}",
            f"- entry_count: {payload.get('entry_count')}",
            f"- next_q_number: {payload.get('next_q_number')}",
            f"- latest_discovery: {payload.get('latest_discovery')}",
            f"- latest_source: {payload.get('latest_source')}",
            "",
            "## Estado Serie Q",
            "",
        ]
        status_counts = payload.get("status_counts") or {}
        if not status_counts:
            lines.append("- sin entradas en registro")
            lines.append("")
        else:
            for key in sorted(status_counts.keys()):
                lines.append(f"- {key}: {status_counts[key]}")
            lines.append("")

        lines.extend(["## Top Candidates", ""])
        candidates = payload.get("top_candidates") or []
        if not candidates:
            lines.append("- sin candidatos en el ultimo discovery")
            lines.append("")
        else:
            for candidate in candidates:
                lines.append(
                    f"- {candidate.get('id')}: {candidate.get('label')} "
                    f"(confianza={candidate.get('confidence')}, q={candidate.get('recommendation')})"
                )
            lines.append("")

        lines.extend(
            [
                "## Resumen Ejecutivo",
                "",
                "- El reporte universal entrega una lectura corta para usuarios no tecnicos y auditabilidad para perfiles tecnicos.",
                "- Use `ryp analyze --profile <perfil>` para ejecutar pipeline y generar este reporte automaticamente.",
            ]
        )
        return "\n".join(lines)
