from __future__ import annotations

import json
import re
import shutil
from statistics import mean
from pathlib import Path
from typing import Any, Dict, List

from ryp_framework.automation.contracts import ArtifactSpec, QSeriesEntry
from ryp_framework.automation.registry import QSeriesRegistryStore
from ryp_framework.utils.paths import get_framework_workspace_path


class SerieQBuilder:
    def __init__(self, store: QSeriesRegistryStore) -> None:
        self.store = store

    @staticmethod
    def default_registry_path() -> Path:
        return get_framework_workspace_path("11_OPERACION", "runtime", "q_series_registry.json")

    @staticmethod
    def default_output_dir() -> Path:
        return get_framework_workspace_path("04_SERIES_Q", "Q_ENTRIES", create_parent=True)

    @staticmethod
    def default_discoveries_dir() -> Path:
        return get_framework_workspace_path("01_ENTRADAS", "DESCUBRIMIENTOS", create_parent=True)

    def scaffold_from_source(self, source: str, output_dir: Path | None = None, title: str | None = None) -> Dict[str, Any]:
        resolved_source_path = self._resolve_source_path(source)
        canonical_source_path, staged_support_files = self._stage_discovery_source(resolved_source_path)
        discovery_payload = self._load_source_payload(canonical_source_path)
        promoted = self.promote_discovery_source(
            canonical_source_path=canonical_source_path,
            discovery_payload=discovery_payload,
            staged_support_files=staged_support_files,
            output_dir=output_dir,
            title=title,
            limit=1,
        )
        first_entry = promoted[0] if promoted else None
        return {
            "ok": True,
            "mode": "single_candidate",
            "q_id": first_entry["q_id"] if first_entry else None,
            "registry_path": str(self.store.path),
            "source_path": str(canonical_source_path),
            "workspace_root": str(get_framework_workspace_path(create_parent=True)),
            "entry_count": len(promoted),
            "entries": promoted,
            "artifacts": first_entry["artifacts"] if first_entry else [],
        }

    def scaffold_all_candidates_from_source(
        self,
        source: str,
        output_dir: Path | None = None,
        title_prefix: str | None = None,
    ) -> Dict[str, Any]:
        resolved_source_path = self._resolve_source_path(source)
        canonical_source_path, staged_support_files = self._stage_discovery_source(resolved_source_path)
        discovery_payload = self._load_source_payload(canonical_source_path)
        promoted = self.promote_discovery_source(
            canonical_source_path=canonical_source_path,
            discovery_payload=discovery_payload,
            staged_support_files=staged_support_files,
            output_dir=output_dir,
            title=title_prefix,
            limit=None,
        )
        return {
            "ok": True,
            "mode": "all_candidates",
            "registry_path": str(self.store.path),
            "source_path": str(canonical_source_path),
            "workspace_root": str(get_framework_workspace_path(create_parent=True)),
            "entry_count": len(promoted),
            "entries": promoted,
        }

    def promote_discovery_source(
        self,
        canonical_source_path: Path,
        discovery_payload: Dict[str, Any],
        staged_support_files: list[Path],
        output_dir: Path | None,
        title: str | None,
        limit: int | None,
    ) -> list[Dict[str, Any]]:
        registry = self.store.load()
        output_dir = output_dir or self.default_output_dir()
        grouped_candidates = self._group_candidates(discovery_payload)
        if limit is not None:
            grouped_candidates = grouped_candidates[:limit]

        promoted_entries: list[Dict[str, Any]] = []
        for group in grouped_candidates:
            candidate_key = str(group["candidate_key"])
            if registry.has_entry(str(canonical_source_path), candidate_key):
                continue
            q_number = registry.next_q_number()
            entry_bundle = self._create_entry_bundle(
                q_number=q_number,
                canonical_source_path=canonical_source_path,
                staged_support_files=staged_support_files,
                output_dir=output_dir,
                discovery_payload=discovery_payload,
                candidate_group=group,
                title=title,
            )
            registry.append(entry_bundle["entry"])
            promoted_entries.append(entry_bundle["result"])

        if promoted_entries:
            self.store.save(registry)
        return promoted_entries

    @staticmethod
    def _build_markdown(q_id: str, title: str, source: str, summary: Dict[str, Any]) -> str:
        top_candidates = summary.get("top_candidates") or []
        top_candidate_lines = [
            f"- {candidate['label']} | confianza={candidate['confianza']:.2f} | recomendacion={candidate['recomendacion_serie_q']}"
            for candidate in top_candidates
        ] or ["- sin candidatos normalizados"]

        metric_lines = [
            f"- {name}: {value:.4f}" if isinstance(value, float) else f"- {name}: {value}"
            for name, value in (summary.get("metricas_resumen") or {}).items()
        ] or ["- sin metricas resumidas"]

        corpus_lines = [f"- {item}" for item in (summary.get("corpus_fuente") or [])] or ["- sin corpus identificado"]

        return "\n".join(
            [
                f"# {q_id} Readiness",
                "",
                f"- title: {title}",
                f"- source: {source}",
                "- status: DRAFT",
                f"- estado_validacion_origen: {summary.get('estado_validacion', 'DESCONOCIDO')}",
                f"- ciclo_origen: {summary.get('ciclo', 'N/A')}",
                f"- corpus_analizados: {summary.get('corpus_analizados', 'N/A')}",
                f"- recomendacion_base: {summary.get('recomendacion_base', 'N/A')}",
                "",
                "## Summary",
                "",
                "Draft generated from a real discovery payload by `ryp_framework.automation.SerieQBuilder`.",
                summary.get("razon_principal", "Sin razon principal sintetizada."),
                "",
                "## Metrics",
                "",
                *metric_lines,
                "",
                "## Top Candidates",
                "",
                *top_candidate_lines,
                "",
                "## Corpus Fuente",
                "",
                *corpus_lines,
                "",
                "## Evidence",
                "",
                f"- source artifact: {source}",
                f"- propiedades_candidatas: {summary.get('propiedades_detectadas', 0)}",
                "",
                "## Pending validation",
                "",
                "- metrics extraction",
                "- readiness consolidation",
                "- stage-gate review",
            ]
        )

    def _resolve_source_path(self, source: str) -> Path:
        source_path = Path(source)
        if source_path.exists():
            return source_path
        internal_path = self.default_discoveries_dir() / source
        if internal_path.exists():
            return internal_path
        return source_path

    def _create_entry_bundle(
        self,
        q_number: int,
        canonical_source_path: Path,
        staged_support_files: list[Path],
        output_dir: Path,
        discovery_payload: Dict[str, Any],
        candidate_group: Dict[str, Any],
        title: str | None,
    ) -> Dict[str, Any]:
        q_id = f"Q{q_number:03d}"
        effective_title = title or candidate_group["suggested_title"] or canonical_source_path.stem
        safe_slug = self._slugify(effective_title or f"q_{q_number:03d}")
        discovery_summary = self._summarize_discovery(
            payload=discovery_payload,
            source_path=canonical_source_path,
            primary_group=candidate_group,
        )

        output_dir.mkdir(parents=True, exist_ok=True)
        q_bundle_dir = output_dir / q_id
        q_bundle_dir.mkdir(parents=True, exist_ok=True)
        md_path = q_bundle_dir / f"{q_id}_READINESS.md"
        json_path = q_bundle_dir / f"{q_id}_EVIDENCE.json"
        manifest_path = q_bundle_dir / f"{q_id}_MANIFEST.json"
        decision_path = q_bundle_dir / f"{q_id}_DECISION.json"

        evidence_payload = {
            "q_id": q_id,
            "source": str(canonical_source_path),
            "title": effective_title,
            "builder_state": "draft",
            "pipeline_stage": "INGESTED",
            "candidate_key": candidate_group["candidate_key"],
            "discovery_summary": discovery_summary,
            "staged_support_files": [str(path) for path in staged_support_files],
        }

        decision_payload = {
            "q_id": q_id,
            "decision": "PENDING",
            "notes": "",
            "updated_at": "",
            "updated_by": "",
        }
        json_path.write_text(json.dumps(evidence_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        decision_path.write_text(json.dumps(decision_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        md_path.write_text(
            self._build_markdown(
                q_id=q_id,
                title=effective_title,
                source=str(canonical_source_path),
                summary=discovery_summary,
            ),
            encoding="utf-8",
        )

        manifest_payload = {
            "q_id": q_id,
            "title": effective_title,
            "bundle_dir": str(q_bundle_dir),
            "status": "DRAFT",
            "pipeline_stage": "INGESTED",
            "candidate_key": candidate_group["candidate_key"],
            "source": str(canonical_source_path),
            "artifacts": {
                "readiness": str(md_path),
                "evidence": str(json_path),
                "decision": str(decision_path),
                "source": str(canonical_source_path),
                "staged_support": [str(path) for path in staged_support_files],
            },
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2), encoding="utf-8")

        artifacts = [
            ArtifactSpec(artifact_id=f"{q_id}_source", artifact_type="discovery_json", path=str(canonical_source_path)),
            ArtifactSpec(artifact_id=f"{q_id}_readiness", artifact_type="readiness_markdown", path=str(md_path)),
            ArtifactSpec(artifact_id=f"{q_id}_evidence", artifact_type="evidence_json", path=str(json_path)),
            ArtifactSpec(artifact_id=f"{q_id}_manifest", artifact_type="q_manifest", path=str(manifest_path)),
            ArtifactSpec(artifact_id=f"{q_id}_decision", artifact_type="decision_stub", path=str(decision_path)),
            *[
                ArtifactSpec(
                    artifact_id=f"{q_id}_support_{index + 1}",
                    artifact_type="discovery_support",
                    path=str(path),
                )
                for index, path in enumerate(staged_support_files)
            ],
        ]
        entry = QSeriesEntry(
            q_number=q_number,
            title=effective_title,
            source=str(canonical_source_path),
            evidence=[str(canonical_source_path), *[str(path) for path in staged_support_files]],
            artifacts=artifacts,
            metadata={
                "slug": safe_slug,
                "estado_validacion": discovery_summary.get("estado_validacion"),
                "metricas_resumen": discovery_summary.get("metricas_resumen"),
                "recomendacion_base": discovery_summary.get("recomendacion_base"),
                "workspace_root": str(get_framework_workspace_path(create_parent=True)),
                "candidate_key": candidate_group["candidate_key"],
                "candidate_count": candidate_group["count"],
                "candidate_group": candidate_group,
                "bundle_dir": str(q_bundle_dir),
                "manifest_path": str(manifest_path),
                "decision_path": str(decision_path),
                "pipeline_stage": "INGESTED",
            },
        )
        return {
            "entry": entry,
            "result": {
                "q_id": entry.q_id,
                "title": effective_title,
                "candidate_key": candidate_group["candidate_key"],
                "source_path": str(canonical_source_path),
                "discovery_summary": discovery_summary,
                "artifacts": [artifact.to_dict() for artifact in artifacts],
            },
        }

    def _stage_discovery_source(self, source_path: Path) -> tuple[Path, list[Path]]:
        if not source_path.exists():
            return source_path, []
        internal_dir = self.default_discoveries_dir()
        internal_dir.mkdir(parents=True, exist_ok=True)
        canonical_source_path = internal_dir / source_path.name
        if source_path.resolve() != canonical_source_path.resolve():
            shutil.copy2(source_path, canonical_source_path)
        else:
            canonical_source_path = source_path

        staged_support_files: list[Path] = []
        support_md = source_path.with_suffix(".md")
        if support_md.exists():
            internal_md_path = internal_dir / support_md.name
            if support_md.resolve() != internal_md_path.resolve():
                shutil.copy2(support_md, internal_md_path)
            else:
                internal_md_path = support_md
            staged_support_files.append(internal_md_path)
        return canonical_source_path, staged_support_files

    @staticmethod
    def _load_source_payload(source_path: Path) -> Dict[str, Any]:
        if source_path.exists() and source_path.suffix.lower() == ".json":
            return json.loads(source_path.read_text(encoding="utf-8"))
        return {"raw_source": str(source_path)}

    def _summarize_discovery(
        self,
        payload: Dict[str, Any],
        source_path: Path,
        primary_group: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        candidates = payload.get("propiedades_candidatas") or []
        normalized_candidates = []
        metric_samples: dict[str, list[float]] = {}
        corpus_fuente = set()
        familias = set()

        for candidate in candidates:
            metricas = candidate.get("metricas") or {}
            for key, value in metricas.items():
                if isinstance(value, (int, float)):
                    metric_samples.setdefault(key, []).append(float(value))
            corpus = candidate.get("corpus_fuente")
            if corpus:
                corpus_fuente.add(str(corpus))
            for familia in candidate.get("familias_activas") or []:
                familias.add(str(familia))
            normalized_candidates.append(
                {
                    "id": str(candidate.get("id") or "SIN_ID"),
                    "label": str(candidate.get("label") or candidate.get("tipo") or "sin_label"),
                    "tipo": str(candidate.get("tipo") or "sin_tipo"),
                    "confianza": float(candidate.get("confianza") or 0.0),
                    "recomendacion_serie_q": str(candidate.get("recomendacion_serie_q") or "SIN_RECOMENDACION"),
                    "razon": str(candidate.get("razon") or ""),
                }
            )

        grouped_candidates = self._group_candidates(payload)
        top_candidates = grouped_candidates[:3]
        top_candidate = primary_group or (top_candidates[0] if top_candidates else None)
        suggested_title = None
        recomendacion_base = None
        razon_principal = None

        if top_candidate:
            recomendacion_base = top_candidate["recomendacion_serie_q"]
            suggested_title = self._title_from_recommendation(recomendacion_base) or top_candidate["label"]
            razon_principal = top_candidate["razon"]

        metric_summary = {
            key: mean(values)
            for key, values in sorted(metric_samples.items())
            if values
        }

        return {
            "source_name": source_path.name,
            "timestamp": payload.get("timestamp"),
            "ciclo": payload.get("ciclo"),
            "corpus_analizados": payload.get("corpus_analizados"),
            "estado_validacion": payload.get("estado_validacion") or "SIN_ESTADO",
            "propiedades_detectadas": len(candidates),
            "recomendacion_base": recomendacion_base,
            "suggested_title": suggested_title,
            "razon_principal": razon_principal,
            "familias_activas": sorted(familias),
            "corpus_fuente": sorted(corpus_fuente),
            "metricas_resumen": metric_summary,
            "top_candidates": top_candidates,
        }

    def _group_candidates(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        grouped: dict[str, dict[str, Any]] = {}
        for candidate in payload.get("propiedades_candidatas") or []:
            recommendation = str(candidate.get("recomendacion_serie_q") or candidate.get("label") or candidate.get("tipo") or "SIN_RECOMENDACION")
            candidate_key = self._slugify(recommendation)
            bucket = grouped.setdefault(
                candidate_key,
                {
                    "candidate_key": candidate_key,
                    "recomendacion_serie_q": recommendation,
                    "label": str(candidate.get("label") or candidate.get("tipo") or "sin_label"),
                    "tipo": str(candidate.get("tipo") or "sin_tipo"),
                    "confianzas": [],
                    "metric_samples": {},
                    "familias_activas": set(),
                    "corpus_fuente": set(),
                    "razones": [],
                    "ids": set(),
                    "count": 0,
                },
            )
            bucket["count"] += 1
            bucket["confianzas"].append(float(candidate.get("confianza") or 0.0))
            bucket["ids"].add(str(candidate.get("id") or "SIN_ID"))
            if candidate.get("razon"):
                bucket["razones"].append(str(candidate.get("razon")))
            if candidate.get("corpus_fuente"):
                bucket["corpus_fuente"].add(str(candidate.get("corpus_fuente")))
            for familia in candidate.get("familias_activas") or []:
                bucket["familias_activas"].add(str(familia))
            for key, value in (candidate.get("metricas") or {}).items():
                if isinstance(value, (int, float)):
                    bucket["metric_samples"].setdefault(key, []).append(float(value))

        grouped_candidates: list[Dict[str, Any]] = []
        for candidate_key, bucket in grouped.items():
            metricas = {
                key: mean(values)
                for key, values in sorted(bucket["metric_samples"].items())
                if values
            }
            confianza = mean(bucket["confianzas"]) if bucket["confianzas"] else 0.0
            grouped_candidates.append(
                {
                    "candidate_key": candidate_key,
                    "id": sorted(bucket["ids"])[0] if bucket["ids"] else "SIN_ID",
                    "label": bucket["label"],
                    "tipo": bucket["tipo"],
                    "confianza": confianza,
                    "recomendacion_serie_q": bucket["recomendacion_serie_q"],
                    "razon": bucket["razones"][0] if bucket["razones"] else "",
                    "familias_activas": sorted(bucket["familias_activas"]),
                    "corpus_fuente": sorted(bucket["corpus_fuente"]),
                    "metricas": metricas,
                    "count": bucket["count"],
                    "suggested_title": self._title_from_recommendation(bucket["recomendacion_serie_q"]) or bucket["label"],
                }
            )

        grouped_candidates.sort(
            key=lambda item: (item["confianza"], item["count"], len(item["familias_activas"])),
            reverse=True,
        )
        return grouped_candidates

    @staticmethod
    def _title_from_recommendation(recommendation: str | None) -> str | None:
        if not recommendation:
            return None
        cleaned = recommendation.replace("Q1_SERIE_XXX_", "").replace("Q_SERIE_", "")
        cleaned = cleaned.replace("_", " ").strip()
        return cleaned.title() if cleaned else None

    @staticmethod
    def _slugify(text: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
        return slug or "q-entry"