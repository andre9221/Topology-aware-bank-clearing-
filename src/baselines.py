"""
baselines.py
============
Baseline clearing algorithms and solver benchmarks for the Bank Clearing Problem:
  1. Plain Greedy (Weight-ordered descending heuristic)
  2. Greedy + Local Search (Greedy with 1-opt local search additions)
  3. HiGHS MIP Solver (Branch-and-cut exact 0/1 integer program)
  4. HiGHS LP Relaxation (Continuous relaxation providing polyhedral upper bounds)
"""

import time
import collections
import numpy as np
import scipy.sparse as sp
import highspy
from .graph_utils import build_incidence_csc, verify_net_feasibility


def greedy_clearing(arcs, deposits, node_list):
    """
    Plain Greedy clearing: processes obligations in descending face value w(u, v).
    Commits arc if and only if Net_u + w <= D_u.
    """
    t0 = time.perf_counter()
    net = {nd: 0.0 for nd in node_list}
    cleared = []

    order = sorted(range(len(arcs)), key=lambda j: -arcs[j][2])
    for j in order:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            cleared.append(j)

    t_elapsed = time.perf_counter() - t0
    in_sol = [False] * len(arcs)
    for j in cleared:
        in_sol[j] = True

    is_feasible, max_viol, _ = verify_net_feasibility(node_list, arcs, deposits, in_sol)
    vol = sum(arcs[j][2] for j in cleared)

    return {
        "volume": vol,
        "count": len(cleared),
        "time": t_elapsed,
        "is_feasible": is_feasible,
        "max_violation": max_viol,
    }


def greedy_local_search(arcs, deposits, node_list, time_limit=1.0):
    """
    Greedy + Local Search: starts with Plain Greedy and iteratively scans
    unsettled obligations to find 1-opt augmentations within the allotted time limit.
    """
    t0 = time.perf_counter()
    n = len(arcs)
    net = {nd: 0.0 for nd in node_list}
    in_sol = [False] * n

    # Initial greedy pass
    order = sorted(range(n), key=lambda j: -arcs[j][2])
    for j in order:
        u, v, w = arcs[j]
        if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
            net[u] += w
            net[v] -= w
            in_sol[j] = True

    # 1-opt local search scan within time limit
    unsettled = sorted([j for j in range(n) if not in_sol[j]], key=lambda j: -arcs[j][2])
    deadline = t0 + time_limit

    improved = True
    while improved and time.perf_counter() < deadline:
        improved = False
        for j in unsettled:
            if time.perf_counter() >= deadline:
                break
            if not in_sol[j]:
                u, v, w = arcs[j]
                if net[u] + w <= deposits.get(u, 0.0) + 1e-9:
                    net[u] += w
                    net[v] -= w
                    in_sol[j] = True
                    improved = True

    t_elapsed = min(time_limit, time.perf_counter() - t0)
    cleared = [j for j in range(n) if in_sol[j]]
    is_feasible, max_viol, _ = verify_net_feasibility(node_list, arcs, deposits, in_sol)
    vol = sum(arcs[j][2] for j in cleared)

    return {
        "volume": vol,
        "count": len(cleared),
        "time": t_elapsed,
        "is_feasible": is_feasible,
        "max_violation": max_viol,
    }


def highs_exact_mip(arcs, deposits, node_list, time_limit=10.0, output_flag=False):
    """
    Branch-and-Cut exact Mixed-Integer Programming solver using HiGHS.
    Solves:
      max   sum w(u, v) * x_uv
      s.t.  Out_i - In_i <= D_i  for all i in V
            x_uv in {0, 1}
    """
    t0 = time.perf_counter()
    n_arcs = len(arcs)
    n_nodes = len(node_list)

    if n_arcs == 0 or n_nodes == 0:
        return {"volume": 0.0, "count": 0, "time": 0.0, "status": "empty", "is_feasible": True}

    node_to_idx = {n: i for i, n in enumerate(node_list)}
    A = build_incidence_csc(node_to_idx, arcs)

    lp = highspy.HighsLp()
    lp.num_col_ = n_arcs
    lp.num_row_ = n_nodes
    lp.col_cost_ = np.array([-float(w) for _, _, w in arcs], dtype=float)
    lp.col_lower_ = np.zeros(n_arcs)
    lp.col_upper_ = np.ones(n_arcs)
    lp.row_lower_ = np.full(n_nodes, -highspy.kHighsInf)
    lp.row_upper_ = np.array([float(deposits.get(n, 0.0)) for n in node_list], dtype=float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = A.indptr.astype(np.int64)
    lp.a_matrix_.index_ = A.indices.astype(np.int32)
    lp.a_matrix_.value_ = A.data.astype(float)
    lp.integrality_ = np.full(n_arcs, highspy.HighsVarType.kInteger)

    h = highspy.Highs()
    h.setOptionValue("output_flag", output_flag)
    h.setOptionValue("time_limit", float(time_limit))
    h.setOptionValue("threads", 8)
    h.passModel(lp)
    h.run()

    t_elapsed = time.perf_counter() - t0
    sol = h.getSolution()
    info = h.getInfo()

    cleared = []
    vol = 0.0
    status = str(h.getModelStatus())

    in_sol = [False] * n_arcs
    if sol.col_value is not None and len(sol.col_value) == n_arcs:
        for j in range(n_arcs):
            if sol.col_value[j] > 0.5:
                cleared.append(j)
                in_sol[j] = True
                vol += arcs[j][2]

    is_feasible, max_viol, _ = verify_net_feasibility(node_list, arcs, deposits, in_sol)

    return {
        "volume": vol,
        "count": len(cleared),
        "time": t_elapsed,
        "status": status,
        "is_feasible": is_feasible,
        "max_violation": max_viol,
    }


def highs_lp_relaxation(arcs, deposits, node_list, output_flag=False):
    """
    Continuous LP relaxation:
      Replaces x_uv in {0, 1} with 0 <= x_uv <= 1.
    Yields the theoretical upper bound (integrality gap diagnostic).
    """
    t0 = time.perf_counter()
    n_arcs = len(arcs)
    n_nodes = len(node_list)

    if n_arcs == 0 or n_nodes == 0:
        return {"bound": 0.0, "time": 0.0, "status": "empty", "fractional_count": 0}

    node_to_idx = {n: i for i, n in enumerate(node_list)}
    A = build_incidence_csc(node_to_idx, arcs)

    lp = highspy.HighsLp()
    lp.num_col_ = n_arcs
    lp.num_row_ = n_nodes
    lp.col_cost_ = np.array([-float(w) for _, _, w in arcs], dtype=float)
    lp.col_lower_ = np.zeros(n_arcs)
    lp.col_upper_ = np.ones(n_arcs)
    lp.row_lower_ = np.full(n_nodes, -highspy.kHighsInf)
    lp.row_upper_ = np.array([float(deposits.get(n, 0.0)) for n in node_list], dtype=float)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = A.indptr.astype(np.int64)
    lp.a_matrix_.index_ = A.indices.astype(np.int32)
    lp.a_matrix_.value_ = A.data.astype(float)
    lp.integrality_ = np.full(n_arcs, highspy.HighsVarType.kContinuous)

    h = highspy.Highs()
    h.setOptionValue("output_flag", output_flag)
    h.setOptionValue("solver", "ipm")  # Interior Point Method for fast continuous LP
    h.passModel(lp)
    h.run()

    t_elapsed = time.perf_counter() - t0
    sol = h.getSolution()

    bound = 0.0
    frac_cnt = 0
    if sol.col_value is not None:
        for v in sol.col_value:
            if 1e-4 < v < 1.0 - 1e-4:
                frac_cnt += 1
        bound = -h.getInfo().objective_function_value

    return {
        "bound": bound,
        "time": t_elapsed,
        "status": str(h.getModelStatus()),
        "fractional_count": frac_cnt,
        "fractional_pct": (frac_cnt / n_arcs * 100.0) if n_arcs > 0 else 0.0,
    }
