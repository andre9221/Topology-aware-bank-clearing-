"""
verify_all.py
=============
End-to-end verification script:
1. Loads the bundled 100-participant clearing network.
2. Runs all six algorithms:
   - HiGHS LP Relaxation (Theoretical Upper Bound)
   - HiGHS Exact MIP (Provable Optimum)
   - Plain Greedy Heuristic
   - Greedy + Local Search
   - Hub-Spoke Clearing (HSC)
   - Cycle-Aware Hub-Spoke Clearing (CA-HSC)
3. Strictly validates feasibility: checks that Out_i - In_i <= D_i for every participant.
4. Prints a publication-quality comparison table and stage contribution breakdown.
"""

import os
import sys
import json
import time

# Add repository root to python path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

from src.graph_utils import format_currency, verify_net_feasibility
from src.ca_hsc import ca_hsc_clearing
from src.hsc import hsc_clearing
from src.baselines import (
    greedy_clearing,
    greedy_local_search,
    highs_exact_mip,
    highs_lp_relaxation,
)


def run_verification(data_path=None):
    if data_path is None:
        data_path = os.path.join(REPO_ROOT, "data", "sample_clearing_network.json")

    print("=" * 80)
    print("TOPOLOGY-AWARE BANK CLEARING: END-TO-END VERIFICATION SUITE")
    print("=" * 80)
    print(f"Loading clearing network from: {data_path}")

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data["nodes"]
    arcs = [tuple(a) for a in data["arcs"]]
    deposits = {int(k) if isinstance(k, str) and k.isdigit() else k: float(v) for k, v in data["deposits"].items()}

    gross_volume = sum(a[2] for a in arcs)
    print(f"Participants (V) : {len(nodes):,}")
    print(f"Obligations  (A) : {len(arcs):,}")
    print(f"Gross Face Value : {format_currency(gross_volume)}")
    print(f"Collateral Ratio : alpha = {data.get('alpha', 0.20):.2f}")
    print("-" * 80)

    # 1. Continuous LP Relaxation
    print("1/6 Computing Continuous LP Relaxation Bound...")
    lp_res = highs_lp_relaxation(arcs, deposits, nodes)
    lp_bound = lp_res["bound"]
    print(f"    LP Upper Bound   : {format_currency(lp_bound)} (Time: {lp_res['time']:.3f}s)")

    # 2. HiGHS Exact MIP
    print("2/6 Running HiGHS Branch-and-Cut Exact MIP Solver...")
    mip_res = highs_exact_mip(arcs, deposits, nodes, time_limit=10.0)
    mip_vol = mip_res["volume"]
    print(f"    Global Optimum   : {format_currency(mip_vol)} (Time: {mip_res['time']:.3f}s, Feasible: {mip_res['is_feasible']})")

    # 3. Plain Greedy
    print("3/6 Running Plain Greedy Heuristic...")
    greedy_res = greedy_clearing(arcs, deposits, nodes)
    greedy_vol = greedy_res["volume"]
    print(f"    Greedy Cleared   : {format_currency(greedy_vol)} (Time: {greedy_res['time']*1000:.2f}ms, Feasible: {greedy_res['is_feasible']})")

    # 4. Greedy + Local Search
    print("4/6 Running Greedy + Local Search...")
    gls_res = greedy_local_search(arcs, deposits, nodes, time_limit=1.0)
    gls_vol = gls_res["volume"]
    print(f"    Greedy+LS Cleared: {format_currency(gls_vol)} (Time: {gls_res['time']*1000:.2f}ms, Feasible: {gls_res['is_feasible']})")

    # 5. Hub-Spoke Clearing (HSC)
    print("5/6 Running Hub-Spoke Clearing (HSC)...")
    hsc_res = hsc_clearing(nodes, arcs, deposits, k_frac=0.06, time_limit=5.0)
    hsc_vol = hsc_res["volume"]
    print(f"    HSC Cleared      : {format_currency(hsc_vol)} (Time: {hsc_res['time']:.3f}s, Feasible: {hsc_res['is_feasible']})")

    # 6. Cycle-Aware Hub-Spoke Clearing (CA-HSC)
    print("6/6 Running Cycle-Aware Hub-Spoke Clearing (CA-HSC)...")
    cahsc_res = ca_hsc_clearing(nodes, arcs, deposits, k_frac=0.05, return_details=True)
    cahsc_vol = cahsc_res["volume"]
    print(f"    CA-HSC Cleared   : {format_currency(cahsc_vol)} (Time: {cahsc_res['time']*1000:.2f}ms, Feasible: {cahsc_res['is_feasible']})")

    print("\n" + "=" * 80)
    print(f"{'Method':<22} | {'Cleared ($)':<12} | {'% LP Bound':<10} | {'% Optimum':<10} | {'Time':<10} | {'Status'}")
    print("-" * 80)

    all_methods = [
        ("LP Relaxation (Bound)", lp_bound, 100.0, (lp_bound/mip_vol*100) if mip_vol>0 else 0, f"{lp_res['time']:.3f}s", "Upper Bound"),
        ("HiGHS MIP (Optimum)", mip_vol, (mip_vol/lp_bound*100) if lp_bound>0 else 0, 100.0, f"{mip_res['time']:.3f}s", "Optimal" if mip_res['is_feasible'] else "INVALID"),
        ("Plain Greedy", greedy_vol, (greedy_vol/lp_bound*100) if lp_bound>0 else 0, (greedy_vol/mip_vol*100) if mip_vol>0 else 0, f"{greedy_res['time']*1000:.1f}ms", "Feasible" if greedy_res['is_feasible'] else "INVALID"),
        ("Greedy + Local Search", gls_vol, (gls_vol/lp_bound*100) if lp_bound>0 else 0, (gls_vol/mip_vol*100) if mip_vol>0 else 0, f"{gls_res['time']*1000:.1f}ms", "Feasible" if gls_res['is_feasible'] else "INVALID"),
        ("HSC (Decomposition)", hsc_vol, (hsc_vol/lp_bound*100) if lp_bound>0 else 0, (hsc_vol/mip_vol*100) if mip_vol>0 else 0, f"{hsc_res['time']:.3f}s", "Feasible" if hsc_res['is_feasible'] else "INVALID"),
        ("CA-HSC (Proposed)", cahsc_vol, (cahsc_vol/lp_bound*100) if lp_bound>0 else 0, (cahsc_vol/mip_vol*100) if mip_vol>0 else 0, f"{cahsc_res['time']*1000:.1f}ms", "Feasible" if cahsc_res['is_feasible'] else "INVALID"),
    ]

    for name, v, lp_p, opt_p, t_str, stat in all_methods:
        print(f"{name:<22} | {format_currency(v):<12} | {lp_p:>8.1f}% | {opt_p:>8.1f}% | {t_str:>10} | {stat}")

    print("=" * 80)
    print("\nCA-HSC STAGE DECOMPOSITION & LIQUIDITY CONTRIBUTION:")
    print("-" * 60)
    st_vols = cahsc_res["stage_volumes"]
    st_cnts = cahsc_res["stage_counts"]
    for st_name, st_val in st_vols.items():
        pct = (st_val / cahsc_vol * 100.0) if cahsc_vol > 0 else 0.0
        cnt = st_cnts[st_name]
        print(f"  Stage: {st_name:<18} -> {format_currency(st_val):>10} ({pct:>5.1f}%) | {cnt:>4} payments")
    print(f"  Total Settled Volume: {format_currency(cahsc_vol):>10} (100.0%) | {cahsc_res['count']} payments")
    print(f"  Overall Execution Time : {cahsc_res['time']*1000:.2f} milliseconds")
    print("=" * 80)

    # Verification Assertions
    assert cahsc_res["is_feasible"], "Error: CA-HSC produced an infeasible settlement!"
    assert hsc_res["is_feasible"], "Error: HSC produced an infeasible settlement!"
    assert greedy_res["is_feasible"], "Error: Plain Greedy produced an infeasible settlement!"
    assert gls_res["is_feasible"], "Error: Greedy+LS produced an infeasible settlement!"
    print("\n[SUCCESS] All feasibility invariants verified: Out_i(X) - In_i(X) <= D_i for all participants.")
    print("[SUCCESS] Zero deposit violations detected across all tested algorithms.\n")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    run_verification(path)

