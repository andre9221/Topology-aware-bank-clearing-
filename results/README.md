# Experimental Results and Benchmark Synthesis

This directory contains verified empirical benchmark data, execution logs, and detailed analysis corresponding to the published paper:
**"Topology-Aware Bank Clearing: Hub–Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement"** (Andrea Amalanathan & Sudha C, VIT Chennai).

---

## 1. Executive Summary of Key Positive Results

### A. Large-Scale 24-Hour Settlement Performance (114,819 Obligations)
In high-throughput, production-scale financial settlement environments where exact solvers cannot operate under operational deadlines:
- **CA-HSC clears $8.203 Billion in 1.27 seconds** (57.8% of the continuous LP bound, settling 46,593 payment obligations).
- **Outperforms Plain Greedy ($3.820 Billion, 26.9%) by +$4.384 Billion (+114.8%)**.
- **Outperforms Greedy + Local Search ($4.956 Billion, 34.9%) by +$3.247 Billion (+65.5%)**.
- **Exact MIP Solvers Fail Completely:** Cold-started HiGHS MIP times out with **$0.00 settled** within operational limits due to root LP relaxation overhead on 114k variables.
- Offline branch-and-cut requires **322.56 seconds** to certify the global optimum ($11.96B); CA-HSC attains **68.6% of this global optimum in just 1.27 s** (a 254× speedup).

### B. Sub-Second Real-Time Feasibility on 12-Hour Network (56,360 Obligations)
- **CA-HSC clears $3.040 Billion in 0.52 seconds** (61.9% of the $4.91B LP bound, 21,230 obligations).
- Sub-second execution comfortably clears the strict 1.0-second RTGS deadline.
- More than doubles the liquidity cleared by Plain Greedy ($1.23B, 25.1%) and Greedy+LS ($1.59B, 32.4%).

### C. Ultra-Fast Clearing on 1-Hour Network (4,059 Obligations)
- **CA-HSC settles $62.6 Million in 0.03 seconds (30 milliseconds)** (52.7% of LP bound, 1,678 obligations).

---

## 2. Table 8: Head-to-Head 1-Second Operational Clearing Benchmark ($\alpha = 0.20$)

| Settlement Window | Algorithm | Cleared Volume ($) | % of LP Bound | Settled Payments | Execution Time | Status / Operational Outcome |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **24 Hours** (114,819 arcs) | **HiGHS MIP** | \$0.00 | 0.0% | 0 | 1.90 s | No incumbent (Timeout) |
| | **Plain Greedy** | \$3.820B | 26.9% | 37,777 | 0.25 s | Feasible |
| | **Greedy + LS** | \$4.956B | 34.9% | 46,216 | 0.38 s | Feasible |
| | **CA-HSC (Proposed)** | **\$8.203B** | **57.8%** | **46,593** | **1.27 s** | **Feasible (+$4.384B / +114.8% vs. Greedy)** |
| **12 Hours** (56,360 arcs) | **HiGHS MIP** | \$0.00 | 0.0% | 0 | 1.34 s | No incumbent (Timeout) |
| | **Plain Greedy** | \$1.23B | 25.1% | 17,730 | 0.09 s | Feasible |
| | **Greedy + LS** | \$1.59B | 32.4% | 21,314 | 0.17 s | Feasible |
| | **CA-HSC (Proposed)** | **\$3.04B** | **61.9%** | **21,230** | **0.52 s** | **Feasible (Sub-second real-time)** |
| **1 Hour** (4,059 arcs) | **HiGHS MIP** | \$71.5M | 60.3% | 1,999 | 1.02 s | Partial Incumbent |
| | **Plain Greedy** | \$30.0M | 25.3% | 1,585 | <0.01 s | Feasible |
| | **CA-HSC (Proposed)** | **\$62.6M** | **52.7%** | **1,678** | **0.03 s** | **Feasible (30 ms execution)** |

---

## 3. Table 9: CA-HSC Stage Contributions & Bilateral Netting Efficacy

The multi-stage design reveals that topological cycle identification provides the overwhelming majority of settled value:

| Pipeline Stage | 1-Hour Window | 12-Hour Window | 24-Hour Window | Key Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **Stage 1: Bilateral 2-Cycles** | \$42.4M (67.8%) | \$1.96B (64.5%) | **\$4.64B (56.7%)** | Mutual reciprocal offset; zero net deposit consumed for balanced flow |
| **Stage 2: Hub-Directed Core** | \$17.8M (28.5%) | \$685.6M (22.6%) | **\$2.41B (29.5%)** | Weight-ordered clearing across central liquidity routing hubs |
| **Stage 3: Spoke Clusters** | \$1.8M (2.9%) | \$48.2M (1.6%) | **\$150.3M (1.8%)** | Residual clearing among peripheral participants |
| **Stage 4: 1-Opt Refinement** | \$0.45M (0.7%) | \$344.4M (11.3%) | **\$983.2M (12.0%)** | Single-pass sweep capturing newly funded obligations |
| **Total Settled Volume** | **\$62.6M (100%)** | **\$3.04B (100%)** | **\$8.18B - \$8.20B** | **Strict Invariant Feasibility Guaranteed** |

---

## 4. Progressive Anytime Streaming Milestones

In a real-time streaming environment, CA-HSC outputs certified feasible payment subsets continuously without waiting for total completion:

- **299 ms:** \$1.99 Billion cleared (24.3% of final)
- **558 ms:** \$4.64 Billion cleared (56.6% of final; complete Stage 1 bilateral netting)
- **741 ms:** \$7.29 Billion cleared (88.9% of final; hub core commitments complete)
- **860 ms:** \$8.20 Billion cleared (100.0% of final settlement completed)

---

## 5. Synthetic Scale-Free Network Performance (Barabási-Albert Graphs)

Evaluated across 30 paired Monte Carlo trials per graph size under liquidity stress $\alpha = 0.20$:

- At **$n = 1,000$ nodes:** HSC decomposition achieves **91.52% ± 0.50% of the proven MIP optimum** (+3.60 percentage points over Plain Greedy at 87.92%).
- Hub-selection ablation confirms that degree-selected hubs outperform randomly selected hubs by **+4.66 percentage points** (95% CI 4.00–5.32; Holm-adjusted $p < 0.0001$), empirically confirming that power-law degree concentration drives the effectiveness of topology-aware partitioning.
