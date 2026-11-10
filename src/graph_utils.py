"""
graph_utils.py
==============
Network graph utilities, sparse matrix builders, synthetic generators,
and strict feasibility validators for the Bank Clearing Problem (BCP).
"""

import collections
import math
import random
import numpy as np
import scipy.sparse as sp


def format_currency(v):
    """Format floating point values into standard human-readable financial currency."""
    if abs(v) >= 1e9:
        return f"${v/1e9:.2f}B"
    elif abs(v) >= 1e6:
        return f"${v/1e6:.1f}M"
    elif abs(v) >= 1e3:
        return f"${v/1e3:.1f}K"
    else:
        return f"${v:,.2f}"


def build_incidence_csc(node_to_idx, arcs):
    """
    Construct the Compressed Sparse Column (CSC) incidence matrix A for the BCP:
        Row i represents participant i.
        Column j represents obligation arc (u -> v) with weight w.
        A[u, j] = +w  (payer outgoing debit)
        A[v, j] = -w  (payee incoming credit)
    """
    n_arcs = len(arcs)
    n_nodes = len(node_to_idx)

    # 2 non-zero entries per column (payer +, payee -)
    rows = np.empty(2 * n_arcs, dtype=np.int32)
    cols = np.empty(2 * n_arcs, dtype=np.int32)
    data = np.empty(2 * n_arcs, dtype=np.float64)

    for j, (u, v, w) in enumerate(arcs):
        p_idx = 2 * j
        wf = float(w)
        rows[p_idx] = node_to_idx[u]
        cols[p_idx] = j
        data[p_idx] = wf

        rows[p_idx + 1] = node_to_idx[v]
        cols[p_idx + 1] = j
        data[p_idx + 1] = -wf

    return sp.csc_matrix((data, (rows, cols)), shape=(n_nodes, n_arcs))


def verify_net_feasibility(node_list, arcs, deposits, in_solution_mask, tol=1e-7):
    """
    Strictly verify that the chosen clearing solution satisfies:
        Out_i(X) - In_i(X) <= D_i + tol  for all i in V.

    Returns
    -------
    tuple (is_feasible: bool, max_violation: float, net_positions: dict)
    """
    net = {nd: 0.0 for nd in node_list}
    for j, is_cleared in enumerate(in_solution_mask):
        if is_cleared:
            u, v, w = arcs[j]
            net[u] += float(w)
            net[v] -= float(w)

    max_viol = 0.0
    for nd in node_list:
        diff = net[nd] - (deposits.get(nd, 0.0) + tol)
        if diff > max_viol:
            max_viol = diff

    is_feasible = (max_viol <= 0.0)
    return is_feasible, max_viol, net


def generate_barabasi_albert_clearing_graph(n=250, m_attach=3, alpha=0.20, seed=42):
    """
    Generate a directed scale-free network using the Barabási-Albert preferential
    attachment model with log-normal financial obligation values and synthetic deposits.
    """
    import networkx as nx

    rng = random.Random(seed)
    # Undirected base BA graph
    G_undir = nx.barabasi_albert_graph(n, m_attach, seed=seed)

    # Direct edges randomly or preferentially
    arcs = []
    outflows = collections.defaultdict(float)
    nodes = list(range(n))

    for u, v in G_undir.edges():
        # Edge direction: forward, backward, or bilateral (reciprocal)
        r = rng.random()
        # Heavy-tailed log-normal transaction face value ($100 to $1,000,000)
        w1 = float(np.exp(rng.gauss(mu=8.0, sigma=1.8)))
        if r < 0.40:
            arcs.append((u, v, round(w1, 2)))
            outflows[u] += w1
        elif r < 0.80:
            arcs.append((v, u, round(w1, 2)))
            outflows[v] += w1
        else:
            # Reciprocal 2-cycle
            w2 = float(np.exp(rng.gauss(mu=8.0, sigma=1.8)))
            arcs.append((u, v, round(w1, 2)))
            arcs.append((v, u, round(w2, 2)))
            outflows[u] += w1
            outflows[v] += w2

    # Synthetic deposit: D_u = max(1.0, alpha * Outflow(u))
    deposits = {}
    for nd in nodes:
        deposits[nd] = max(1.0, round(alpha * outflows[nd], 2))

    return nodes, arcs, deposits
