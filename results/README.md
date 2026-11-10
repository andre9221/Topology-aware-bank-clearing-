# Empirical Benchmark Results, Raw Data, and Solver Logs

This directory contains the complete empirical data, aggregated summaries, raw trial runs, and actual solver execution logs accompanying the paper:
**"Topology-Aware Bank Clearing: Hub–Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement"** (Andrea Amalanathan & Sudha C, VIT Chennai), as detailed in [`Topology_Aware_Bank_Clearing_Renumbered.docx`](../Topology_Aware_Bank_Clearing_Renumbered.docx).

---

## 📑 Paper Table to File Mapping Matrix

Every table in the renumbered manuscript directly corresponds to the empirical files in this folder:

| Manuscript Table | Description | Primary CSV / Log Files | Directory |
| :--- | :--- | :--- | :--- |
| **Table 2** | Network Sizes (Accounts, Arcs, Gross Volumes) | `results_real_data_full.csv`, `results_stablecoin_real_flows.csv` | [`02_bitcoin_trust_proxies/`](02_bitcoin_trust_proxies/), [`03_stablecoin_clearing/`](03_stablecoin_clearing/) |
| **Table 3** | HSC vs. Plain Greedy on Scale-Free Graphs (30 paired trials, $n = 10 \dots 1,000$) | `results_main_comparison_30trials.csv`<br>`summary_main_comparison_30trials.csv` | [`01_scale_free_benchmarks/`](01_scale_free_benchmarks/) |
| **Table 4** | Hub-Selection Ablation at $n = 250$ (Degree vs. Random vs. Lowest vs. No-Hub) | `results_no_hub_30trials.csv`<br>`summary_no_hub_30trials.csv`<br>`results_k_frac_tradeoff_30trials.csv` | [`01_scale_free_benchmarks/`](01_scale_free_benchmarks/) |
| **Table 5** | Strong-Baseline Comparison on Scale-Free Instances ($n = 250, 1000$) | `results_adaptive_k_30trials.csv`<br>`summary_adaptive_k_30trials.csv`<br>`results_density_impact_30trials.csv` | [`05_additional_sweeps/`](05_additional_sweeps/) |
| **Table 6** | Representative Bitcoin Trust-Network Proxy Results (Full OTC, Alpha, Weekly) | `results_real_data_full.csv`<br>`summary_real_data.csv`<br>`results_real_data_weekly.csv` | [`02_bitcoin_trust_proxies/`](02_bitcoin_trust_proxies/) |
| **Table 7** | 1-Hour Stablecoin Sensitivity & LP Relaxation Integrality Gaps ($\alpha = 0.10 \dots 0.60$) | `results_lp_integrality_gap.csv`<br>`results_stablecoin_real_flows.csv`<br>`results_stress_test.csv` | [`03_stablecoin_clearing/`](03_stablecoin_clearing/), [`05_additional_sweeps/`](05_additional_sweeps/) |
| **Table 8** | CA-HSC Head-to-Head 1-Second Operational Benchmark (1h, 12h, 24h Windows) | `rigorous_benchmark_results.csv`<br>`results_hsc_comparison.csv` | [`03_stablecoin_clearing/`](03_stablecoin_clearing/) |
| **Table 9** | CA-HSC Stage Contributions (Bilateral 2-Cycles, Hub Core, Spokes, Refinement) | `rigorous_benchmark_results.csv`<br>`benchmark_results_snap.json` | [`03_stablecoin_clearing/`](03_stablecoin_clearing/) |
| **Table 10** | Selected Offline Comparisons & Provable Global Optima | `rigorous_benchmark_results.csv`<br>`highs_cold_seed_*.log`<br>`highs_warm_seed_*.log` | [`03_stablecoin_clearing/`](03_stablecoin_clearing/), [`04_solver_logs/`](04_solver_logs/) |

---

## 🌟 Key Positive Findings Represented in These Results

### 1. Massive Settlement Volume on 24-Hour Network (114,819 Obligations)
*(File: `03_stablecoin_clearing/rigorous_benchmark_results.csv`)*
- **CA-HSC settles $8.203 Billion in 1.27 seconds** (57.8% of the continuous LP bound, committing 46,593 payment obligations).
- **Outperforms Plain Greedy ($3.820B, 26.9%) by +$4.384 Billion (+114.8%)**.
- **Outperforms Greedy + Local Search ($4.956B, 34.9%) by +$3.247 Billion (+65.5%)**.
- Exact cold-start MIP solvers strictly time out with **$0.00** settled within operational limits due to root LP overhead across 114k variables.
- Offline proven optimum is **$11.96 Billion** (certified in 322.56 s in `04_solver_logs/highs_cold_seed_1.log`). CA-HSC recovers **68.6% of this certified optimum in 1.27 s** (a 254× speedup).

### 2. Sub-Second Real-Time Feasibility on 12-Hour Network (56,360 Obligations)
*(File: `03_stablecoin_clearing/rigorous_benchmark_results.csv`)*
- **CA-HSC clears $3.040 Billion in 0.52 seconds** (61.9% of the LP bound, 21,230 obligations).
- Easily meets the 1.0-second RTGS deadline while more than doubling the volume cleared by Plain Greedy ($1.23B, 25.1%) and Greedy+LS ($1.59B, 32.4%).

### 3. Bilateral Netting Efficacy (Stage 1 Dominance)
*(Files: `03_stablecoin_clearing/rigorous_benchmark_results.csv`, `benchmark_results_snap.json`)*
- Bilateral 2-cycle presolve settles **56.7% to 67.8% of the final cleared volume** with minimal/zero collateral consumption:
  - 1-Hour window: **$42.4M (67.8%)** settled via reciprocal cycles.
  - 12-Hour window: **$1.96B (64.5%)** settled via reciprocal cycles.
  - 24-Hour window: **$4.64B (56.7%)** settled via 2,614 reciprocal pairs.

### 4. Synthetic Scale-Free Network Optimality
*(Files: `01_scale_free_benchmarks/results_main_comparison_30trials.csv`, `summary_main_comparison_30trials.csv`)*
- In 30 paired Monte Carlo trials at $n = 1,000$, HSC decomposition clears **91.52% ± 0.50% of provable global MIP optimality** (+3.60 percentage points over Plain Greedy at 87.92%).
- Degree-selected hubs significantly outperform random hubs (+4.66 percentage points; Holm-adjusted $p < 0.0001$), confirming that power-law degree concentration drives the effectiveness of core aggregation.

---

## 📁 Directory Breakdown & File Schemas

### `01_scale_free_benchmarks/`
- `results_main_comparison_30trials.csv`: 240 paired trials across $n \in \{10, 18, 30, 50, 100, 250, 500, 1000\}$ comparing Exact MIP, Plain Greedy, and HSC.
- `summary_main_comparison_30trials.csv`: Means, standard deviations, and confidence intervals matching **Table 3**.
- `results_no_hub_30trials.csv` & `summary_no_hub_30trials.csv`: Topology ablation on scale-free vs. Erdős–Rényi graphs matching **Table 4**.
- `results_k_frac_tradeoff_30trials.csv` & `summary_k_frac_tradeoff_30trials.csv`: Sweep of hub fraction $k/n \in \{0.02, 0.04, 0.06, 0.10, 0.16\}$.

### `02_bitcoin_trust_proxies/`
- `results_real_data_full.csv` & `summary_real_data.csv`: Performance on Bitcoin OTC (5,881 nodes, 32,029 arcs) and Bitcoin Alpha (3,783 nodes, 22,650 arcs) matching **Table 6**.
- `results_real_data_weekly.csv` & `summary_real_data_weekly.csv`: Longitudinal analysis across 256 consecutive weekly transaction snapshots (mean cleared proxy weight: 49.38% HSC vs. 47.69% Greedy, $p < 0.0001$).
- `results_real_data_temporal.csv` & `results_real_data_subgraph.csv`: Multi-slice temporal partition benchmarks.

### `03_stablecoin_clearing/`
- `rigorous_benchmark_results.csv`: Ground-truth benchmark data for 1h, 12h, and 24h stablecoin networks under strict 1.0s operational deadline and offline optimization (**Table 8, Table 9, Table 10**).
- `results_stablecoin_real_flows.csv`: Sensitivity analysis of deposit factor $\alpha \in \{0.10, 0.20, 0.40, 0.60\}$ (**Table 7**).
- `results_lp_integrality_gap.csv`: Polyhedral diagnostics showing continuous LP integrality gaps (33.19%–52.31%) and fractional variable shares (30.53%–45.49%).
- `results_hsc_comparison.csv`: Comparative ablation between HSC decomposition and baseline methods.
- `benchmark_results_snap.json`: Detailed JSON telemetry of stage-by-stage transaction volumes and counts.

### `04_solver_logs/`
Actual execution logs produced by the HiGHS branch-and-cut solver:
- `highs_cold_seed_1.log`, `highs_cold_seed_2.log`, `highs_cold_seed_42.log`: Cold-start branch-and-cut certifying provable global optimality on the 24-hour network ($11.96B cleared, 0.31% optimality gap).
- `highs_warm_seed_1.log`, `highs_warm_seed_2.log`, `highs_warm_seed_42.log`: Solver runs warm-started by heuristic initializations.
- `rerun_cold_*.log` & `rerun_warm_*.log`: Independent verification replications certifying reproducible dual bounds.

### `05_additional_sweeps/`
- `results_stress_test.csv` & `summary_stress_test.csv`: 450-trial liquidity stress sweep evaluating varying solver time limits and graph sizes.
- `results_hardness_sweep.csv` & `summary_hardness_sweep.csv`: Computational hardness evaluation across varied payment weight bounds ($w_{\max}$) and graph density ratios.
- `results_adaptive_k_30trials.csv` & `summary_adaptive_k_30trials.csv`: Adaptive eigenvalue-based hub budget selection vs. fixed percentage rules (**Table 5**).
- `results_density_impact_30trials.csv` & `summary_density_impact_30trials.csv`: Performance impact of edge density ($m/n$) in scale-free graphs.
