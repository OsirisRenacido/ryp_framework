"""
simulation — Simulation runners and batch experiment utilities.

Re-exports from _core.
"""

from ._core import (  # noqa: F401
    simulate,
    run_single_experiment,
    run_batch_experiments,
    analyze_batch,
    run_full_experiment_suite,
    explore,
    simulate_mode,
    compare_models,
    log_experiment,
)
