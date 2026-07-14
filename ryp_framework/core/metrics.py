"""
metrics — Autopoiesis, fractal, and stability metrics.

Re-exports from _core.
"""

from ._core import (  # noqa: F401
    cosine_similarity,
    compute_fractal_profile,
    autopoiesis_metrics,
    stability,
    build_core_local_projections,
    integrate_subjectivity_in_A,
    select_reference_higher_order_node,
    assign_axis_anchors_around_reference,
    build_sam_313_from_higher_order_nodes,
    stabilize_sam_313_branches_in_A,
    build_explicit_sam_313_crystal,
    read_higher_order_elements_from_core,
    derive_order4_recursive_feedback,
    compute_order4_recursive_metrics,
    compute_order3_viability_metrics,
    compute_core_semantic_metrics,
    compute_impact_map,
    run_motor_closure_bridge,
    summarize_order4_recursive_taxonomy,
    summarize_order3_viability_taxonomy,
)
