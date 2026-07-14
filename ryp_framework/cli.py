from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ryp_framework import __version__
from ryp_framework.automation.builder import SerieQBuilder
from ryp_framework.automation.ingest import DiscoveryIngestor
from ryp_framework.automation.profiles import allowed_profiles
from ryp_framework.automation.registry import QSeriesRegistryStore
from ryp_framework.automation.reporting import UniversalReportBuilder
from ryp_framework.automation.runner import AutomationCycleRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ryp",
        description="RYP framework CLI",
    )
    subparsers = parser.add_subparsers(dest="command")

    status_parser = subparsers.add_parser("status", help="Show package and automation status")
    status_parser.add_argument(
        "--registry",
        default=str(SerieQBuilder.default_registry_path()),
        help="Path to the Q series registry JSON file.",
    )

    init_registry_parser = subparsers.add_parser("init-registry", help="Create an empty Q series registry")
    init_registry_parser.add_argument(
        "--registry",
        default=str(SerieQBuilder.default_registry_path()),
        help="Path to the Q series registry JSON file.",
    )

    scaffold_parser = subparsers.add_parser("scaffold-q", help="Create a draft Q entry from discovery metadata")
    scaffold_parser.add_argument(
        "--source",
        required=True,
        help="Source discovery JSON. Relative names are resolved inside ryp_framework/workspace/01_ENTRADAS/DESCUBRIMIENTOS.",
    )
    scaffold_parser.add_argument(
        "--registry",
        default=str(SerieQBuilder.default_registry_path()),
        help="Path to the Q series registry JSON file.",
    )
    scaffold_parser.add_argument(
        "--output-dir",
        default=str(SerieQBuilder.default_output_dir()),
        help="Directory where the draft Q markdown/json artifacts will be written.",
    )
    scaffold_parser.add_argument(
        "--title",
        default=None,
        help="Optional human title for the generated Q entry.",
    )

    promote_parser = subparsers.add_parser(
        "promote-discovery",
        help="Create one Q draft per grouped recommendation inside a discovery payload",
    )
    promote_parser.add_argument(
        "--source",
        required=True,
        help="Source discovery JSON. Relative names are resolved inside ryp_framework/workspace/01_ENTRADAS/DESCUBRIMIENTOS.",
    )
    promote_parser.add_argument(
        "--registry",
        default=str(SerieQBuilder.default_registry_path()),
        help="Path to the Q series registry JSON file.",
    )
    promote_parser.add_argument(
        "--output-dir",
        default=str(SerieQBuilder.default_output_dir()),
        help="Directory where grouped Q markdown/json artifacts will be written.",
    )
    promote_parser.add_argument(
        "--title-prefix",
        default=None,
        help="Optional prefix to apply to every generated Q title.",
    )

    cycle_parser = subparsers.add_parser(
        "run-cycle",
        help="Process all internal discovery JSON files and promote grouped Q drafts",
    )
    cycle_parser.add_argument(
        "--discoveries-dir",
        default=str(SerieQBuilder.default_discoveries_dir()),
        help="Directory to scan for discovery JSON files.",
    )
    cycle_parser.add_argument(
        "--output-dir",
        default=str(SerieQBuilder.default_output_dir()),
        help="Directory where grouped Q markdown/json artifacts will be written.",
    )
    cycle_parser.add_argument(
        "--registry",
        default=str(SerieQBuilder.default_registry_path()),
        help="Path to the Q series registry JSON file.",
    )
    cycle_parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Optional limit for the number of discovery files to process.",
    )

    ingest_parser = subparsers.add_parser(
        "ingest-txt",
        help="Convert TXT files into discovery JSON payloads in the framework workspace",
    )
    ingest_parser.add_argument(
        "--input-dir",
        default=str(DiscoveryIngestor.default_txt_input_dir()),
        help="Directory containing input TXT files.",
    )
    ingest_parser.add_argument(
        "--discoveries-dir",
        default=str(SerieQBuilder.default_discoveries_dir()),
        help="Directory where discovery JSON/MD files will be written.",
    )
    ingest_parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern for input TXT files.",
    )
    ingest_parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Optional limit for TXT files to ingest.",
    )
    ingest_parser.add_argument(
        "--profile",
        choices=allowed_profiles(),
        default="general",
        help="Inference profile for discovery generation.",
    )

    run_all_parser = subparsers.add_parser(
        "run-all",
        help="Run end-to-end pipeline TXT -> discoveries -> Q bundles",
    )
    run_all_parser.add_argument(
        "--input-dir",
        default=str(DiscoveryIngestor.default_txt_input_dir()),
        help="Directory containing input TXT files.",
    )
    run_all_parser.add_argument(
        "--discoveries-dir",
        default=str(SerieQBuilder.default_discoveries_dir()),
        help="Directory where discovery JSON/MD files will be written.",
    )
    run_all_parser.add_argument(
        "--output-dir",
        default=str(SerieQBuilder.default_output_dir()),
        help="Directory where grouped Q markdown/json artifacts will be written.",
    )
    run_all_parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern for input TXT files.",
    )
    run_all_parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Optional limit for TXT files to ingest.",
    )
    run_all_parser.add_argument(
        "--profile",
        choices=allowed_profiles(),
        default="general",
        help="Inference profile for TXT ingestion in the end-to-end run.",
    )

    quickstart_parser = subparsers.add_parser(
        "quickstart",
        help="Run a one-command universal demo using packaged example TXT",
    )
    quickstart_parser.add_argument(
        "--profile",
        choices=allowed_profiles(),
        default="general",
        help="Profile preset to run the quickstart pipeline.",
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Run pipeline and generate universal markdown report",
    )
    analyze_parser.add_argument(
        "--input-dir",
        default=str(DiscoveryIngestor.default_txt_input_dir()),
        help="Directory containing input TXT files.",
    )
    analyze_parser.add_argument(
        "--pattern",
        default="*.txt",
        help="Glob pattern for input TXT files.",
    )
    analyze_parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Optional limit for TXT files to ingest.",
    )
    analyze_parser.add_argument(
        "--profile",
        choices=allowed_profiles(),
        default="general",
        help="Profile preset used for the analysis run.",
    )

    report_parser = subparsers.add_parser(
        "report",
        help="Generate universal markdown report from latest pipeline state",
    )
    report_parser.add_argument(
        "--discoveries-dir",
        default=str(SerieQBuilder.default_discoveries_dir()),
        help="Directory containing discovery JSON files.",
    )
    report_parser.add_argument(
        "--reports-dir",
        default=str(UniversalReportBuilder.default_reports_dir()),
        help="Directory where universal reports will be written.",
    )
    report_parser.add_argument(
        "--profile",
        choices=allowed_profiles(),
        default="general",
        help="Profile label included in the report metadata.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        return _launch_legacy_app()

    registry_path = Path(getattr(args, "registry", str(SerieQBuilder.default_registry_path())))
    store = QSeriesRegistryStore(registry_path)

    if args.command == "status":
        registry = store.load()
        payload = {
            "ok": True,
            "version": __version__,
            "entry_count": len(registry.entries),
            "next_q_number": registry.next_q_number(),
            "registry_path": str(registry_path),
            "framework_workspace": str(SerieQBuilder.default_registry_path().parents[2]),
            "discoveries_dir": str(SerieQBuilder.default_discoveries_dir()),
            "q_entries_dir": str(SerieQBuilder.default_output_dir()),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "init-registry":
        registry = store.initialize()
        print(json.dumps(registry.to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "scaffold-q":
        builder = SerieQBuilder(store)
        bundle = builder.scaffold_from_source(
            source=args.source,
            output_dir=Path(args.output_dir),
            title=args.title,
        )
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
        return 0

    if args.command == "promote-discovery":
        builder = SerieQBuilder(store)
        bundle = builder.scaffold_all_candidates_from_source(
            source=args.source,
            output_dir=Path(args.output_dir),
            title_prefix=args.title_prefix,
        )
        print(json.dumps(bundle, ensure_ascii=False, indent=2))
        return 0

    if args.command == "run-cycle":
        runner = AutomationCycleRunner(store)
        payload = runner.run(
            discoveries_dir=Path(args.discoveries_dir),
            output_dir=Path(args.output_dir),
            limit_files=args.limit_files,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "ingest-txt":
        ingestor = DiscoveryIngestor()
        payload = ingestor.ingest_directory(
            input_dir=Path(args.input_dir),
            output_dir=Path(args.discoveries_dir),
            pattern=args.pattern,
            limit_files=args.limit_files,
            profile=args.profile,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "run-all":
        runner = AutomationCycleRunner(store)
        payload = runner.run_all(
            input_txt_dir=Path(args.input_dir),
            discoveries_dir=Path(args.discoveries_dir),
            output_dir=Path(args.output_dir),
            pattern=args.pattern,
            limit_files=args.limit_files,
            profile=args.profile,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "quickstart":
        sample_txt = Path(__file__).resolve().parent / "examples" / "demo_entrada_semantica.txt"
        input_dir = DiscoveryIngestor.default_txt_input_dir()
        input_dir.mkdir(parents=True, exist_ok=True)
        target_txt = input_dir / sample_txt.name
        if not target_txt.exists():
            target_txt.write_text(sample_txt.read_text(encoding="utf-8"), encoding="utf-8")

        runner = AutomationCycleRunner(store)
        payload = runner.run_all(
            input_txt_dir=input_dir,
            discoveries_dir=SerieQBuilder.default_discoveries_dir(),
            output_dir=SerieQBuilder.default_output_dir(),
            pattern="*.txt",
            limit_files=1,
            profile=args.profile,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "report":
        reporter = UniversalReportBuilder(store)
        payload = reporter.build_report(
            profile=args.profile,
            discoveries_dir=Path(args.discoveries_dir),
            reports_dir=Path(args.reports_dir),
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "analyze":
        runner = AutomationCycleRunner(store)
        run_payload = runner.run_all(
            input_txt_dir=Path(args.input_dir),
            discoveries_dir=SerieQBuilder.default_discoveries_dir(),
            output_dir=SerieQBuilder.default_output_dir(),
            pattern=args.pattern,
            limit_files=args.limit_files,
            profile=args.profile,
        )
        reporter = UniversalReportBuilder(store)
        report_payload = reporter.build_report(
            profile=args.profile,
            discoveries_dir=SerieQBuilder.default_discoveries_dir(),
            reports_dir=UniversalReportBuilder.default_reports_dir(),
        )
        payload = {
            "ok": True,
            "pipeline": run_payload,
            "report": report_payload,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


def _launch_legacy_app() -> int:
    try:
        import RYP_APP
    except Exception as exc:
        print(
            "Legacy launcher unavailable. Use 'ryp status', 'ryp init-registry', or 'ryp scaffold-q'.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 1

    main_fn = getattr(RYP_APP, "main", None)
    if callable(main_fn):
        result = main_fn()
        return int(result) if isinstance(result, int) else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())