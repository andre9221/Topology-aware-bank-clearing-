# Topology-Aware Bank Clearing: Hub–Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Solver: HiGHS](https://img.shields.io/badge/MIP%20Solver-HiGHS%201.5%2B-green.svg)](https://highs.dev/)

Official research repository and reference implementation for:

> **Topology-Aware Bank Clearing: Hub–Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement**  
> **Authors:** Andrea Amalanathan<sup>1</sup> and Sudha C<sup>2</sup>  
> *School of Computer Science and Engineering, Vellore Institute of Technology, Chennai campus, Chennai, India*  
> ✉ `andrea.a2024@vitstudent.ac.in` (ORCID: [0009-0005-2615-2701](https://orcid.org/0009-0005-2615-2701)) | `sudha.c@vit.ac.in`

---

## 🚀 Key Positive Results & Scientific Contributions

The **Bank Clearing Problem (BCP)** seeks a maximum-value subset of indivisible payment obligations whose multilateral netting satisfies participant-level deposit constraints ($\text{Out}_i(X) - \text{In}_i(X) \le D_i$). While exact branch-and-cut solvers succeed on small instances, they fail under operational real-time clearing deadlines on large production networks. This repository implements and evaluates two topology-aware algorithms: **Hub–Spoke Clearing (HSC)** and **Cycle-Aware Hub–Spoke Clearing (CA-HSC)**.

### 1. Decisive Volume Victory on Large-Scale 24-Hour Settlement (114,819 Obligations)
On the 24-hour Ethereum ERC-20 stablecoin settlement network (\$14.18B gross volume, 82,779 accounts, 114,819 obligations, collateral stress $\alpha = 0.20$):
- **CA-HSC clears $8.203 Billion in 1.27 seconds** (57.8% of the continuous LP bound, settling 46,593 payment obligations).
- **+$4.384 Billion (+114.8%)** over Plain Greedy (\$3.820B, 26.9%).
- **+$3.247 Billion (+65.5%)** over Greedy with Local Search (\$4.956B, 34.9%).
- **Exact Solvers Fail Under Real-Time Deadlines:** Cold-started HiGHS branch-and-cut times out with **$0.00 settled** within operational limits due to root LP relaxation overhead on 114k variables.
- Offline proven global optimum is \$11.96B (requiring 322.56 seconds); CA-HSC achieves **68.6% of this certified optimum in just 1.27 s** (a 254× speedup).

### 2. Sub-Second Real-Time Feasibility on 12-Hour Network (56,360 Obligations)
- **CA-HSC clears $3.040 Billion in 0.52 seconds** (61.9% of the LP bound, 21,230 obligations).
- Sub-second execution comfortably meets strict 1.0-second RTGS operational deadlines.
- More than doubles the liquidity cleared by Plain Greedy (\$1.23B, 25.1%) and Greedy+LS (\$1.59B, 32.4%).

### 3. Ultra-Fast Clearing on 1-Hour Network (4,059 Obligations)
- **CA-HSC settles $62.6 Million in 0.03 seconds (30 milliseconds)** (52.7% of LP bound, 1,678 obligations).

### 4. Bilateral Netting Efficacy (Stage 1 Dominance)
- Across all evaluated windows, **topological bilateral 2-cycles settle 56.7% to 67.8% of final cleared volume** (e.g., 2,614 reciprocal pairs releasing \$4.64B on 24h) with zero or minimal net deposit consumption.

### 5. Progressive Streaming Settlement
In an anytime streaming architecture, CA-HSC provides early liquidity finality:
- **299 ms:** \$1.99 Billion cleared (24.3% of final)
- **558 ms:** \$4.64 Billion cleared (56.6% of final; complete Stage 1 bilateral netting)
- **741 ms:** \$7.29 Billion cleared (88.9% of final; hub core commitments complete)
- **860 ms:** \$8.20 Billion cleared (100.0% of final settlement completed)

### 6. Synthetic Scale-Free Networks (Barabási-Albert Graphs)
- In 30-trial Monte Carlo tests at $n = 1,000$, HSC decomposition reaches **91.52% of the proven MIP optimum** (+3.60 percentage points over Plain Greedy at 87.92%).
- Degree-based hub selection outperforms random hub selection by **+4.66 percentage points** (95% CI 4.00–5.32; Holm-adjusted $p < 0.0001$), confirming that heavy-tailed power-law connectivity enables effective core aggregation.

---

## 📁 Repository Structure

```text
Topology-Aware-Bank-Clearing/
├── README.md                      # Project documentation, positive results, and quickstart guide
├── LICENSE                        # MIT License
├── requirements.txt               # Python package dependencies
├── .gitignore                     # Git ignore rules for caches, venvs, and large data files
├── paper/                         # Full manuscript and reviewer response deliverables
│   ├── Topology_Aware_Bank_Clearing.md    # Complete paper in GitHub-Flavored Markdown
│   ├── Topology_Aware_Bank_Clearing.docx  # Formatted Word document with styled tables & metadata
│   ├── Response_to_Reviewers.md          # Comprehensive point-by-point reviewer responses
│   └── Response_to_Reviewers.docx        # Response letter in Word format
├── src/                           # Core algorithmic implementations
│   ├── __init__.py
│   ├── ca_hsc.py                  # Cycle-Aware Hub-Spoke Clearing (Stages 1–5 + feasibility check)
│   ├── hsc.py                     # Hub-Spoke Clearing (MIP core + super-spoke aggregation + repair)
│   ├── baselines.py               # Plain Greedy, Greedy+LS, HiGHS MIP, LP relaxation
│   └── graph_utils.py             # Incidence CSC builder, synthetic BA generator, feasibility validator
├── experiments/                   # Benchmark runners & reproduction scripts
│   ├── __init__.py
│   ├── verify_all.py              # End-to-end verification suite on bundled sample network
│   ├── run_1s_benchmark.py        # 1-second deadline comparison (reproduces Table 8 & Table 9)
│   ├── run_streaming_demo.py      # Progressive anytime settlement milestone demonstration
│   └── run_synthetic_benchmark.py # Barabási-Albert scale-free benchmark (reproduces Table 3 & 5)
├── data/                          # Data files & documentation
│   ├── README.md                  # Dataset specifications & SNAP download instructions
│   └── sample_clearing_network.json # Bundled 100-bank network for instant zero-config testing
└── results/                       # Verified empirical results and execution logs
    ├── README.md                  # Detailed breakdown of empirical findings
    ├── empirical_benchmark_summary.csv # Verified ground truth benchmark numbers across all windows
    └── verification_log.txt       # Pre-generated execution log confirming feasibility and runtime
```

---

## ⚙️ Installation & Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Topology-Aware-Bank-Clearing.git
cd Topology-Aware-Bank-Clearing
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🧪 Running and Checking Instructions

### A. Instant Verification Suite (Fastest Check: <1 second)
Runs all six algorithms (LP Bound, HiGHS MIP, Plain Greedy, Greedy+LS, HSC, CA-HSC) on the included 100-bank network, verifies 100% feasibility ($\text{Out}_i - \text{In}_i \le D_i$), and prints the comparison table:
```bash
python experiments/verify_all.py
```
**Expected Output:**
```text
================================================================================
TOPOLOGY-AWARE BANK CLEARING: END-TO-END VERIFICATION SUITE
================================================================================
Method                 | Cleared ($)  | % LP Bound | % Optimum  | Time       | Status
--------------------------------------------------------------------------------
LP Relaxation (Bound)  | $13.3M       |    100.0% |    106.3% |     0.013s | Upper Bound
HiGHS MIP (Optimum)    | $12.5M       |     94.1% |    100.0% |     0.298s | Optimal
Plain Greedy           | $3.2M        |     24.0% |     25.5% |      0.3ms | Feasible
Greedy + Local Search  | $3.3M        |     24.8% |     26.4% |      0.5ms | Feasible
HSC (Decomposition)    | $11.7M       |     88.3% |     93.8% |     0.018s | Feasible
CA-HSC (Proposed)      | $5.2M        |     39.2% |     41.7% |      2.0ms | Feasible
================================================================================
[SUCCESS] All feasibility invariants verified: Out_i(X) - In_i(X) <= D_i for all participants.
[SUCCESS] Zero deposit violations detected across all tested algorithms.
```

### B. Reproduce 1-Second Operational Clearing Benchmark (Table 8)
Displays the verified head-to-head performance under the 1.0-second deadline across 1h, 12h, and 24h stablecoin networks:
```bash
python experiments/run_1s_benchmark.py
```

### C. Demonstrate Progressive Anytime Streaming Settlement (Section 7.6)
Simulates real-time payment feed processing and logs timestamped volume milestones:
```bash
python experiments/run_streaming_demo.py
```
**Milestones Logged:**
- `299 ms`: \$1.99B (24.3% of final)
- `558 ms`: \$4.64B (56.6% of final; complete bilateral netting)
- `741 ms`: \$7.29B (88.9% of final; hub core commitments complete)
- `860 ms`: \$8.20B (100.0% of CA-HSC settlement complete)

### D. Run Synthetic Scale-Free Network Benchmark (Table 3 & Table 5)
Evaluates HSC vs. Plain Greedy vs. Exact MIP on Barabási-Albert scale-free networks ($n \in \{50, 100, 250\}$):
```bash
python experiments/run_synthetic_benchmark.py
```

---

## 🔬 Algorithmic Overview

### The Bank Clearing Problem (BCP)
Given a directed obligation graph $G = (V, A)$ with face values $w(u, v) > 0$ and participant deposit collateral limits $D_i \ge 0$:
$$\max_{x \in \{0, 1\}^{|A|}} \sum_{(u, v) \in A} w(u, v) \, x_{uv}$$
$$\text{subject to} \quad \sum_{v:(i, v) \in A} w(i, v) \, x_{iv} - \sum_{u:(u, i) \in A} w(u, i) \, x_{ui} \le D_i \quad \forall i \in V$$

### CA-HSC 5-Stage Pipeline
1. **Degree-Based Topology Partitioning:** Identifies the top $k = \max(k_{\min}, \lceil \alpha \cdot |V| \rceil)$ highest-degree nodes as Hub Core $H$; all remaining participants form Spoke Periphery $S$.
2. **Bilateral 2-Cycle Netting Presolve:** Finds reciprocal obligations ($u \to v$ and $v \to u$). Mutual flow $\min(a, b)$ is deposit-neutral; only the net delta $|a - b|$ consumes collateral from the net debtor. Prioritized as $H\text{-}H \to H\text{-}S \to S\text{-}S$.
3. **Hub-Directed Core Settlement:** Weight-ordered descending scan over obligations incident to $H$.
4. **Spoke Peripheral Settlement:** Weight-ordered descending scan over internal spoke obligations ($S\text{-}S$).
5. **Incremental Refinement Sweep:** Single-pass scan re-evaluating unsettled obligations whose payers received incoming liquidity in Stages 3–4.
6. **Invariant Feasibility:** Every individual commitment checks $\text{Net}_u + w \le D_u$, guaranteeing 100% feasibility at every prefix without requiring repair.

---

## 📄 Paper & Documentation Deliverables

The complete manuscript and peer-review response files are provided in `paper/`:
- **Manuscript (Word):** [`paper/Topology_Aware_Bank_Clearing.docx`](paper/Topology_Aware_Bank_Clearing.docx)
- **Manuscript (Markdown):** [`paper/Topology_Aware_Bank_Clearing.md`](paper/Topology_Aware_Bank_Clearing.md)
- **Response to Reviewers (Word):** [`paper/Response_to_Reviewers.docx`](paper/Response_to_Reviewers.docx)
- **Response to Reviewers (Markdown):** [`paper/Response_to_Reviewers.md`](paper/Response_to_Reviewers.md)

---

## 📜 Citation

If you use this codebase or paper in your research, please cite:

```bibtex
@article{amalanathan2026topology,
  title={Topology-Aware Bank Clearing: Hub--Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement},
  author={Amalanathan, Andrea and Sudha, C.},
  journal={Working Paper, School of Computer Science and Engineering, Vellore Institute of Technology, Chennai campus},
  year={2026}
}
```

---

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
