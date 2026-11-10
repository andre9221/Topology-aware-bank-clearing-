"""
hsc.py
======
Implementation of Hub-Spoke Clearing (HSC).
A topology-aware hybrid decomposition algorithm for the Bank Clearing Problem (BCP).

Pipeline:
  1. Topology Partitioning: Degree-based selection of Hub Core H and Spoke Periphery S.
  2. Super-Spoke Aggregation: Identification of weakly connected components in S,
     pooled as virtual aggregate nodes.
  3. Core Mixed-Integer Program: Solves 0/1 integer program on H and virtual super-spokes.
  4. Spoke Rationing / Allocation: Allocates aggregate flows to original obligations.
  5. Deterministic Worklist Feasibility Repair: Sequentially removes violating obligations
     with guaranteed finite termination (at most |X| <= m steps).
"""

import time
import collections
import math
import numpy as np
import scipy.sparse as sp
import highspy
from .graph_utils import verify_net_feasibility, build_incidence_csc


def hsc_clearing(node_list, arcs, deposits, k_frac=0.06, time_limit=10.0):
    """
    Execute Hub-Spoke Clearing (HSC) algorithm.

    Parameters
    ----------
    node_list : list
        List of participant account/bank IDs.
    arcs : list of tuple
        Payment obligations (u, v, w).
    deposits : dict
        Mapping participant ID -> available deposit collateral limit D_u.
    k_frac : float, optional
        Fraction of highest-degree nodes designated as hubs (default: 0.06).
    time_limit : float, optional
        Time budget for the Hub-Core MIP solver (default: 10.0 s).

    Returns
    -------
    dict
        - volume: total settled face value ($)
        - count: total settled payment obligations count
        - time: execution time in seconds
        - is_feasible: verified feasibility indicator
    """
    t0 = time.perf_counter()
    n_arcs = len(arcs)
    n_nodes = len(node_list)

    if n_arcs == 0 or n_nodes == 0:
        return {"volume": 0.0, "count": 0, "time": 0.0, "is_feasible": True}

    # Step 1: Hub Identification
    in_deg = collections.defaultdict(int)
    out_deg = collections.defaultdict(int)
    for u, v, w in arcs:
        out_deg[u] += 1
        in_deg[v] += 1

    deg = {n: in_deg[n] + out_deg[n] for n in node_list}
    sorted_nodes = sorted(node_list, key=lambda n: -deg[n])

    k = max(2, int(math.ceil(k_frac * n_nodes)))
    k = min(k, n_nodes)

    H = set(sorted_nodes[:k])
    S = set(sorted_nodes[k:])

    # Step 2: Super-Spoke Aggregation via Disjoint Set (Union-Find)
    parent = {n: n for n in S}

    def find(p):
        path = []
        while parent[p] != p:
            path.append(p)
            p = parent[p]
        for node in path:
            parent[node] = p
        return p

    def union(p1, p2):
        r1, r2 = find(p1), find(p2)
        if r1 != r2:
            parent[r1] = r2

    for u, v, w in arcs:
        if u in S and v in S:
            union(u, v)

    comp_map = {n: find(n) for n in S}
    comps = set(comp_map.values())

    # Build Core Variables (Hub-Hub arcs and Spoke-to-Hub/Hub-to-Spoke aggregated arcs)
    core_arcs = []
    arc_to_core = {}

    for j, (u, v, w) in enumerate(arcs):
        if u in H and v in H:
            arc_to_core[j] = len(core_arcs)
            core_arcs.append((u, v, w, [j]))
        elif u in S and v in H:
            c = comp_map[u]
            # virtual arc c -> v
            arc_to_core[j] = len(core_arcs)
            core_arcs.append((f"SS_{c}", v, w, [j]))
        elif u in H and v in S:
            c = comp_map[v]
            # virtual arc u -> c
            arc_to_core[j] = len(core_arcs)
            core_arcs.append((u, f"SS_{c}", w, [j]))

    # Step 3: Solve Core via HiGHS MIP
    cleared_arcs = set()
    if core_arcs:
        core_nodes = list(H) + [f"SS_{c}" for c in comps]
        node_to_cidx = {n: i for i, n in enumerate(core_nodes)}

        core_deposits = {}
        for h in H:
            core_deposits[h] = float(deposits.get(h, 0.0))
        for c in comps:
            # Pooled deposit for super-spoke
            pooled_dep = sum(deposits.get(nd, 0.0) for nd in S if comp_map[nd] == c)
            core_deposits[f"SS_{c}"] = float(pooled_dep)

        h_mip = highspy.Highs()
        h_mip.setOptionValue("output_flag", False)
        h_mip.setOptionValue("time_limit", float(time_limit))

        n_ca = len(core_arcs)
        n_cn = len(core_nodes)

        for _ in range(n_ca):
            h_mip.addVariable(0.0, 1.0, highspy.HighsVarType.kInteger)

        h_mip.changeObjectiveSense(highspy.ObjSense.kMinimize)
        for i, (u, v, w, _) in enumerate(core_arcs):
            h_mip.changeColCost(i, -float(w))

        # Flow constraints for core nodes
        arc_incidence = {n: [] for n in core_nodes}
        for i, (u, v, w, _) in enumerate(core_arcs):
            arc_incidence[u].append((i, float(w)))
            arc_incidence[v].append((i, -float(w)))

        for n in core_nodes:
            if not arc_incidence[n]:
                continue
            idx = [i for i, _ in arc_incidence[n]]
            vals = [c for _, c in arc_incidence[n]]
            h_mip.addRow(-highspy.kHighsInf, core_deposits[n], len(idx), idx, vals)

        h_mip.run()
        sol = h_mip.getSolution()

        try:
            for i, (u, v, w, orig_indices) in enumerate(core_arcs):
                if sol.col_value[i] > 0.5:
                    for orig_j in orig_indices:
                        cleared_arcs.add(orig_j)
        except Exception:
            pass

    # Step 4: Spoke Internal Obligation Allocation (Greedy within components)
    spoke_internal = [j for j in range(n_arcs) if arcs[j][0] in S and arcs[j][1] in S]
    spoke_internal.sort(key=lambda j: -arcs[j][2])

    net = {nd: 0.0 for nd in node_list}
    in_sol = [False] * n_arcs
    for j in cleared_arcs:
        u, v, w = arcs[j]
        net[u] += w
        net[v] -= w
        in_sol[j] = True

    for j in spoke_internal:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            in_sol[j] = True
            cleared_arcs.add(j)

    # Step 5: Deterministic Worklist Feasibility Repair
    # Find all violating participants: Net_u > D_u
    violating = collections.deque([nd for nd in node_list if net[nd] > deposits.get(nd, 0.0) + 1e-9])

    while violating:
        u = violating.popleft()
        if net[u] <= deposits.get(u, 0.0) + 1e-9:
            continue

        # Find cleared outgoing arcs from u, select lightest to remove
        out_arcs = [j for j in range(n_arcs) if in_sol[j] and arcs[j][0] == u]
        if not out_arcs:
            continue

        out_arcs.sort(key=lambda j: arcs[j][2])
        remove_j = out_arcs[0]
        u_p, v_p, w_p = arcs[remove_j]

        # Deselect arc
        in_sol[remove_j] = False
        cleared_arcs.discard(remove_j)
        net[u_p] -= w_p
        net[v_p] += w_p

        # Re-check u_p
        if net[u_p] > deposits.get(u_p, 0.0) + 1e-9:
            violating.append(u_p)

        # Re-check v_p (loss of incoming credit may cause violation)
        if net[v_p] > deposits.get(v_p, 0.0) + 1e-9:
            violating.append(v_p)

    t_elapsed = time.perf_counter() - t0
    is_feasible, max_viol, _ = verify_net_feasibility(node_list, arcs, deposits, in_sol)
    vol = sum(arcs[j][2] for j in cleared_arcs)

    return {
        "volume": vol,
        "count": len(cleared_arcs),
        "time": t_elapsed,
        "is_feasible": is_feasible,
        "max_violation": max_viol,
    }
