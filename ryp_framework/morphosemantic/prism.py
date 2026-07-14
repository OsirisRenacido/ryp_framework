from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from .operators import (
    compute_self_observation_proxy,
    interpret_axis_permutation,
    normalize,
)


CANONICAL_ROUTE_SIGNATURES = ("SAM", "SMA", "ASM", "AMS", "MAS", "MSA")


def _to_numpy(vector: Iterable[float]) -> np.ndarray:
    return normalize(vector)


def _angle_deg(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    denom = float(np.linalg.norm(vector_a) * np.linalg.norm(vector_b))
    if denom <= 0.0:
        return 0.0
    cosine = float(np.clip(np.dot(vector_a, vector_b) / denom, -1.0, 1.0))
    return float(np.degrees(np.arccos(cosine)))


def build_interaction_internal_sam(
    structural_similarity: float,
    trajectory_correlation: float,
    interaction_memory: float,
) -> np.ndarray:
    return normalize(
        [
            structural_similarity,
            (trajectory_correlation + 1.0) / 2.0,
            interaction_memory,
        ]
    )


def apply_prism_refraction(
    external_sam: Iterable[float],
    internal_sam: Iterable[float],
    boundary_strength: float = 0.60,
    reentry_gain: float = 0.20,
) -> dict:
    external_vector = _to_numpy(external_sam)
    internal_vector = _to_numpy(internal_sam)

    boundary_strength = float(np.clip(boundary_strength, 0.0, 1.0))
    reentry_gain = float(np.clip(reentry_gain, 0.0, 1.0))

    alignment = float(np.clip(np.dot(external_vector, internal_vector), 0.0, 1.0))
    external_gain = (1.0 - boundary_strength) * (1.0 + (1.0 - alignment) * 0.25)
    internal_gain = boundary_strength + reentry_gain * alignment
    refracted_vector = normalize(internal_vector * internal_gain + external_vector * external_gain)

    external_route = interpret_axis_permutation(external_vector)
    internal_route = interpret_axis_permutation(internal_vector)
    refracted_route = interpret_axis_permutation(refracted_vector)
    route_shift = internal_route["signature"] != refracted_route["signature"]
    closure_proxy = float(
        np.clip(
            0.5 * float(np.dot(internal_vector, refracted_vector))
            + 0.5 * compute_self_observation_proxy(refracted_vector),
            0.0,
            1.0,
        )
    )

    return {
        "external_sam": tuple(np.round(external_vector, 6)),
        "internal_sam": tuple(np.round(internal_vector, 6)),
        "refracted_sam": tuple(np.round(refracted_vector, 6)),
        "external_route": external_route,
        "internal_route": internal_route,
        "refracted_route": refracted_route,
        "route_signature": refracted_route["signature"],
        "route_shift": route_shift,
        "alignment": round(alignment, 6),
        "refraction_angle_deg": round(_angle_deg(external_vector, refracted_vector), 6),
        "closure_proxy": round(closure_proxy, 6),
        "boundary_strength": round(boundary_strength, 6),
        "reentry_gain": round(reentry_gain, 6),
    }


def route_signature_tracker(route_vectors: Sequence[Iterable[float]]) -> dict:
    signatures = [interpret_axis_permutation(_to_numpy(vector))["signature"] for vector in route_vectors]
    counts = {signature: signatures.count(signature) for signature in CANONICAL_ROUTE_SIGNATURES}
    covered = [signature for signature, count in counts.items() if count > 0]
    return {
        "signatures": signatures,
        "counts": counts,
        "covered_signatures": covered,
        "canonical_coverage": round(len(covered) / len(CANONICAL_ROUTE_SIGNATURES), 6),
        "stability_reached": len(covered) == len(CANONICAL_ROUTE_SIGNATURES),
    }