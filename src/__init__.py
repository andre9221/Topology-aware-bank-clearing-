"""
Topology-Aware Bank Clearing Package
====================================
Algorithms for the Bank Clearing Problem (BCP) under multilateral netting constraints.
- CA-HSC: Cycle-Aware Hub-Spoke Clearing (deterministic multi-stage heuristic)
- HSC: Hub-Spoke Clearing (core MIP + super-spoke aggregation + worklist repair)
- Baselines: Plain Greedy, Greedy + Local Search, HiGHS MIP, Continuous LP Relaxation
"""

from .ca_hsc import ca_hsc_clearing
from .hsc import hsc_clearing
from .baselines import (
    greedy_clearing,
    greedy_local_search,
    highs_exact_mip,
    highs_lp_relaxation,
)
from .graph_utils import (
    build_incidence_csc,
    generate_barabasi_albert_clearing_graph,
    verify_net_feasibility,
    format_currency,
)

__all__ = [
    "ca_hsc_clearing",
    "hsc_clearing",
    "greedy_clearing",
    "greedy_local_search",
    "highs_exact_mip",
    "highs_lp_relaxation",
    "build_incidence_csc",
    "generate_barabasi_albert_clearing_graph",
    "verify_net_feasibility",
    "format_currency",
]

