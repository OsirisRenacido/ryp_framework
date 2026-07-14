"""
matrix.py — SAM matrix construction and chain extraction utilities.

Re-exports the public APIs from build_universal and extract_chains
so callers can do: ``from ryp_framework.sam.matrix import SAMBuilder, ChainExtractor``
"""

from .build_universal import *   # noqa: F401, F403
from .extract_chains import *    # noqa: F401, F403
