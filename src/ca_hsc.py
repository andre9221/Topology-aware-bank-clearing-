"""
ca_hsc.py
=========
Production Implementation of Cycle-Aware Hub-Spoke Clearing (CA-HSC).
A deterministic multi-stage clearing heuristic for the Bank Clearing Problem (BCP)
designed for large-scale financial settlement networks under strict deadlines.

Key Architectural Stages:
  Stage 1: Topology Identification & Hub-Spoke Degree Partitioning
  Stage 2: Bilateral 2-Cycle Netting Presolve (Priority: Hub-Hub -> Hub-Spoke -> Spoke-Spoke)
  Stage 3: Hub-Directed Core Settlement (Weight-Ordered Inflows/Outflows)
  Stage 4: Spoke Peripheral Cluster Settlement
  Stage 5: Fast Incremental Refinement Sweep (1-Pass)
"""

import time
import collections
import math
from .graph_utils import verify_net_feasibility, format_currency


def ca_hsc_clearing(node_list, arcs, deposits, k_frac=0.05, k_min=10, return_details=False):
    """
    Execute the Cycle-Aware Hub-Spoke Clearing (CA-HSC) algorithm.

    Parameters
    ----------
    node_list : list
        List of participant account/bank IDs.
    arcs : list of tuple
        Payment obligations formatted as (u, v, w) where participant u owes v amount w.
    deposits : dict
        Mapping participant ID -> available deposit collateral limit D_u.
    k_frac : float, optional
        Fraction of highest-degree participants assigned to Hub Core H (default: 0.05).
    k_min : int, optional
        Minimum number of hubs (default: 10).
    return_details : bool, optional
        Whether to return granular stage contributions and solution bitmask (default: False).

    Returns
    -------
    dict
        - volume: total settled face value ($)
        - count: total settled payment obligations count
        - time: total execution time in seconds
        - is_feasible: verified feasibility indicator (all Net_i <= D_i)
        - stage_volumes: dictionary of volume settled per stage
        - in_solution: boolean mask of settled obligations (if return_details=True)
    """
    t_start = time.perf_counter()
    n_arcs = len(arcs)
    n_nodes = len(node_list)

    if n_arcs == 0 or n_nodes == 0:
        return {
            "volume": 0.0,
            "count": 0,
            "time": 0.0,
            "is_feasible": True,
            "stage_volumes": {},
        }

    # -------------------------------------------------------------------------
    # STAGE 1: Topology Identification & Hub-Spoke Degree Partitioning
    # -------------------------------------------------------------------------
    in_deg = collections.defaultdict(int)
    out_deg = collections.defaultdict(int)
    for u, v, w in arcs:
        out_deg[u] += 1
        in_deg[v] += 1

    total_deg = {nd: in_deg[nd] + out_deg[nd] for nd in node_list}
    sorted_nodes = sorted(node_list, key=lambda nd: -total_deg[nd])

    k = max(k_min, int(math.ceil(k_frac * n_nodes)))
    k = min(k, n_nodes)

    H = set(sorted_nodes[:k])          # Hub Core: central, highly-connected liquidity routing banks
    S = set(sorted_nodes[k:])          # Spoke Periphery: retail, merchant, and low-connectivity nodes

    # Track net positions: Net_i = Outflow_i - Inflow_i
    net = {nd: 0.0 for nd in node_list}
    in_sol = [False] * n_arcs

    # -------------------------------------------------------------------------
    # STAGE 2: Bilateral 2-Cycle Netting Presolve
    # -------------------------------------------------------------------------
    # Reciprocal arcs (u -> v and v -> u) are netted out bilaterally.
    # The mutual offset min(a, b) consumes zero deposit; only the net delta |a - b|
    # requires collateral from the net debtor.
    pairs = collections.defaultdict(list)
    for j, (u, v, w) in enumerate(arcs):
        pk = (min(u, v), max(u, v))
        pairs[pk].append(j)

    # Topological priority: Hub-Hub cycles first, then Hub-Spoke, then Spoke-Spoke
    def pair_priority(item):
        (a, b), idx_list = item
        vol = sum(arcs[j][2] for j in idx_list)
        is_hh = (a in H and b in H)
        is_hs = (a in H or b in H)
        tier = 2 if is_hh else (1 if is_hs else 0)
        return (tier, vol)

    sorted_pairs = sorted(pairs.items(), key=pair_priority, reverse=True)

    stage1_vol = 0.0
    stage1_count = 0

    for (a, b), idx_list in sorted_pairs:
        # Check if mutual reciprocal obligations exist
        has_ab = any(arcs[j][0] == a for j in idx_list)
        has_ba = any(arcs[j][0] == b for j in idx_list)
        if has_ab and has_ba:
            delta = collections.defaultdict(float)
            for j in idx_list:
                u, v, w = arcs[j]
                delta[u] += w
                delta[v] -= w

            # Verify collateral feasibility before committing the reciprocal bundle
            if all(net[nd] + delta.get(nd, 0.0) <= deposits.get(nd, 0.0) + 1e-9 for nd in delta):
                for j in idx_list:
                    u, v, w = arcs[j]
                    net[u] += w
                    net[v] -= w
                    in_sol[j] = True
                    stage1_vol += w
                    stage1_count += 1

    # -------------------------------------------------------------------------
    # STAGE 3: Hub-Directed Core Liquidity Settlement
    # -------------------------------------------------------------------------
    # High-value obligations directly incident to the Hub Core (H-H and H-S/S-H)
    hub_arcs = [
        j for j in range(n_arcs)
        if not in_sol[j] and (arcs[j][0] in H or arcs[j][1] in H)
    ]
    hub_arcs.sort(key=lambda j: -arcs[j][2])

    stage2_vol = 0.0
    stage2_count = 0
    for j in hub_arcs:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            in_sol[j] = True
            stage2_vol += w
            stage2_count += 1

    # -------------------------------------------------------------------------
    # STAGE 4: Spoke Peripheral Cluster Settlement
    # -------------------------------------------------------------------------
    # Settle remaining peripheral obligations among spokes (S-S)
    spoke_arcs = [
        j for j in range(n_arcs)
        if not in_sol[j] and arcs[j][0] in S and arcs[j][1] in S
    ]
    spoke_arcs.sort(key=lambda j: -arcs[j][2])

    stage3_vol = 0.0
    stage3_count = 0
    for j in spoke_arcs:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            in_sol[j] = True
            stage3_vol += w
            stage3_count += 1

    # -------------------------------------------------------------------------
    # STAGE 5: Fast Incremental Refinement Sweep (1-Pass)
    # -------------------------------------------------------------------------
    # Re-evaluate remaining unscheduled arcs whose sources may now have received
    # incoming credits from Stages 3 and 4
    unsettled = [j for j in range(n_arcs) if not in_sol[j]]
    unsettled.sort(key=lambda j: -arcs[j][2])

    stage4_vol = 0.0
    stage4_count = 0
    for j in unsettled:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            in_sol[j] = True
            stage4_vol += w
            stage4_count += 1

    t_elapsed = time.perf_counter() - t_start

    # Strict Invariant Feasibility Check
    is_feasible, max_viol, _ = verify_net_feasibility(node_list, arcs, deposits, in_sol)
    total_volume = sum(arcs[j][2] for j in range(n_arcs) if in_sol[j])
    total_count = sum(1 for is_c in in_sol if is_c)

    res = {
        "volume": total_volume,
        "count": total_count,
        "time": t_elapsed,
        "is_feasible": is_feasible,
        "max_violation": max_viol,
        "hubs_count": len(H),
        "spokes_count": len(S),
        "stage_volumes": {
            "bilateral_cycles": stage1_vol,
            "hub_directed": stage2_vol,
            "spoke_clusters": stage3_vol,
            "refinement": stage4_vol,
        },
        "stage_counts": {
            "bilateral_cycles": stage1_count,
            "hub_directed": stage2_count,
            "spoke_clusters": stage3_count,
            "refinement": stage4_count,
        },
    }

    if return_details:
        res["in_solution"] = in_sol

    return res

