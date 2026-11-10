# Datasets: Bank Clearing Problem & Topology-Aware Clearing

This directory contains data files, schemas, and instructions for running benchmarks on both the provided sample clearing networks and the full-scale empirical datasets used in the paper.

---

## 1. Included Sample Dataset (`sample_clearing_network.json`)

To enable immediate, zero-configuration replication without requiring multi-gigabyte blockchain downloads, this repository bundles a self-contained 100-participant financial clearing network:

- **Participants:** 100 banks / institutional accounts (5 core hub clearing banks, 95 peripheral spokes)
- **Obligations:** 297 payment obligations with heavy-tailed log-normal face values (\$2K to \$5M)
- **Topology:** Core-periphery structure featuring reciprocal bilateral obligations, hub-directed flows, and spoke clusters
- **Collateral Limits:** Synthetic deposit rule $D_i = \max(100, \alpha \cdot \text{Outflow}_i)$ at stress parameter $\alpha = 0.20$

Run instantly with:
```bash
python experiments/verify_all.py --data data/sample_clearing_network.json
```

---

## 2. Paper Empirical Datasets

### A. Stanford SNAP Ethereum ERC-20 Stablecoin Transfers
- **Source:** Stanford Network Analysis Project (SNAP) [Ethereum ERC-20 Stablecoin Transfers](https://snap.stanford.edu/data/ERC20-stablecoins.html)
- **Coins:** Tether (USDT), USD Coin (USDC), and Dai (DAI).
- **Scale:**
  - **1-Hour Window:** 3,705 accounts, 4,059 obligations, \$219.3M gross volume.
  - **12-Hour Window:** 43,406 accounts, 56,360 obligations, \$6.38B gross volume.
  - **24-Hour Window:** 82,779 accounts, 114,819 obligations, \$16.78B gross volume.
- **Deposit Policy:** Standardized synthetic deposit benchmark $D_u = \max(1, \alpha \cdot \text{Outflow}(u))$ with stress levels $\alpha \in \{0.10, 0.20, 0.40, 0.60\}$.
- **Setup for Full Replication:**
  If you have downloaded `token_transfers.csv` or `token_transfers_V3.0.0.csv`, place it in `data/` or pass the path via:
  ```bash
  python experiments/run_1s_benchmark.py --csv /path/to/token_transfers.csv
  ```

### B. Bitcoin OTC and Bitcoin Alpha Signed Trust Networks
- **Source:** SNAP [soc-sign-bitcoinotc](https://snap.stanford.edu/data/soc-sign-bitcoinotc.html) & [soc-sign-bitcoinalpha](https://snap.stanford.edu/data/soc-sign-bitcoinalpha.html)
- **Role in Research:** Used purely as non-financial topological proxies to evaluate how degree heterogeneity and cycles affect clearing heuristics on unweighted network topologies.

### C. Synthetic Scale-Free & Erdős–Rényi Networks
- **Generator:** Built into `src/graph_utils.py` (`generate_barabasi_albert_clearing_graph`).
- **Sizes:** $n \in \{10, 18, 30, 50, 100, 250, 500, 1000\}$ across 30 paired Monte Carlo trials per size.
- Run automatically via:
  ```bash
  python experiments/run_synthetic_benchmark.py
  ```

