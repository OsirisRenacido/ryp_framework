from __future__ import annotations

import json
from pathlib import Path

from ryp_framework.automation.contracts import QSeriesRegistry


class QSeriesRegistryStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def initialize(self) -> QSeriesRegistry:
        registry = QSeriesRegistry()
        self.save(registry)
        return registry

    def load(self) -> QSeriesRegistry:
        if not self.path.exists():
            return QSeriesRegistry()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return QSeriesRegistry.from_dict(payload)

    def save(self, registry: QSeriesRegistry) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(registry.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )