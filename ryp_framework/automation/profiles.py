from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfileConfig:
    key: str
    label: str
    integration_bias: float
    translation_bias: float
    closure_bias: float
    description: str


_PROFILE_MAP: dict[str, ProfileConfig] = {
    "general": ProfileConfig(
        key="general",
        label="General",
        integration_bias=1.0,
        translation_bias=1.0,
        closure_bias=1.0,
        description="Preset balanceado para uso transversal.",
    ),
    "academico": ProfileConfig(
        key="academico",
        label="Academico",
        integration_bias=1.08,
        translation_bias=1.06,
        closure_bias=0.96,
        description="Refuerza argumentacion, metodo y trazabilidad.",
    ),
    "educativo": ProfileConfig(
        key="educativo",
        label="Educativo",
        integration_bias=1.02,
        translation_bias=1.10,
        closure_bias=0.95,
        description="Optimiza claridad pedagogica y progresion conceptual.",
    ),
    "editorial": ProfileConfig(
        key="editorial",
        label="Editorial",
        integration_bias=0.98,
        translation_bias=1.14,
        closure_bias=0.92,
        description="Prioriza legibilidad, cohesion narrativa y estilo.",
    ),
    "investigacion_aplicada": ProfileConfig(
        key="investigacion_aplicada",
        label="Investigacion Aplicada",
        integration_bias=1.12,
        translation_bias=1.04,
        closure_bias=1.02,
        description="Favorece robustez empirica y explotacion operativa.",
    ),
}


def allowed_profiles() -> tuple[str, ...]:
    return tuple(sorted(_PROFILE_MAP.keys()))


def resolve_profile(raw_profile: str | None) -> ProfileConfig:
    normalized = str(raw_profile or "general").strip().lower()
    return _PROFILE_MAP.get(normalized, _PROFILE_MAP["general"])
