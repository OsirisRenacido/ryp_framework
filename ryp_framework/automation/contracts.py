from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ArtifactSpec:
    artifact_id: str
    artifact_type: str
    path: str
    status: str = "draft"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TaskSpec:
    task_id: str
    title: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[ArtifactSpec] = field(default_factory=list)
    validators: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["outputs"] = [artifact.to_dict() for artifact in self.outputs]
        return payload


@dataclass(slots=True)
class QSeriesEntry:
    q_number: int
    variant: str = "BASE"
    status: str = "DRAFT"
    title: str = ""
    source: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    evidence: List[str] = field(default_factory=list)
    artifacts: List[ArtifactSpec] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def q_id(self) -> str:
        suffix = "" if self.variant.upper() == "BASE" else f"_{self.variant.upper()}"
        return f"Q{self.q_number:03d}{suffix}"

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["q_id"] = self.q_id
        payload["artifacts"] = [artifact.to_dict() for artifact in self.artifacts]
        return payload


@dataclass(slots=True)
class QSeriesRegistry:
    version: str = "0.1.0"
    generated_at: str = field(default_factory=utc_now_iso)
    entries: List[QSeriesEntry] = field(default_factory=list)

    def next_q_number(self) -> int:
        if not self.entries:
            return 1
        return max(entry.q_number for entry in self.entries) + 1

    def append(self, entry: QSeriesEntry) -> None:
        self.entries.append(entry)
        self.generated_at = utc_now_iso()

    def has_entry(self, source: str, candidate_key: str) -> bool:
        return any(
            entry.source == source and str(entry.metadata.get("candidate_key") or "") == candidate_key
            for entry in self.entries
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "QSeriesRegistry":
        entries = []
        for raw_entry in payload.get("entries") or []:
            artifacts = [ArtifactSpec(**artifact) for artifact in raw_entry.get("artifacts") or []]
            entry_payload = dict(raw_entry)
            entry_payload.pop("q_id", None)
            entry_payload["artifacts"] = artifacts
            entries.append(QSeriesEntry(**entry_payload))
        return cls(
            version=str(payload.get("version") or "0.1.0"),
            generated_at=str(payload.get("generated_at") or utc_now_iso()),
            entries=entries,
        )