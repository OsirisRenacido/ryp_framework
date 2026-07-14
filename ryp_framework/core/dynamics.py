"""
dynamics — S-A-M core dynamic operators.

Re-exports the foundational transformation functions from _core.
"""

from ._core import (  # noqa: F401
    T,
    S_alpha,
    R,
    collapse,
    Omega,
    F,
    normalize,
    get_permutation_matrix,
    initialize_base_permutation,
    apply_intervention,
    recommend_a_axis_stabilization,
    set_conjugation_navigator,
    reset_conjugation_navigator,
)
