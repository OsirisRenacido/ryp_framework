from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from ryp_framework.automation.ingest import DiscoveryIngestor
from ryp_framework.automation.registry import QSeriesRegistryStore
from ryp_framework.automation.reporting import UniversalReportBuilder
from ryp_framework.automation.runner import AutomationCycleRunner


class PipelineContractTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["RYP_FRAMEWORK_STANDALONE"] = "1"
        self._tmp = tempfile.TemporaryDirectory(prefix="ryp_contract_")
        self.tmp_path = Path(self._tmp.name)
        self.input_dir = self.tmp_path / "input_txt"
        self.discoveries_dir = self.tmp_path / "discoveries"
        self.output_dir = self.tmp_path / "q_entries"
        self.registry_path = self.tmp_path / "runtime" / "q_series_registry.json"
        self.input_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_sample_txt(self, name: str = "sample.txt") -> Path:
        path = self.input_dir / name
        path.write_text(
            "La realidad y la perspectiva articulan un sistema semantico. "
            "El aprendizaje conecta experiencia, psicologia y computacion.",
            encoding="utf-8",
        )
        return path

    def test_ingest_txt_contract_fields(self) -> None:
        self._write_sample_txt()
        ingestor = DiscoveryIngestor()
        payload = ingestor.ingest_directory(
            input_dir=self.input_dir,
            output_dir=self.discoveries_dir,
            pattern="*.txt",
            limit_files=1,
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["processed_files"], 1)
        discovery_path = Path(payload["discovery_files"][0])
        self.assertTrue(discovery_path.exists())

        discovery_json = json.loads(discovery_path.read_text(encoding="utf-8"))
        self.assertIn("propiedades_candidatas", discovery_json)
        self.assertIn("metricas_globales", discovery_json)
        self.assertGreaterEqual(len(discovery_json["propiedades_candidatas"]), 2)

        first_candidate = discovery_json["propiedades_candidatas"][0]
        for field in ("id", "tipo", "label", "confianza", "recomendacion_serie_q", "corpus_fuente"):
            self.assertIn(field, first_candidate)

    def test_ingest_txt_academic_profile_adds_metrics(self) -> None:
        self._write_sample_txt("academico.txt")
        ingestor = DiscoveryIngestor()
        payload = ingestor.ingest_directory(
            input_dir=self.input_dir,
            output_dir=self.discoveries_dir,
            pattern="*.txt",
            limit_files=1,
            profile="academico",
        )

        self.assertEqual(payload["profile"], "academico")
        discovery_path = Path(payload["discovery_files"][0])
        discovery_json = json.loads(discovery_path.read_text(encoding="utf-8"))
        metrics = discovery_json["metricas_globales"]

        self.assertEqual(discovery_json["perfil_usuario"], "academico")
        for field in ("academic_signal_score", "citation_density", "method_coverage", "argumentation_index"):
            self.assertIn(field, metrics)

        labels = {item.get("label") for item in discovery_json["propiedades_candidatas"]}
        self.assertIn("subcapa_argumentacion_metodologica", labels)

    def test_run_all_generates_q_bundles(self) -> None:
        self._write_sample_txt()
        store = QSeriesRegistryStore(self.registry_path)
        runner = AutomationCycleRunner(store)

        payload = runner.run_all(
            input_txt_dir=self.input_dir,
            discoveries_dir=self.discoveries_dir,
            output_dir=self.output_dir,
            pattern="*.txt",
            limit_files=1,
        )

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["cycle"]["created_entries"] >= 1)
        registry = store.load()
        self.assertGreaterEqual(len(registry.entries), 1)

        first_entry = registry.entries[0]
        manifest_path = Path(str(first_entry.metadata.get("manifest_path") or ""))
        decision_path = Path(str(first_entry.metadata.get("decision_path") or ""))
        self.assertTrue(manifest_path.exists())
        self.assertTrue(decision_path.exists())

    def test_run_all_is_idempotent_for_same_txt(self) -> None:
        self._write_sample_txt()
        store = QSeriesRegistryStore(self.registry_path)
        runner = AutomationCycleRunner(store)

        first = runner.run_all(
            input_txt_dir=self.input_dir,
            discoveries_dir=self.discoveries_dir,
            output_dir=self.output_dir,
            pattern="*.txt",
            limit_files=1,
        )
        second = runner.run_all(
            input_txt_dir=self.input_dir,
            discoveries_dir=self.discoveries_dir,
            output_dir=self.output_dir,
            pattern="*.txt",
            limit_files=1,
        )

        self.assertGreaterEqual(first["cycle"]["created_entries"], 1)
        self.assertEqual(second["cycle"]["created_entries"], 0)

    def test_run_all_academic_profile_roundtrip(self) -> None:
        self._write_sample_txt("paper_like.txt")
        store = QSeriesRegistryStore(self.registry_path)
        runner = AutomationCycleRunner(store)

        payload = runner.run_all(
            input_txt_dir=self.input_dir,
            discoveries_dir=self.discoveries_dir,
            output_dir=self.output_dir,
            pattern="*.txt",
            limit_files=1,
            profile="academico",
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["profile"], "academico")
        self.assertEqual(payload["ingest"]["profile"], "academico")

    def test_universal_profiles_ingest_supported(self) -> None:
        self._write_sample_txt("profiles.txt")
        ingestor = DiscoveryIngestor()
        for profile in ("general", "academico", "educativo", "editorial", "investigacion_aplicada"):
            payload = ingestor.ingest_directory(
                input_dir=self.input_dir,
                output_dir=self.discoveries_dir,
                pattern="*.txt",
                limit_files=1,
                profile=profile,
            )
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["profile"], profile)

    def test_universal_report_generation(self) -> None:
        self._write_sample_txt("report.txt")
        store = QSeriesRegistryStore(self.registry_path)
        runner = AutomationCycleRunner(store)
        runner.run_all(
            input_txt_dir=self.input_dir,
            discoveries_dir=self.discoveries_dir,
            output_dir=self.output_dir,
            pattern="*.txt",
            limit_files=1,
            profile="educativo",
        )

        report_builder = UniversalReportBuilder(store)
        report = report_builder.build_report(
            profile="educativo",
            discoveries_dir=self.discoveries_dir,
            reports_dir=self.tmp_path / "reports",
        )
        self.assertTrue(report["ok"])
        self.assertEqual(report["profile"], "educativo")
        self.assertTrue(Path(report["report_path"]).exists())


if __name__ == "__main__":
    unittest.main()