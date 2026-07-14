from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from ryp_framework.automation.contracts import utc_now_iso
from ryp_framework.automation.builder import SerieQBuilder
from ryp_framework.automation.profiles import resolve_profile
from ryp_framework.language import tokenize
from ryp_framework.utils.paths import get_framework_workspace_path


_FAMILY_KEYWORDS = {
    "experiencia": {"experiencia", "vivencia", "practica", "practica", "aprendizaje"},
    "filosofia": {"filosofia", "ontologia", "epistemologia", "logos", "ser"},
    "computacion": {"algoritmo", "codigo", "software", "sistema", "datos", "ia"},
    "psicologia": {"mente", "emocion", "cognitivo", "psicologia", "conducta"},
    "puente_ryp": {"ryp", "perspectiva", "realidad", "relacional", "sam"},
    "biociencias": {"biologia", "organismo", "autopoiesis", "vida", "ecologia"},
}

_ACADEMIC_MARKERS = {
    "citation_tokens": {
        "et", "al", "doi", "vol", "pp", "revista", "journal", "estudio", "referencia", "bibliografia"
    },
    "method_markers": {
        "metodo", "metodologia", "muestra", "analisis", "hipotesis", "resultado", "discusion", "conclusion"
    },
    "argument_markers": {
        "por", "tanto", "sin", "embargo", "ademas", "evidencia", "demuestra", "sugiere", "implica"
    },
}

_EDUCATION_MARKERS = {
    "explica", "ejemplo", "aprende", "didactico", "guia", "paso", "concepto", "clase", "objetivo"
}

_EDITORIAL_MARKERS = {
    "tono", "estilo", "narrativa", "fluidez", "claridad", "lectura", "coherencia", "redaccion"
}

_APPLIED_RESEARCH_MARKERS = {
    "prototipo", "validacion", "implementacion", "campo", "experimento", "resultado", "impacto", "operativo"
}


@dataclass(slots=True)
class DiscoveryIngestor:
    @staticmethod
    def default_txt_input_dir() -> Path:
        return get_framework_workspace_path("01_ENTRADAS", "TXT", create_parent=True)

    @staticmethod
    def default_discoveries_dir() -> Path:
        return SerieQBuilder.default_discoveries_dir()

    def ingest_directory(
        self,
        input_dir: Path | None = None,
        output_dir: Path | None = None,
        pattern: str = "*.txt",
        limit_files: int | None = None,
        profile: str = "general",
    ) -> Dict[str, Any]:
        txt_root = input_dir or self.default_txt_input_dir()
        discoveries_root = output_dir or self.default_discoveries_dir()
        txt_root.mkdir(parents=True, exist_ok=True)
        discoveries_root.mkdir(parents=True, exist_ok=True)

        files = sorted(txt_root.glob(pattern))
        if limit_files is not None:
            files = files[:limit_files]

        ingested: List[Dict[str, Any]] = []
        for file_path in files:
            ingested.append(self.ingest_file(file_path=file_path, output_dir=discoveries_root, profile=profile))

        profile_cfg = resolve_profile(profile)
        return {
            "ok": True,
            "profile": profile_cfg.key,
            "input_dir": str(txt_root),
            "output_dir": str(discoveries_root),
            "processed_files": len(files),
            "discovery_files": [item["discovery_json"] for item in ingested],
            "files": ingested,
        }

    def ingest_file(self, file_path: Path, output_dir: Path | None = None, profile: str = "general") -> Dict[str, Any]:
        discoveries_root = output_dir or self.default_discoveries_dir()
        discoveries_root.mkdir(parents=True, exist_ok=True)

        text = self._read_text(file_path)
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
        safe_stem = re.sub(r"[^a-zA-Z0-9]+", "_", file_path.stem).strip("_") or "entrada"
        discovery_name = f"{safe_stem}_{text_hash}_DESCUBRIMIENTOS"
        discovery_json_path = discoveries_root / f"{discovery_name}.json"
        discovery_md_path = discoveries_root / f"{discovery_name}.md"

        profile_cfg = resolve_profile(profile)
        metrics = self._compute_metrics(text, profile=profile_cfg.key)
        candidates = self._build_candidates(metrics=metrics, source_name=file_path.name, profile=profile_cfg.key)

        payload = {
            "timestamp": utc_now_iso(),
            "ciclo": 1,
            "corpus_analizados": 1,
            "propiedades_candidatas": candidates,
            "estado_validacion": "EN_REVISION",
            "decision_usuario": None,
            "fecha_decision": None,
            "notas_usuario": "",
            "perfil_usuario": profile_cfg.key,
            "source_txt": str(file_path),
            "source_hash": text_hash,
            "metricas_globales": metrics,
        }
        discovery_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        discovery_md_path.write_text(self._build_markdown(payload), encoding="utf-8")

        return {
            "source_txt": str(file_path),
            "source_hash": text_hash,
            "profile": profile_cfg.key,
            "discovery_json": str(discovery_json_path),
            "discovery_md": str(discovery_md_path),
            "candidate_count": len(candidates),
        }

    @staticmethod
    def _read_text(file_path: Path) -> str:
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return file_path.read_text(encoding=encoding)
            except Exception:
                continue
        return file_path.read_text(errors="ignore")

    def _compute_metrics(self, text: str, profile: str = "general") -> Dict[str, Any]:
        tokens = tokenize(text)
        token_count = len(tokens)
        sentence_chunks = [chunk.strip() for chunk in re.split(r"[.!?]+", text) if chunk.strip()]
        sentence_count = max(1, len(sentence_chunks))
        unique_tokens = len(set(tokens))
        unique_ratio = (unique_tokens / token_count) if token_count else 0.0

        trajectory = self._build_stable_trajectory(tokens)
        sam_vector = trajectory.mean(axis=0)
        sam_vector = sam_vector / (np.sum(sam_vector) + 1e-9)
        vec_entropy = float(-np.sum(sam_vector * np.log(sam_vector + 1e-8)))
        closure_index = max(0.0, min(1.0, 1.0 - (vec_entropy / 1.2)))

        autopoiesis_index = max(
            0.0,
            min(1.0, 0.45 * unique_ratio + 0.35 * min(1.0, token_count / 300.0) + 0.20 * min(1.0, sentence_count / 40.0)),
        )
        epistemic_gap_index = abs(autopoiesis_index - closure_index)

        if len(trajectory) > 1:
            trajectory_delta = np.linalg.norm(np.diff(trajectory, axis=0), axis=1)
            continuity_index = max(0.0, min(1.0, 1.0 - float(np.mean(trajectory_delta)) * 2.0))
            boundary_coherence_index = max(0.0, min(1.0, 1.0 - float(np.std(trajectory_delta)) * 2.0))
            reentry_similarity = max(0.0, min(1.0, float(np.dot(trajectory[0], trajectory[-1]))))
        else:
            continuity_index = 1.0
            boundary_coherence_index = 1.0
            reentry_similarity = 1.0

        families = self._detect_families(tokens)
        family_coverage = len(families) / 6.0
        semantic_density = min(1.0, (token_count / sentence_count) / 24.0)
        lexical_complexity = self._clamp(0.65 * unique_ratio + 0.35 * semantic_density)

        metrics = {
            "sentence_count": sentence_count,
            "token_count": token_count,
            "unique_tokens": unique_tokens,
            "unique_ratio": unique_ratio,
            "avg_sentence_tokens": token_count / sentence_count,
            "autopoiesis_index": autopoiesis_index,
            "closure_index": closure_index,
            "epistemic_gap_index": epistemic_gap_index,
            "reentry_similarity": reentry_similarity,
            "continuity_index": continuity_index,
            "boundary_coherence_index": boundary_coherence_index,
            "family_count": len(families),
            "family_coverage": self._clamp(family_coverage),
            "semantic_density": semantic_density,
            "lexical_complexity": lexical_complexity,
            "familias_activas": families,
        }
        metrics.update(self._compute_profile_markers(tokens=tokens, sentence_count=sentence_count, profile=profile))
        return metrics

    def _compute_profile_markers(self, tokens: List[str], sentence_count: int, profile: str) -> Dict[str, float]:
        if profile == "academico":
            return self._compute_academic_metrics(tokens=tokens, sentence_count=sentence_count)
        if profile == "educativo":
            return self._compute_educational_metrics(tokens=tokens, sentence_count=sentence_count)
        if profile == "editorial":
            return self._compute_editorial_metrics(tokens=tokens, sentence_count=sentence_count)
        if profile == "investigacion_aplicada":
            return self._compute_applied_research_metrics(tokens=tokens, sentence_count=sentence_count)
        return {}

    def _compute_academic_metrics(self, tokens: List[str], sentence_count: int) -> Dict[str, float]:
        token_count = max(1, len(tokens))
        token_set = {str(token).lower() for token in tokens}

        citation_hits = len(token_set.intersection(_ACADEMIC_MARKERS["citation_tokens"]))
        method_hits = len(token_set.intersection(_ACADEMIC_MARKERS["method_markers"]))
        argument_hits = len(token_set.intersection(_ACADEMIC_MARKERS["argument_markers"]))

        citation_density = self._clamp((citation_hits / token_count) * 20.0)
        method_coverage = self._clamp(method_hits / 8.0)
        argumentation_index = self._clamp(argument_hits / 9.0)
        paragraph_pressure = self._clamp((token_count / max(1, sentence_count)) / 30.0)
        academic_signal_score = self._clamp(
            0.35 * citation_density + 0.30 * method_coverage + 0.20 * argumentation_index + 0.15 * paragraph_pressure
        )

        return {
            "citation_density": citation_density,
            "method_coverage": method_coverage,
            "argumentation_index": argumentation_index,
            "paragraph_pressure": paragraph_pressure,
            "academic_signal_score": academic_signal_score,
        }

    def _compute_educational_metrics(self, tokens: List[str], sentence_count: int) -> Dict[str, float]:
        token_count = max(1, len(tokens))
        token_set = {str(token).lower() for token in tokens}
        marker_hits = len(token_set.intersection(_EDUCATION_MARKERS))
        didactic_density = self._clamp((marker_hits / token_count) * 25.0)
        pedagogic_flow = self._clamp((token_count / max(1, sentence_count)) / 20.0)
        educational_signal_score = self._clamp(0.55 * didactic_density + 0.45 * pedagogic_flow)
        return {
            "didactic_density": didactic_density,
            "pedagogic_flow": pedagogic_flow,
            "educational_signal_score": educational_signal_score,
        }

    def _compute_editorial_metrics(self, tokens: List[str], sentence_count: int) -> Dict[str, float]:
        token_count = max(1, len(tokens))
        token_set = {str(token).lower() for token in tokens}
        marker_hits = len(token_set.intersection(_EDITORIAL_MARKERS))
        style_signal = self._clamp((marker_hits / token_count) * 30.0)
        readability_signal = self._clamp(1.0 - abs((token_count / max(1, sentence_count)) - 18.0) / 18.0)
        editorial_signal_score = self._clamp(0.60 * readability_signal + 0.40 * style_signal)
        return {
            "style_signal": style_signal,
            "readability_signal": readability_signal,
            "editorial_signal_score": editorial_signal_score,
        }

    def _compute_applied_research_metrics(self, tokens: List[str], sentence_count: int) -> Dict[str, float]:
        token_count = max(1, len(tokens))
        token_set = {str(token).lower() for token in tokens}
        marker_hits = len(token_set.intersection(_APPLIED_RESEARCH_MARKERS))
        empirical_density = self._clamp((marker_hits / token_count) * 30.0)
        operational_resolution = self._clamp((token_count / max(1, sentence_count)) / 22.0)
        applied_signal_score = self._clamp(0.50 * empirical_density + 0.50 * operational_resolution)
        return {
            "empirical_density": empirical_density,
            "operational_resolution": operational_resolution,
            "applied_signal_score": applied_signal_score,
        }

    @staticmethod
    def _stable_token_vector(token: str) -> np.ndarray:
        normalized = str(token or "").strip().lower()
        digest = hashlib.sha256(normalized.encode("utf-8")).digest()
        values = np.array([digest[0], digest[1], digest[2]], dtype=float) + 1.0
        values = values / np.sum(values)
        return values

    def _build_stable_trajectory(self, tokens: List[str]) -> np.ndarray:
        if not tokens:
            return np.array([[1 / 3, 1 / 3, 1 / 3]], dtype=float)
        vectors = [self._stable_token_vector(token) for token in tokens]
        return np.array(vectors, dtype=float)

    @staticmethod
    def _detect_families(tokens: List[str]) -> List[str]:
        token_set = {str(token).lower() for token in tokens}
        families = []
        for family_name, keywords in _FAMILY_KEYWORDS.items():
            if token_set.intersection(keywords):
                families.append(family_name)
        return families

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, value))

    def _build_candidates(self, metrics: Dict[str, Any], source_name: str, profile: str = "general") -> List[Dict[str, Any]]:
        family_count = int(metrics.get("family_count") or 0)
        families = metrics.get("familias_activas") or []
        family_coverage = float(metrics.get("family_coverage") or 0.0)
        lexical_complexity = float(metrics.get("lexical_complexity") or 0.0)
        semantic_density = float(metrics.get("semantic_density") or 0.0)
        continuity = float(metrics.get("continuity_index") or 0.0)
        reentry = float(metrics.get("reentry_similarity") or 0.0)
        closure = float(metrics.get("closure_index") or 0.0)
        gap = float(metrics.get("epistemic_gap_index") or 0.0)
        autopoiesis = float(metrics.get("autopoiesis_index") or 0.0)
        translational_cohesion = self._clamp(0.55 * continuity + 0.45 * reentry)
        novelty_pressure = self._clamp(0.60 * (1.0 - closure) + 0.40 * lexical_complexity)

        integration_conf = self._clamp(
            0.20 + 0.38 * family_coverage + 0.25 * autopoiesis + 0.17 * (1.0 - gap)
        )
        translation_conf = self._clamp(
            0.18 + 0.30 * translational_cohesion + 0.22 * semantic_density + 0.20 * family_coverage + 0.10 * lexical_complexity
        )
        closure_alert_conf = self._clamp(0.20 + 0.55 * novelty_pressure + 0.25 * (1.0 - closure))

        if profile == "academico":
            citation_density = float(metrics.get("citation_density") or 0.0)
            method_coverage = float(metrics.get("method_coverage") or 0.0)
            argumentation_index = float(metrics.get("argumentation_index") or 0.0)
            academic_signal_score = float(metrics.get("academic_signal_score") or 0.0)
            integration_conf = self._clamp(0.72 * integration_conf + 0.28 * academic_signal_score)
            translation_conf = self._clamp(0.74 * translation_conf + 0.26 * argumentation_index)
            closure_alert_conf = self._clamp(0.80 * closure_alert_conf + 0.20 * (1.0 - method_coverage))
        elif profile == "educativo":
            educational_signal = float(metrics.get("educational_signal_score") or 0.0)
            integration_conf = self._clamp(0.84 * integration_conf + 0.16 * educational_signal)
            translation_conf = self._clamp(0.70 * translation_conf + 0.30 * educational_signal)
        elif profile == "editorial":
            editorial_signal = float(metrics.get("editorial_signal_score") or 0.0)
            translation_conf = self._clamp(0.65 * translation_conf + 0.35 * editorial_signal)
            closure_alert_conf = self._clamp(0.85 * closure_alert_conf + 0.15 * (1.0 - editorial_signal))
        elif profile == "investigacion_aplicada":
            applied_signal = float(metrics.get("applied_signal_score") or 0.0)
            integration_conf = self._clamp(0.70 * integration_conf + 0.30 * applied_signal)
            closure_alert_conf = self._clamp(0.75 * closure_alert_conf + 0.25 * (1.0 - applied_signal))

        candidates = [
            {
                "id": "PROP_001",
                "tipo": "subcapa_emergente",
                "label": "subcapa_integracion_multi_dominio",
                "confianza": round(integration_conf, 4),
                "metricas": {
                    "autopoiesis": round(float(metrics["autopoiesis_index"]), 6),
                    "closure": round(float(metrics["closure_index"]), 6),
                    "epistemic_gap": round(float(metrics["epistemic_gap_index"]), 6),
                },
                "familias_activas": families,
                "razon": f"Integracion detectada en {family_count} familias activas",
                "recomendacion_serie_q": "Q1_SERIE_XXX_INTEGRACION_MULTI_DOMINIO",
                "corpus_fuente": source_name,
                "senales": {
                    "family_coverage": round(family_coverage, 6),
                    "autopoiesis_index": round(autopoiesis, 6),
                    "epistemic_gap_index": round(gap, 6),
                },
            },
            {
                "id": "PROP_002",
                "tipo": "subcapa_emergente",
                "label": "subcapa_traduccion_operativa",
                "confianza": round(translation_conf, 4),
                "metricas": {
                    "autopoiesis": round(float(metrics["autopoiesis_index"]), 6),
                    "closure": round(float(metrics["closure_index"]), 6),
                    "epistemic_gap": round(float(metrics["epistemic_gap_index"]), 6),
                },
                "familias_activas": families,
                "razon": "Capacidad de traduccion inferida por continuidad y diversidad semantica",
                "recomendacion_serie_q": "Q1_SERIE_XXX_TRADUCCION_OPERATIVA",
                "corpus_fuente": source_name,
                "senales": {
                    "translational_cohesion": round(translational_cohesion, 6),
                    "semantic_density": round(semantic_density, 6),
                    "lexical_complexity": round(lexical_complexity, 6),
                },
            },
        ]

        if profile == "academico":
            candidates.append(
                {
                    "id": "PROP_005",
                    "tipo": "subcapa_emergente",
                    "label": "subcapa_argumentacion_metodologica",
                    "confianza": round(
                        self._clamp(
                            0.25
                            + 0.40 * float(metrics.get("method_coverage") or 0.0)
                            + 0.35 * float(metrics.get("argumentation_index") or 0.0)
                        ),
                        4,
                    ),
                    "metricas": {
                        "academic_signal_score": round(float(metrics.get("academic_signal_score") or 0.0), 6),
                        "method_coverage": round(float(metrics.get("method_coverage") or 0.0), 6),
                        "argumentation_index": round(float(metrics.get("argumentation_index") or 0.0), 6),
                    },
                    "familias_activas": families,
                    "razon": "Perfil academico activo: estructura argumental y metodologica detectada",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_ARGUMENTACION_METODOLOGICA",
                    "corpus_fuente": source_name,
                    "senales": {
                        "citation_density": round(float(metrics.get("citation_density") or 0.0), 6),
                        "method_coverage": round(float(metrics.get("method_coverage") or 0.0), 6),
                        "argumentation_index": round(float(metrics.get("argumentation_index") or 0.0), 6),
                    },
                }
            )
        elif profile == "educativo":
            candidates.append(
                {
                    "id": "PROP_006",
                    "tipo": "subcapa_emergente",
                    "label": "subcapa_claridad_pedagogica",
                    "confianza": round(self._clamp(0.30 + 0.70 * float(metrics.get("educational_signal_score") or 0.0)), 4),
                    "metricas": {
                        "didactic_density": round(float(metrics.get("didactic_density") or 0.0), 6),
                        "pedagogic_flow": round(float(metrics.get("pedagogic_flow") or 0.0), 6),
                    },
                    "familias_activas": families,
                    "razon": "Perfil educativo activo: explicabilidad y progresion detectadas",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_CLARIDAD_PEDAGOGICA",
                    "corpus_fuente": source_name,
                    "senales": {
                        "educational_signal_score": round(float(metrics.get("educational_signal_score") or 0.0), 6),
                    },
                }
            )
        elif profile == "editorial":
            candidates.append(
                {
                    "id": "PROP_007",
                    "tipo": "subcapa_emergente",
                    "label": "subcapa_coherencia_editorial",
                    "confianza": round(self._clamp(0.25 + 0.75 * float(metrics.get("editorial_signal_score") or 0.0)), 4),
                    "metricas": {
                        "style_signal": round(float(metrics.get("style_signal") or 0.0), 6),
                        "readability_signal": round(float(metrics.get("readability_signal") or 0.0), 6),
                    },
                    "familias_activas": families,
                    "razon": "Perfil editorial activo: cohesión de estilo y legibilidad detectadas",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_COHERENCIA_EDITORIAL",
                    "corpus_fuente": source_name,
                    "senales": {
                        "editorial_signal_score": round(float(metrics.get("editorial_signal_score") or 0.0), 6),
                    },
                }
            )
        elif profile == "investigacion_aplicada":
            candidates.append(
                {
                    "id": "PROP_008",
                    "tipo": "subcapa_emergente",
                    "label": "subcapa_evidencia_operativa",
                    "confianza": round(self._clamp(0.30 + 0.70 * float(metrics.get("applied_signal_score") or 0.0)), 4),
                    "metricas": {
                        "empirical_density": round(float(metrics.get("empirical_density") or 0.0), 6),
                        "operational_resolution": round(float(metrics.get("operational_resolution") or 0.0), 6),
                    },
                    "familias_activas": families,
                    "razon": "Perfil de investigacion aplicada activo: evidencia operativa detectada",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_EVIDENCIA_OPERATIVA",
                    "corpus_fuente": source_name,
                    "senales": {
                        "applied_signal_score": round(float(metrics.get("applied_signal_score") or 0.0), 6),
                    },
                }
            )

        if closure < 0.35:
            candidates.append(
                {
                    "id": "PROP_003",
                    "tipo": "metrica_novel",
                    "label": "closure_index_bajo_sin_precedente",
                    "confianza": round(closure_alert_conf, 4),
                    "metricas": {
                        "sentence_count": metrics["sentence_count"],
                        "token_count": metrics["token_count"],
                        "autopoiesis_index": round(float(metrics["autopoiesis_index"]), 6),
                        "closure_index": round(float(metrics["closure_index"]), 6),
                        "epistemic_gap_index": round(float(metrics["epistemic_gap_index"]), 6),
                        "reentry_similarity": round(float(metrics["reentry_similarity"]), 6),
                        "continuity_index": round(float(metrics["continuity_index"]), 6),
                        "boundary_coherence_index": round(float(metrics["boundary_coherence_index"]), 6),
                    },
                    "familias_activas": families,
                    "razon": "Valor de closure_index bajo, requiere evaluacion",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_CLOSURE_BAJO",
                    "corpus_fuente": source_name,
                    "senales": {
                        "novelty_pressure": round(novelty_pressure, 6),
                        "closure_index": round(closure, 6),
                    },
                }
            )

        if lexical_complexity >= 0.65 and metrics["token_count"] >= 40:
            diversity_conf = self._clamp(0.35 + 0.40 * lexical_complexity + 0.25 * semantic_density)
            candidates.append(
                {
                    "id": "PROP_004",
                    "tipo": "metrica_novel",
                    "label": "diversidad_lexica_alta",
                    "confianza": round(diversity_conf, 4),
                    "metricas": {
                        "token_count": metrics["token_count"],
                        "unique_tokens": metrics["unique_tokens"],
                        "unique_ratio": round(float(metrics["unique_ratio"]), 6),
                        "lexical_complexity": round(lexical_complexity, 6),
                        "semantic_density": round(semantic_density, 6),
                    },
                    "familias_activas": families,
                    "razon": "Complejidad lexical alta detectada en corpus de entrada",
                    "recomendacion_serie_q": "Q1_SERIE_XXX_DIVERSIDAD_LEXICA",
                    "corpus_fuente": source_name,
                    "senales": {
                        "lexical_complexity": round(lexical_complexity, 6),
                        "semantic_density": round(semantic_density, 6),
                    },
                }
            )

        return candidates

    @staticmethod
    def _build_markdown(payload: Dict[str, Any]) -> str:
        lines = [
            f"# Reporte de Descubrimientos - {Path(str(payload.get('source_txt', 'entrada'))).name}",
            "",
            f"- timestamp: {payload.get('timestamp')}",
            f"- estado: {payload.get('estado_validacion')}",
            f"- perfil_usuario: {payload.get('perfil_usuario', 'general')}",
            f"- source_txt: {payload.get('source_txt')}",
            "",
            "## Metricas Globales",
            "",
            f"- token_count: {payload.get('metricas_globales', {}).get('token_count')}",
            f"- sentence_count: {payload.get('metricas_globales', {}).get('sentence_count')}",
            f"- family_coverage: {payload.get('metricas_globales', {}).get('family_coverage')}",
            "",
            "## Propiedades Detectadas",
            "",
        ]
        profile = str(payload.get("perfil_usuario") or "general").lower()
        metrics = payload.get("metricas_globales") or {}
        if profile == "academico":
            lines.extend(
                [
                    "## Resumen Academico",
                    "",
                    f"- academic_signal_score: {metrics.get('academic_signal_score')}",
                    f"- citation_density: {metrics.get('citation_density')}",
                    f"- method_coverage: {metrics.get('method_coverage')}",
                    f"- argumentation_index: {metrics.get('argumentation_index')}",
                    "",
                ]
            )
        elif profile == "educativo":
            lines.extend(
                [
                    "## Resumen Educativo",
                    "",
                    f"- educational_signal_score: {metrics.get('educational_signal_score')}",
                    f"- didactic_density: {metrics.get('didactic_density')}",
                    f"- pedagogic_flow: {metrics.get('pedagogic_flow')}",
                    "",
                ]
            )
        elif profile == "editorial":
            lines.extend(
                [
                    "## Resumen Editorial",
                    "",
                    f"- editorial_signal_score: {metrics.get('editorial_signal_score')}",
                    f"- style_signal: {metrics.get('style_signal')}",
                    f"- readability_signal: {metrics.get('readability_signal')}",
                    "",
                ]
            )
        elif profile == "investigacion_aplicada":
            lines.extend(
                [
                    "## Resumen Investigacion Aplicada",
                    "",
                    f"- applied_signal_score: {metrics.get('applied_signal_score')}",
                    f"- empirical_density: {metrics.get('empirical_density')}",
                    f"- operational_resolution: {metrics.get('operational_resolution')}",
                    "",
                ]
            )
        for candidate in payload.get("propiedades_candidatas") or []:
            lines.extend(
                [
                    f"### {candidate.get('id')}: {candidate.get('label')}",
                    "",
                    f"- tipo: {candidate.get('tipo')}",
                    f"- confianza: {candidate.get('confianza')}",
                    f"- recomendacion: {candidate.get('recomendacion_serie_q')}",
                    f"- razon: {candidate.get('razon')}",
                    f"- corpus: {candidate.get('corpus_fuente')}",
                    "",
                ]
            )
        return "\n".join(lines)