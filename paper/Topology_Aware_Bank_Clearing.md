Topology-Aware Bank Clearing: Hub–Spoke Decomposition, Cycle-Aware Heuristics, and Large-Scale Settlement
Andrea Amalanathan1
School of Computer Science and Engineering, Vellore Institute of Technology, Chennai campus,
Chennai, India.
[andrea.a2024@vitstudent.ac.in](mailto:andrea.a2024@vitstudent.ac.in)
ORCID: 0009-0005-2615-2701
Sudha C 2,
Vellore Institute of Technology
Chennai campus,
Chennai, India
[sudha.c@vit.ac.in](mailto:sudha.c@vit.ac.in)
ORCID:
1. Abstract
The Bank Clearing Problem (BCP) selects indivisible payment obligations to maximize settled value while ensuring that each participant’s net debit does not exceed its available deposit. This study evaluates two topology-aware methods: Hub–Spoke Clearing (HSC), which applies integer programming to an aggregated hub core and repairs peripheral decisions, and Cycle-Aware Hub–Spoke Clearing (CA-HSC), a deterministic multi-stage heuristic without an integer program. Experiments cover synthetic scale-free and Erdős–Rényi graphs, Bitcoin OTC/Alpha trust-rating networks used only as topology proxies, and public Ethereum ERC-20 stablecoin transfers (USDT, USDC and DAI) with synthetic deposits. In 30-trial scale-free tests, HSC reaches 91.52% of the exact optimum at 1,000 nodes, compared with 87.92% for plain greedy. However, greedy with local search reaches 99.03%, and a time-matched exact run reaches 99.22%, showing that HSC’s gain is baseline-dependent. On a one-hour stablecoin sensitivity experiment, the LP integrality gap ranges from 33.19% to 52.31%; at a deposit factor α = 0.20, plain greedy clears 26.9% of the LP bound on the 24-hour network. CA-HSC clears $3.04 billion in 0.52 s on 56,360 obligations (61.9% of the LP bound) and $8.203 billion in 1.27 s on 114,819 obligations (57.8%). Its bilateral-cycle stage contributes 56.7–67.8% of final volume. An offline exact run later proves a $11.96 billion optimum for the 24-hour instance in 322.56 s; CA-HSC attains 68.6% of that optimum. These findings demonstrate a quality–latency trade-off under modeled liquidity constraints, not validated performance on central-bank settlement data.
Keywords—bank clearing problem; liquidity-saving mechanisms; interbank payment networks; hub–spoke decomposition; bilateral netting; mixed-integer programming; stablecoin transfers.
2. Introduction
Real-time gross settlement (RTGS) systems reduce settlement risk by transferring payments individually, but they can require substantial intraday liquidity. Liquidity-saving mechanisms (LSMs) coordinate payment release and offset obligations to reduce funding pressure. The computational problem considered here is the selection of a maximum-value subset of indivisible obligations subject to participant-level net-debit constraints. Exact formulations can provide optimal solutions, but their runtime can become prohibitive as the number of obligations increases [1, 2].
Payment networks are heterogeneous. Core–periphery structure and high-degree institutions can influence the propagation of incoming and outgoing payments, while public blockchain transfer networks contain highly skewed transaction values. Recent work studies strategic effects of LSMs, dynamic clearing policies, and optimization of payment batches, but these objectives and settings differ from the static indivisible-obligation problem examined here [2–4].
This paper evaluates two distinct algorithms. HSC applies exact integer programming to a degree-selected hub core and uses aggregation, spoke allocation, and feasibility repair. CA-HSC removes the integer program and uses deposit-checked bilateral-cycle settlement followed by hub-directed, spoke-cluster, and incremental passes. The experiments report both favorable and unfavorable results: topology-aware HSC can improve on plain greedy in synthetic scale-free graphs, but stronger baselines outperform it; CA-HSC provides much higher cleared volume than plain greedy on the largest modeled stablecoin network, but its 24-hour runtime exceeds one second.
The contributions are: (i) a hub–spoke decomposition with a terminating feasibility repair; (ii) a cycle-aware heuristic that maintains feasibility at each commitment; (iii) a comparative evaluation across synthetic, trust-proxy, and stablecoin-transfer networks; and (iv) an explicit characterization of the quality–latency trade-off, including a proven large-instance optimum. The stablecoin transfers are not treated as bank-to-bank settlement instructions, and all deposits used in these experiments are synthetic.
3. Related Work
3.1. Algorithmic clearing and liquidity-saving mechanisms
Cambe and Xing [1] formulate the bank-clearing problem as a solver-based optimization task and report that their method outperforms two established offsetting algorithms in more than 91% of their simulations. This motivates an optimization benchmark, but does not imply that exact or solver-based methods satisfy every strict latency budget. Chen, Baron, and Chen [2] study dynamic clearing with payment arrivals, setup costs, variable clearing costs, and liquidity costs; their dynamic-programming objective differs from the static maximum-value subset selection used here. Hayakawa [3] examines strategic payment timing in core–periphery networks, while Astuti et al. [4] optimize the order of payment batches in TARGET2 with a constrained quadratic model. These studies motivate liquidity-aware optimization, but none directly evaluates HSC or CA-HSC.
3.2. Network topology, clearing theory, and settlement dynamics
Hüser [5] surveys interbank-network structure and systemic-risk research, providing context for why connectivity and concentration matter. Hayakawa [6] studies liquidity in financial networks, and Eboli et al. [7] show that connectivity and centralization can create a robustness–fragility trade-off under shocks. Csóka and Herings [8] characterize existence and uniqueness properties of clearing payment matrices using strongly connected components. These studies concern system structure, contagion, or payment-matrix clearing rather than the discrete selection of indivisible obligations under participant-level deposit constraints.
Research on liquidity provision and LSM design addresses incentives as well as algorithms. Nellen [9] studies collateralized intraday credit and settlement coordination; Byck and Heijmans [10] simulate bilateral offsetting, FIFO bypass, multilateral offsetting, and combined mechanisms using Canadian LVTS data. Garratt [11] applies Shapley-value cost allocation to a centralized netting queue, while Nellen [12] examines how liquidity-facility design and late-settlement fees affect coordination. Ketelaars and Borm [13] unify centralized and decentralized clearing mechanisms in a claims-based financial-network framework. Banerjee et al. [14] extend clearing and contagion to continuous-time RTGS dynamics. Garratt et al. [15] investigate auction-based liquidity-saving mechanisms, and Mattern and Meyer [16] identify critical participants in Switzerland’s SIC RTGS system using payment type, frequency, and value/volume views. Capponi and Chang [17] show that the welfare and systemic-risk effects of settlement speed depend on topology and liquidity conditions. Together, these papers establish that clearing quality, liquidity use, incentives, and timing are linked, but they do not supply a directly comparable benchmark for the HSC/CA-HSC obligation-selection objective.
3.3. Stablecoin studies and interpretation of the evaluation data
Nguyen et al. [18] study interdependence in the price stability of USDT, USDC, DAI, and other stablecoins; this is market-stability evidence, not a clearing algorithm. Schär et al. [19] distinguish token-transfer event logs from complex Ethereum transactions that may bundle multiple operations, warning against treating every transfer event as an independent economic payment. Lee and Tou [20] link stablecoin primary-market activity to wholesale interbank payment data and find evidence of liquidity exposure at banks connected to stablecoin deposits. These studies motivate careful use of blockchain data while reinforcing a key limitation here: observed on-chain transfer values are real, but the deposit constraints in our clearing experiments are synthetic, and the data do not constitute institutional RTGS instructions.
Table 1. Detailed comparison of 20 studies relevant to topology-aware bank clearing.
Study
Research question / method
Data, setting, or principal finding
Relevance and distinction from this paper
Cambe & Xing (2024) [1]
Solver-based optimization for the bank-clearing problem; compares a MILP-based approach with established offsetting algorithms.
Reports better performance than two established algorithms in more than 91% of simulation instances; does not guarantee global optimality for every instance.
Closest algorithmic comparator and motivation for exact/solver baselines. The present study focuses on topology-aware decomposition and strict runtime–quality trade-offs at larger graph sizes.
Chen, Baron & Chen (2024 online; 2025 issue) [2]
Dynamic programming for optimal clearing frequency when obligations arrive over time; accounts for setup, variable clearing, and liquidity costs.
Case study uses industrial-scale Payments Canada debt data; derives structural properties of dynamic clearing policies.
Establishes the importance of time-dependent clearing, but optimizes when to clear rather than selecting a maximum-value static subset of indivisible obligations.
Hayakawa (2025) [3]
Strategic network model of bank payment timing and liquidity-saving mechanisms in interconnected/core–periphery systems.
Shows that LSM effects depend on network structure and participants’ incentives.
Supports topology-sensitive evaluation. It models strategic behavior and welfare, not the computational performance of HSC or CA-HSC.
Astuti et al. (2026) [4]
Constrained quadratic model / quantum-assisted reordering of payment batches in gross settlement.
TARGET2 application reports average daily liquidity savings of approximately €23M–€38M across a 35-day sample for batch sizes 70 and 140.
Recent optimization comparator on operational payment data; objective is batch reordering and liquidity savings, not discrete obligation-subset maximization.
Hüser (2015) [5]
Survey of interbank-network literature on interconnectedness, network formation, contagion, and systemic risk.
Synthesizes evidence that network architecture is central to understanding financial-system vulnerability.
Provides broad network context. It is a survey rather than an algorithmic clearing benchmark.
Hayakawa (2020) [6]
Graph/flow-based analysis of liquidity in financial networks and sequential settlement.
Studies how cycles and network structure influence liquidity needs in financial networks.
Conceptually supports cycle-aware clearing, but the objective and algorithmic evaluation differ from the discrete BCP considered here.
Eboli et al. (2023) [7]
Numerical contagion analysis across interbank networks with varying density and centralization.
Finds a robustness–fragility trade-off: centralization and connectivity can improve resilience to some shocks while increasing vulnerability to others.
Motivates measuring topology and selecting hubs carefully; systemic-risk outcomes are not the same as maximizing feasible settled value.
Csóka & Herings (2023/2024) [8]
Mathematical characterization of clearing payment matrices under general bankruptcy/claims rules; uses strongly connected components.
Shows that clearing matrices form a lattice and provides conditions for uniqueness.
Clarifies the theoretical meaning of cycles and clearing outcomes, but studies payment-matrix existence/uniqueness rather than an indivisible-payment selection heuristic.
Nellen (2015) [9]
Game-theoretic analysis of collateralized intraday credit, two-part tariffs, and settlement coordination.
Compares implications of liquidity-facility design with stylized Swiss SIC and Fedwire settlement behavior.
Shows that available liquidity and incentives shape settlement; the current experiments instead hold deposits fixed (and synthetic for blockchain data) to compare selection algorithms.
Byck & Heijmans (2020) [10]
Simulation of bilateral offsetting, FIFO bypass, multilateral offsetting, and combined LSMs.
Uses 2018 Canadian LVTS transaction data; finds LSM benefits grow as available intraday liquidity tightens, with combined mechanisms often saving more liquidity.
Provides an operational simulation baseline for LSM design; the present work compares selected obligations and cleared face value under explicit per-node constraints.
Garratt (2022) [11]
Centralized nonurgent-payment netting queue with Shapley-value allocation of liquidity costs.
Uses take-it-or-leave-it offers to make welfare-improving netting proposals acceptable to liquidity providers.
Highlights fairness and incentives in LSM design; HSC/CA-HSC optimize feasible volume and do not model cost-sharing or participant acceptance.
Nellen (2019) [12]
Studies intraday liquidity facilities, fixed/variable liquidity costs, late-settlement fees, and coordination.
Finds that end-of-day liquidity availability and fee calibration affect incentives for early settlement and coordination.
Shows that operational timing and policy parameters matter; these dimensions are outside the static benchmark and should be addressed in future work.
Ketelaars & Borm (2024) [13]
Unifies centralized and decentralized clearing mechanisms in financial networks with assets, liabilities, and claims rules.
Provides a mathematical framework for how agent-specific claims rules determine mutual payments.
Relevant to clearing theory, but not an empirical runtime comparison of discrete payment-selection algorithms.
Banerjee, Bernstein & Feinstein (2025) [14]
Continuous-time extension of financial-network clearing with RTGS payment dynamics and default contagion.
Models dynamic interbank liabilities, cash and capital accounts, early defaults, and grace periods for overdue payments.
Adds temporal and default-risk realism beyond the present static graph model; it does not benchmark HSC/CA-HSC on large obligation lists.
Garratt et al. (2025) [15]
Auction-based liquidity-saving mechanism coordinating liquidity-sharing through participant bids.
BIS working paper; evaluates an incentive-based mechanism using agent-based simulations calibrated to RTGS systems.
Alternative LSM design emphasizing incentives and liquidity sharing rather than deterministic topology-based selection.
Mattern & Meyer (2025) [16]
Network and clustering approach to identify critical participants, incorporating payment type, frequency, value, and volume.
Uses Swiss SIC RTGS data; finds that critical participants include some mid-sized domestic banks and financial-market infrastructures, not only the largest banks.
Supports richer topology features than transaction value alone; its goal is systemic criticality analysis, not clearing-volume optimization.
Capponi & Chang (2025; revised 2026) [17]
Model of settlement speed incorporating netting benefits, liquidity costs, counterparty risk, and network topology.
Shows that faster settlement can reduce crisis probability yet increase crisis severity; optimal speed depends on topology and liquidity conditions.
Justifies evaluating both quality and latency. The present work measures algorithm runtime and cleared value, not equilibrium welfare or systemic-default outcomes.
Nguyen et al. (2023) [18]
Time-series analysis of connectedness among stablecoin price-stability measures.
Studies USDT, USDC, PAX, TUSD, and DAI over 2019–2021; reports heterogeneous stability and spillovers among coins.
Provides digital-asset context only. It does not analyze transfer-network clearing and is not evidence that token transfers are bank payment instructions.
Schär et al. (2026) [19]
Analyzes Ethereum stablecoin event logs and distinguishes simple transfer events from multi-step smart-contract transactions.
Uses hundreds of millions of event logs; finds that a large share of transfer events occur within complex transactions, so event-level counts can misstate economic activity.
Directly motivates the data caveat: ERC-20 transfer edges are observable events, not necessarily independent real-world payment obligations.
Lee & Tou (2026) [20]
Links stablecoin primary-market activity with wholesale interbank payment records to study bank liquidity exposure.
Finds that banks connected to stablecoin deposits face increased payment demand and liquidity exposure around primary-market activity.
Connects stablecoin activity to bank liquidity, but differs from our dataset: their analysis links bank records, whereas this study applies synthetic deposits to public transfer edges.
3.4. Research gap
The literature covers solver-based offsetting, dynamic clearing, LSM incentives, network contagion, payment-batch optimization, and stablecoin activity, but these works use different objectives, models, and data. The contribution here is therefore not a claim to be the first topology-aware or cycle-based clearing method. Instead, the paper evaluates HSC and CA-HSC under a common discrete-obligation feasibility model, compares them with both weak and strong baselines, and reports the quality–latency trade-off across synthetic networks, trust-network proxies, and Ethereum transfer windows. The evidence also limits the claim: HSC is not dominant against greedy plus local search, and CA-HSC takes 1.27 s on the 24-hour network, so it does not meet a strict one-second deadline in that run. The stablecoin deposits are synthetic, and the blockchain experiments are not validation on central-bank settlement instructions.
4. Problem Formulation
Let G = (V, A) be a directed graph with n = |V| participants and m = |A| obligations. Each arc (u, v) has positive face value w(u, v), and each participant i has deposit Dᵢ ≥ 0. Let xᵤᵥ ∈ {0, 1} indicate whether an obligation is settled. Define Outᵢ = Σᵥ w(i, v)xᵢᵥ, Inᵢ = Σᵤ w(u, i)xᵤᵢ, and Netᵢ = Outᵢ − Inᵢ. The clearing problem is
maximize Z = Σ₍ᵤ,ᵥ₎∈A w(u, v)xᵤᵥ
subject to Outᵢ − Inᵢ ≤ Dᵢ for all i ∈ V; xᵤᵥ ∈ {0, 1}.
An obligation is settled fully or deferred. Incoming payments reduce net debit, and reciprocal arcs are permitted. The continuous LP relaxation replaces binary restrictions with 0 ≤ xᵤᵥ ≤ 1 and provides an upper bound; it is not itself a feasible discrete clearing. A proven integer optimum is claimed only when the solver certifies optimality. The decision version of BCP is NP-complete [21].
For a selected set X ⊆ A, define Outᵢ(X) = Σⱼ:(i,j)∈X w(i,j), Inᵢ(X) = Σⱼ:(j,i)∈X w(j,i), and Netᵢ(X) = Outᵢ(X) − Inᵢ(X). Feasibility is equivalent to Netᵢ(X) ≤ Dᵢ for every participant i. The objective is the total face value Σ₍ᵤ,ᵥ₎∈A w(u,v)xᵤᵥ. This formulation permits incoming payments to finance outgoing obligations in the same clearing batch while preserving indivisibility.
4.1. Deposit construction
For Ethereum stablecoin experiments, deposits are synthetic: Dᵤ = max(1, α·Outflow(u)), with α = 0.20 as the principal stress setting and sensitivity tests over α ∈ {0.10, 0.20, 0.40, 0.60}. This α is a selected modeling parameter, not a measured regulatory liquidity ratio. For Bitcoin OTC/Alpha, positive trust ratings are converted into positive proxy weights and deposits are set to max(1, round(0.6 × total inflow)); these values are not monetary amounts. Stablecoin data are taken from the SNAP ERC-20 transfer collection [22], and the Bitcoin trust graphs from the SNAP signed-network datasets [23].
5. Proposed Algorithms
5.1. Hub–Spoke Clearing (HSC)
HSC selects the k highest-degree participants (in-degree plus out-degree) as hubs H; all other participants form the spoke set S. Connected components of the undirected spoke-induced graph are identified using union–find and treated as super-spokes. Each component is represented by a virtual node with pooled deposit and aggregated arcs to and from hubs. HSC then solves a 0/1 integer program on the hubs and virtual super-spokes, allocates selected aggregate spoke-to-hub flows to original members in descending weight order subject to each member’s actual deposit, greedily processes internal spoke obligations, and applies a worklist repair.
The hub set H contains the k participants with largest total degree deg(v) = indeg(v) + outdeg(v), and S = V\H denotes the spokes. Connected spoke components are aggregated into super-spokes with pooled liquidity. The exact binary optimization is then restricted to hub-to-hub obligations and the aggregated spoke representation. After the core is solved, the aggregate allocations are rationed back to original spoke obligations, followed by a feasibility repair on the original graph. This structure concentrates combinatorial search on participants with the greatest connectivity while retaining participant-level feasibility checks.
Figure 1. Hub–Spoke Clearing pipeline. Aggregation reduces the exact core problem, while rationing and repair restore feasibility at original participant level.
5.2. Feasibility analysis
Let W = {u : Netᵤ > Dᵤ} be the set of violating participants. Because Dᵤ ≥ 0 and all obligation weights are positive, any violating participant has at least one selected outgoing arc. Repair deletes the lightest selected outgoing arc of a violating participant and updates the net positions of both endpoints. Each iteration removes one selected arc and no arc is reinserted, so repair terminates after at most |X| ≤ m deletions. When no violation remains, the clearing is feasible. This proves termination and feasibility, but not an approximation ratio for the complete HSC algorithm.
The repair procedure maintains a worklist of violating participants. For a violating payer u, it removes a cleared outgoing obligation (u,v), reducing Outᵤ and therefore Netᵤ by the positive amount w(u,v). If the payee v becomes violating after losing that incoming offset, v must have at least one cleared outgoing obligation: otherwise Netᵥ = −Inᵥ ≤ 0 ≤ Dᵥ, a contradiction. Each repair step deletes one selected arc and no deleted arc is reintroduced. Hence the procedure terminates after at most |X| ≤ m deletions, and when the worklist is empty every participant satisfies Netᵢ ≤ Dᵢ. The repair is therefore finite and feasibility-restoring.
5.3. Cycle-Aware Hub–Spoke Clearing (CA-HSC)
CA-HSC retains degree-based ordering but removes the hub integer program. It executes four deterministic stages: (1) find reciprocal pairs and commit both arcs only if the combined net changes respect both participants’ deposits; (2) scan hub-incident arcs in descending weight order; (3) scan remaining spoke-to-spoke arcs; and (4) revisit rejected arcs in a bounded single 1-opt pass. A one-way arc u → v is committed only when Netᵤ + w(u, v) ≤ Dᵤ.
For reciprocal obligations u → v and v → u, the net changes are ΔNetᵤ = w(u, v) − w(v, u) and ΔNetᵥ = −ΔNetᵤ. Equal amounts consume no net deposit; unequal amounts consume deposit only for the differential at the net debtor. Thus, bilateral-cycle processing is not assumed to be universally deposit-neutral. Because each commitment is checked against the true payer deposit and incoming payments reduce net debit, every prefix remains feasible; no repair pass is required.
More explicitly, let a = w(u,v) and b = w(v,u). Clearing both obligations changes the two net positions by a−b and b−a. The common amount min(a,b) is offset bilaterally; only the unmatched amount |a−b| creates a net debit for one participant. CA-HSC checks that residual debit against the payer’s available deposit before committing the pair. If a = b, the pair is deposit-neutral. Because every later obligation is also checked against the current net position, every prefix of the CA-HSC commitment sequence is feasible.
5.4. Complexity and guarantees
The reported HSC runtime is O(n log n + m log m + f(k, p)), where p is the number of super-spoke components and the exact core term can grow exponentially with k and p. CA-HSC has O(m log m + n) time and O(m + n) space under the fixed-pass design. Neither complete algorithm has a demonstrated global approximation ratio for the netting formulation. The reported 1/2 bound applies only to the HSC spoke greedy step in a different gross-outflow model and is not claimed for the complete method.
The spoke-greedy subroutine has a 1/2 approximation guarantee only for the stated gross-outflow component model. This bound does not extend automatically to the full HSC algorithm under netting, and no global approximation ratio is claimed for complete HSC or CA-HSC. The complexity statement for CA-HSC follows from sorting obligations and degree-ordered passes: O(m log m + n) time and O(m+n) storage. HSC additionally incurs the exact hub-core term, whose worst-case growth is exponential in the selected core size.
6. Datasets and Experimental Protocol
The evaluation covers (i) synthetic Barabási–Albert scale-free graphs [24] and Erdős–Rényi graphs, (ii) Bitcoin OTC and Alpha positive trust-rating networks, and (iii) Ethereum ERC-20 stablecoin transfers for USDT, USDC, and DAI. Bitcoin graphs are topology proxies rather than payment records. Stablecoin transfer values are observed on-chain values, but the participant deposits are synthetic. Duplicate directed pairs are aggregated and zero-valued transfers excluded in the reported preprocessing.
Table 2. Network sizes used in the selected real-data evaluations.
Network / window
Participants / accounts
Obligations
Gross / proxy volume
Bitcoin OTC (positive ratings)
5,881
32,029
62,947 proxy units
Bitcoin Alpha (positive ratings)
3,783
22,650
45,202 proxy units
Stablecoin, 1 h
3,705
4,059
$219.3M
Stablecoin, 12 h
43,406
56,360
$6.38B
Stablecoin, 24 h
82,779
114,819
$16.78B
Experiments used Python 3.12.10 on Windows 11 with an AMD Ryzen 7 CPU (8 cores, 16 threads, 16 GB RAM), NetworkX 3.6.1, PuLP/CBC for initial synthetic tests, and HiGHS 1.15.1 for large stablecoin LP/MIP tests. Standard synthetic comparisons used 30 paired trials; the liquidity stress sweep used five trials per cell. Metrics include cleared volume, percentage of a proven integer optimum when available, percentage of the LP bound otherwise, elapsed time, and recomputed feasibility. Timings from different scripts are indicative and are not treated as paired measurements.
6.4. Reproducibility and interpretation of reported quantities
The synthetic network experiments, Bitcoin trust-network proxy experiments, and Ethereum stablecoin-transfer experiments answer different questions and should not be pooled into one headline score. Synthetic graphs allow comparison against a known optimum at selected sizes; Bitcoin OTC/Alpha graphs test behavior on non-payment network topologies; and ERC-20 transfer windows test the computational behavior of the method on large, skewed-value transaction graphs. The stablecoin experiments use a synthetic deposit rule Dᵤ = max(1, α·Outflow(u)), with α = 0.20 for the main CA-HSC comparison. Because α controls the available liquidity by construction, the resulting cleared amounts are conditional on this assumption. They are not estimates of actual bank liquidity savings.
For transparency, reported quantities are described according to their evidentiary status: “proven optimum” is reserved for a solver run that certified optimality; “LP bound” refers to the continuous relaxation; “incumbent” means a feasible solution found by a solver without a proof of optimality; and “cleared value” denotes the objective value of the feasible selected obligations under the specified model. Timing results are tied to their stated execution and are not treated as repeated-run averages unless repeated trials are explicitly reported.
7. Results
7.1. HSC on synthetic scale-free graphs
Across 30-trial scale-free tests, HSC improved on plain greedy at several sizes but not at every size. At n = 1,000, HSC reached 91.52% of the proven optimum versus 87.92% for greedy, a 3.60 percentage-point gain. At n = 30 and n = 50, HSC was slightly worse than greedy. These results support a conditional benefit, not universal dominance.
Table 3. HSC and plain greedy on scale-free graphs (30 trials; quality as % of proven optimum).
n
k
Greedy (%)
HSC (%)
Difference (pp)
10
2
88.47 ± 3.36
95.29 ± 1.59
+6.83
18
2
87.82 ± 2.57
91.51 ± 2.13
+3.70
30
2
88.06 ± 1.60
87.93 ± 2.88
−0.13
50
3
88.23 ± 1.03
86.99 ± 2.27
−1.24
100
6
87.73 ± 0.63
90.07 ± 1.37
+2.34
250
15
88.00 ± 0.53
90.29 ± 0.87
+2.29
500
30
87.80 ± 0.35
91.38 ± 0.55
+3.58
1,000
60
87.92 ± 0.26
91.52 ± 0.50
+3.60
Figure 2. Scale-free clearing quality and runtime ratio reported in the synthetic benchmark. HSC’s advantage over plain greedy is moderate and varies with graph size.
7.2. Topology ablation and stronger baselines
The hub-selection ablation isolates the role of topology. At n = 250 and k = 40 on scale-free graphs, degree-selected hubs achieved 93.03% of optimum compared with 88.37% for random hubs, a paired advantage of 4.66 percentage points (95% CI 4.00–5.32; Holm-adjusted p < 0.0001 [25]). At k = 15, the advantage was smaller (+1.47 points). On no-hub graphs at k = 15, degree selection offered essentially no advantage (+0.03 points; p = 0.94).
Table 4. Hub-selection ablation at n = 250 (mean ± SD, % of optimum).
Graph type
k
Degree
Random
Lowest degree
Scale-free
15
89.90 ± 1.89
88.43 ± 1.99
88.54 ± 1.16
Scale-free
40
93.03 ± 1.18
88.37 ± 1.40
87.94 ± 1.29
No hubs
15
89.09 ± 1.64
89.06 ± 1.78
89.31 ± 1.86
No hubs
40
90.77 ± 1.40
89.30 ± 1.76
89.20 ± 1.53
Figure 3. Hub-selection ablation on scale-free and hub-free graphs. Degree-based selection helps most when the graph has a clear hub structure.
Stronger baselines change the interpretation. At n = 1,000, greedy with local search achieved 99.03% of optimum in 26.0 ms; HSC with a 16% hub budget achieved 92.90% in 83.5 ms; and a time-matched exact run achieved 99.22% in 110.4 ms. A fixed 6%-of-n hub budget reached 91.21%, while the tested adaptive rule reached 87.84%. HSC’s gain over plain greedy therefore does not translate into an advantage over stronger local-search or exact baselines.
Table 5. Strong-baseline comparison on synthetic scale-free instances.
Method
n = 250 (% opt.)
Time (ms)
n = 1,000 (% opt.)
Time (ms)
Greedy
89.60 ± 1.35
2.5
89.30 ± 0.75
10.1
Greedy + local search
98.99 ± 0.45
7.3
99.03 ± 0.23
26.0
HSC, k = 6%
90.01 ± 2.10
15.8
90.85 ± 0.73
47.0
HSC, k = 16%
92.94 ± 1.24
26.7
92.90 ± 0.69
83.5
Exact, time-matched
99.73 ± 0.32
33.1
99.22 ± 0.21
110.4
Exact, to optimality
100
42.2
100
166.7
7.3. Bitcoin trust-network proxies
On the full Bitcoin trust graphs, HSC’s modest gain over plain greedy is outweighed by local search. On Bitcoin OTC, HSC reached 92.72% of the exact optimum in 4.692 s, while greedy with local search reached 98.40% in 0.132 s. On Bitcoin Alpha, HSC reached 92.98% in 2.355 s versus 98.30% for local search in 0.091 s. Across 256 weekly OTC snapshots, HSC cleared 49.38% of proxy-rating weight on average versus 47.69% for greedy (+1.69 points, p < 0.0001). These quantities are trust-rating proxies and must not be interpreted as dollars.
Table 6. Representative Bitcoin trust-network proxy results.
Network / subset
Exact
Greedy
HSC fixed
Greedy + LS
OTC full (% optimum)
100%
92.55%
92.72%
98.40%
Alpha full (% optimum)
100%
92.32%
92.98%
98.30%
OTC weekly (mean cleared proxy weight)
—
47.69%
49.38%
—
7.4. Stablecoin liquidity stress and LP integrality gaps
The earlier one-hour stablecoin sensitivity experiment used 3,713 accounts and 4,078 obligations. As deposits tighten, plain greedy degrades: at α = 0.10 it clears $16.47M, or 27.01% of the certified exact optimum, compared with $71.07M (78.80%) at α = 0.60. Across the tested α values, the continuous LP integrality gap ranges from 33.19% to 52.31%, and 30.53%–45.49% of LP variables are fractional. These values show why the continuous relaxation is a useful upper bound but not a substitute for a discrete feasible clearing.
Table 7. One-hour stablecoin sensitivity and LP relaxation diagnostics (earlier preprocessing run).
α
Exact ($M)
Greedy ($M)
Greedy / exact
LP upper ($M)
LP gap
Fractional vars
0.10
60.98
16.47
27.01%
91.29
33.19%
45.49%
0.20
71.54
26.99
37.73%
118.65
39.70%
42.45%
0.40
82.16
53.68
65.33%
163.01
49.60%
38.60%
0.60
90.18
71.07
78.80%
189.13
52.31%
30.53%
For larger earlier windows at α = 0.20, HiGHS proved $200.14M on 7,906 obligations in 1.777 s and $370.14M on 16,093 obligations in 5.404 s. HSC hub-ILP runs on those instances took approximately 60–66 s and generally cleared less than stronger baselines. Thus, the favorable large-network results below are attributable to CA-HSC, not to the exact-core HSC formulation.
7.5. CA-HSC on large stablecoin windows
The later CA-HSC pipeline used 4,059 obligations in the one-hour window, 56,360 in the 12-hour window, and 114,819 in the 24-hour window, with α = 0.20. On the 12-hour network, CA-HSC cleared $3.04B in 0.52 s (61.9% of the $4.91B LP bound), compared with $1.23B for greedy and $1.59B for greedy plus local search. On the 24-hour network, CA-HSC cleared $8.203B in 1.27 s (57.8% of the $14.203B LP bound), compared with $3.820B for greedy and $4.956B for greedy plus local search. CA-HSC therefore improved on plain greedy by $4.384B (114.8%) in the 24-hour comparison, but did not meet a strict one-second deadline.
Table 8. CA-HSC and baseline performance on the later stablecoin pipeline (α = 0.20).
Window
Method
Cleared
% LP bound
Payments
Time (s)
Status
24 h
HiGHS MIP
$0.00
0.0%
0
1.90
No incumbent
24 h
Greedy
$3.820B
26.9%
37,777
0.25
Feasible
24 h
Greedy + LS
$4.956B
34.9%
46,216
0.38
Feasible
24 h
CA-HSC
$8.203B
57.8%
46,593
1.27
Feasible
12 h
HiGHS MIP
$0.00
0.0%
0
1.34
No incumbent
12 h
Greedy
$1.23B
25.1%
17,730
0.09
Feasible
12 h
Greedy + LS
$1.59B
32.4%
21,314
0.17
Feasible
12 h
CA-HSC
$3.04B
61.9%
21,230
0.52
Feasible
1 h
HiGHS MIP
$71.5M
60.3%
1,999
1.02
Partial
1 h
Greedy
$30.0M
25.3%
1,585
≈0.00
Feasible
1 h
CA-HSC
$62.6M
52.7%
1,678
0.03
Feasible
Figure 4. Cleared volume on the 24-hour stablecoin window. CA-HSC exceeds both greedy baselines but remains below the offline optimum.
The one-hour CA-HSC run cleared $62.6M in 0.03 s, while the reported 1.02 s HiGHS result was a partial incumbent of $71.5M. An earlier run with different preprocessing certified $71.54M in 0.788 s; these executions are not merged because they do not use identical inputs or budgets. Cold-start MIP runs on the 12- and 24-hour windows returned no feasible incumbent within their short nominal budgets. A zero incumbent indicates solver failure to find a feasible solution within the run, not absence of a feasible clearing.
7.6. CA-HSC stage contribution and progressive settlement
The bilateral-cycle stage is the largest contributor in each reported window, accounting for 56.7%–67.8% of final volume. In the stage-benchmark 24-hour execution, 2,614 reciprocal pairs contributed $4.64B; hub-directed processing added $2.41B, spoke clusters $150.3M, and 1-opt refinement $983.2M. This stage table belongs to a separate execution that cleared $8.18B in 1.30 s; it is not arithmetically combined with the head-to-head result of $8.203B in 1.27 s.
Table 9. CA-HSC stage contributions (separate stage-benchmark execution).
Stage
1 hour
12 hours
24 hours
Bilateral 2-cycles
$42.4M (67.8%)
$1.96B (64.5%)
$4.64B (56.7%)
Hub-directed
$17.8M (28.5%)
$685.6M (22.6%)
$2.41B (29.5%)
Spoke clusters
$1.8M (2.9%)
$48.2M (1.6%)
$150.3M (1.8%)
1-opt refinement
$0.451M (0.7%)
$344.4M (11.3%)
$983.2M (12.0%)
Total / runtime
$62.6M / 0.03 s
$3.04B / 0.52 s
$8.18B / 1.30 s
A separate progressive-settlement demonstration logged $1.99B at 299 ms, $4.64B at 558 ms, $7.29B at 741 ms, and $8.20B at 860 ms. These are internal milestones from a different script, not end-to-end runtimes and not substitutes for Table 7.
7.7. Offline quality–latency trade-off
Offline optimization improves solution quality when given more time. A separate 24-hour run proved an integer optimum of $11.96B in 322.56 s. Relative to that optimum, CA-HSC reached 68.6%, while Cycle-GLS reached $8.84B (74.0%) in 1.89 s. The cold HiGHS run did not obtain an incumbent in approximately 74 s; a warm-started run seeded by Cycle-GLS retained its $8.84B solution but did not prove optimality within its limit. The 12-hour integer optimum was not proven, so only percentages of the LP bound are reported for that window.
Table 10. Selected offline comparisons; LP-bound percentages are used unless a proven integer optimum is explicitly stated.
Window
Method
Cleared
% LP bound
Time (s)
Outcome
12 h
CA-HSC
$3.04B
61.9%
0.52
Feasible
12 h
Cycle-GLS
$3.13B
63.9%
0.60
Feasible
12 h
HiGHS cold
$3.77B
76.8%
300.09
Timed out; optimum unproven
24 h
CA-HSC
$8.20B
57.8%
1.27
68.6% of proven optimum
24 h
Cycle-GLS
$8.84B
62.3%
1.89
74.0% of proven optimum
24 h
HiGHS cold
$11.96B
84.2%
322.56
Proven optimum
Figure 5. Offline volume/runtime comparison for 12-hour and 24-hour windows. The 1-second line separates short-latency heuristics from longer offline runs.
7.5. Practical Interpretation and Potential Operational Value
The results suggest a useful design principle for liquidity-saving systems: a clearing engine need not wait for a single global optimization to finish before returning a feasible set of payments. CA-HSC commits obligations only after checking the resulting participant-level net debit, allowing it to produce an internally feasible partial clearing quickly. In an operational architecture, such a result could serve as an early candidate batch while a more expensive optimizer continues to search for improvements. This is a proposed deployment pattern, not a production-system result established by the experiments in this paper.
7.5.1. Why bilateral cycles matter
Bilateral reciprocal obligations are attractive because the matched portion offsets between the two participants. For obligations of values a and b in opposite directions, the common amount min(a,b) can be settled without creating an unmatched debit; only the difference |a−b| affects the pair’s net position. The stage experiment found that bilateral cycles contributed 56.7% of the final cleared volume in the reported 24-hour execution, and bilateral cycles contributed between 56.7% and 67.8% across the reported windows. These are measured shares from the specified runs, not a guarantee that the same proportions will hold in another payment system. The result nevertheless motivates checking reciprocal obligations early, particularly when the system is under a tight processing budget.
For a payment operator, the practical implication is not that all reciprocal transfers should automatically be prioritized. The operator would still need to respect payment priority, irrevocability rules, cut-off times, legal settlement finality, and participant-level liquidity. Rather, cycle-aware processing provides a candidate ordering that can be combined with the operator’s policy constraints. The feasibility checks in CA-HSC are necessary for liquidity consistency under the paper’s model, but they do not implement every operational rule used in a live RTGS service.
7.5.2. A two-speed clearing architecture
A possible operational architecture separates immediate feasibility from continued optimization. In the first stage, a fast heuristic produces a feasible partial batch. In the second stage, a solver or local-search process attempts to improve the remaining unsettled obligations within the available time. If a new solution is accepted, the system would need a clearly specified commit boundary so that an already released payment is not silently withdrawn. The experiments support the computational motivation for this architecture: CA-HSC produced $3.04 billion of cleared value in 0.52 seconds on the 12-hour stablecoin-transfer window, while the 24-hour run produced $8.203 billion in 1.27 seconds. The latter is useful as a throughput-quality observation but exceeds a strict one-second deadline, so it should not be described as meeting that deadline.
The exact and heuristic results serve different purposes. On the 24-hour stablecoin window, the offline optimum was proven at $11.96 billion after 322.56 seconds, while CA-HSC cleared $8.203 billion in the reported run. The offline optimum therefore provides a quality reference, whereas the heuristic provides a much faster feasible result. This comparison illustrates a quality–latency trade-off; it does not show that CA-HSC is optimal or that the same runtime ratio will hold under other hardware, network loads, or settlement rules. The 12-hour instance has no proven optimum in the reported experiments, so its quality should be discussed against the LP bound and baselines rather than assigned an unverified optimality gap.
7.5.3. How a payment institution could use the findings
The findings are most directly relevant to research and engineering teams designing liquidity-saving batch logic, simulation environments, or decision-support tools. A clearing operator could use the approach to explore whether topology-aware candidate selection improves a baseline under its own obligation graph and liquidity distribution. The algorithm can also help prioritize which obligations to evaluate first, while retaining a feasibility check at each commitment. Before any operational use, however, the institution would need to replay historical payment instructions, apply actual participant liquidity and payment priorities, model settlement finality and cancellation rules, test adversarial and peak-load scenarios, and conduct independent performance and correctness validation.
For treasury and liquidity-management teams, the measured stage contributions can help formulate testable questions: how much volume is available through reciprocal obligations; how sensitive is the cleared amount to the hub budget; and when does the marginal value of additional optimization time justify the computational cost? The current paper provides benchmark observations that can inform those questions, but it does not establish a monetary saving for a bank, a reduction in real reserve requirements, or a reduction in systemic risk. Such claims would require real institutional payment data, actual liquidity positions, and an evaluation design that measures those outcomes directly.
7.5.4. Interpreting the datasets responsibly
The synthetic scale-free experiments isolate how graph structure can affect the heuristic. At n = 1,000, HSC cleared 91.52% of the exact optimum compared with 87.92% for plain greedy, a 3.60 percentage-point improvement. At smaller sizes n = 30 and n = 50, the same advantage was not observed. Against stronger baselines, greedy plus local search reached 99.03% of optimum in 26.0 ms, while HSC at k = 16% reached 92.90% in 83.5 ms; a time-matched exact run reached 99.22% in 110.4 ms. The positive result is therefore specific: topology-aware decomposition can improve on a simple greedy baseline in some larger synthetic graphs, but it is not uniformly superior to stronger optimization methods.
The Bitcoin OTC and Alpha datasets are signed trust networks, not payment ledgers. Their use in this paper is restricted to topology-proxy experiments; their edge weights should not be interpreted as cleared monetary value. Likewise, the Ethereum ERC-20 dataset contains token-transfer events, while the deposits used by the algorithm are synthetic values derived from outflow using the chosen parameter α. These datasets enable reproducible structural and computational tests, but they do not substitute for confidential interbank settlement records. Keeping these distinctions explicit makes the positive findings more useful: they identify hypotheses and algorithmic behavior worth testing on operational data without overstating what the present benchmarks demonstrate.
8. Discussion and Limitations
The results identify two regimes. Exact optimization is appropriate for smaller batches or latency-tolerant workloads and can ultimately outperform heuristics. CA-HSC is more suitable when a feasible partial clearing is required quickly: it commits obligations incrementally and preserves feasibility at each step. HSC’s gains over plain greedy on synthetic scale-free graphs are conditional on topology and hub budget, and they disappear against stronger local-search or time-matched exact baselines.
A practical evaluation should report at least four dimensions together: (i) cleared face value, (ii) feasibility under the stated liquidity model, (iii) wall-clock latency and whether the time limit is met, and (iv) the reference quality level, distinguishing a proven optimum from an LP relaxation or a feasible incumbent. This paper reports these quantities where available and labels the status of the relevant solver run. In particular, an LP relaxation is an upper bound and may contain fractional obligations; it is not itself a feasible settlement plan. Similarly, a solver that returns no incumbent within a short time limit has not demonstrated infeasibility—it has only failed to provide a feasible incumbent within that run’s budget.
The results also indicate why baseline selection matters. A comparison only against plain greedy would overstate the practical strength of HSC because local search and exact optimization can recover substantially more value on the reported synthetic and stablecoin cases. Conversely, comparing a fast heuristic only against an offline optimum would obscure the latency cost of obtaining that optimum. A fair operational comparison therefore needs a common time budget, identical input graph and liquidity constraints, and a consistent definition of cleared value. The large-window results in this paper include executions from distinct scripts, so their values are reported separately rather than combined as if they were a single paired benchmark.
Several limitations constrain interpretation. First, Ethereum events are token transfers between accounts and contracts, not institutional interbank obligations. Second, deposits are synthetically assigned from outflow and do not represent central-bank reserve balances or observed liquidity. Third, the largest CA-HSC result takes 1.27–1.30 s and therefore exceeds a strict one-second end-to-end deadline. Fourth, large stablecoin configurations were run once (the 24-hour benchmark was repeated in a separate stage script) on one machine; no confidence intervals are available for these large-instance timing and volume claims. Fifth, timing values from separate scripts are indicative, not controlled paired comparisons. Finally, neither full HSC nor full CA-HSC has a proven global approximation ratio for the netting problem.
Future work should evaluate both methods on actual settlement instructions with real liquidity positions, priorities, and operational constraints; replicate latency measurements across machines and runs; and test hybrid architectures in which CA-HSC supplies an immediate feasible clearing while exact optimization improves the residual batch in the background.
9. Conclusion
This study compares a topology-aware exact-core decomposition with a cycle-aware polynomial-time heuristic. HSC reaches 91.52% of the exact optimum at n = 1,000 in the reported scale-free benchmark, but stronger local search and time-matched exact solving perform better. CA-HSC clears $3.04B in 0.52 s on the 12-hour stablecoin window and $8.203B in 1.27 s on the 24-hour window, where plain greedy clears $3.820B. Bilateral cycles account for 56.7%–67.8% of volume in the separate stage tests. A proven offline optimum of $11.96B shows that CA-HSC sacrifices solution quality for latency. The evidence supports CA-HSC as a promising feasibility-preserving heuristic under synthetic liquidity stress, not as validated production RTGS performance.
References
[1] J. Cambe and Z. Xing, “Just solve it: A simple method to improve the design and performance of liquidity-saving mechanisms,” Journal of Financial Market Infrastructures, vol. 11, no. 2, pp. 27–49, 2024. https://www.risk.net/journal-of-financial-market-infrastructures/7959350/just-solve-it-a-simple-method-to-improve-the-design-and-performance-of-liquidity-saving-mechanisms.
[2] S. Chen, O. Baron, and N. Chen, “Optimal dynamic clearing for interbank payments,” Management Science, vol. 71, no. 4, pp. 2953–2974, 2025 (published online 2024). https://doi.org/10.1287/mnsc.2023.00380.
[3] H. Hayakawa, “How a liquidity saving mechanism affects bank behavior in interconnected payment networks,” Journal of Economic Interaction and Coordination, vol. 20, pp. 41–71, 2025 (published online 2024). https://doi.org/10.1007/s11403-024-00408-0.
[4] V. Astuti, A. Baldeschi, L. Bastianelli, G. Bruno, A. Desai, D. Marsden, and R. Russo, “Liquidity optimization in gross settlement systems with quantum reordering: Application to TARGET2,” Journal of Economic Dynamics and Control, vol. 190, art. 105385, 2026. https://doi.org/10.1016/j.jedc.2026.105385.
[5] A.-C. Hüser, “Too interconnected to fail: A survey of the interbank networks literature,” SAFE Working Paper No. 91, 2015. https://www.risk.net/journal-of-network-theory-in-finance/2425987/too-interconnected-to-fail-a-survey-of-the-interbank-networks-literature.
[6] H. Hayakawa, “Liquidity in financial networks,” Computational Economics, vol. 55, pp. 253–301, 2020. https://doi.org/10.1007/s10614-019-09895-x.
[7] M. Eboli, B. Ozel, A. Teglio, and A. Toto, “Connectivity, centralisation and ‘robustness-yet-fragility’ of interbank networks,” Annals of Finance, vol. 19, pp. 169–200, 2023. https://doi.org/10.1007/s10436-022-00416-9.
[8] P. Csóka and P. J.-J. Herings, “Uniqueness of clearing payment matrices in financial networks,” Mathematics of Operations Research, vol. 49, no. 1, pp. 232–250, 2024 (published online 2023). https://doi.org/10.1287/moor.2023.1354.
[9] T. Nellen, “Collateralised liquidity, two-part tariff and settlement coordination,” Swiss National Bank Working Paper No. 2015-13, 2015. https://www.snb.ch/en/publications/research/working-papers/2015/working_paper_2015_13.
[10] S. Byck and R. Heijmans, “How much liquidity would a liquidity-saving mechanism save if a liquidity-saving mechanism could save liquidity? A simulation approach for Canada’s large-value payment system,” De Nederlandsche Bank Working Paper No. 682, 2020. https://www.dnb.nl/en/publications/research-publications/working-paper-2020/how-much-liquidity-would-a-liquidity-saving-mechanism-save-if-a-liquidity-saving-mechanism-could-save-liquidity-a-simulation-approach-for-canada-s-large-value-payment-system-shaun-byck/.
[11] R. J. Garratt, “An application of Shapley value cost allocation to liquidity savings mechanisms,” Journal of Money, Credit and Banking, vol. 54, no. 6, pp. 1875–1888, 2022. https://doi.org/10.1111/jmcb.12853.
[12] T. Nellen, “Intraday liquidity facilities, late settlement fee and coordination,” Journal of Banking & Finance, vol. 106, pp. 124–131, 2019. https://doi.org/10.1016/j.jbankfin.2019.06.009.
[13] M. W. Ketelaars and P. Borm, “On the unification of centralized and decentralized clearing mechanisms in financial networks,” Mathematical Methods of Operations Research, vol. 99, pp. 205–231, 2024. https://doi.org/10.1007/s00186-024-00860-5.
[14] T. Banerjee, A. Bernstein, and Z. Feinstein, “Dynamic clearing and contagion in financial networks,” European Journal of Operational Research, vol. 321, no. 2, pp. 664–675, 2025. https://doi.org/10.1016/j.ejor.2024.09.046.
[15] R. J. Garratt, M. L. Bech, M. Nanut Petrič, and C. Ates, “Auction-based liquidity saving mechanisms,” BIS Working Paper No. 1318, Bank for International Settlements, 2025. https://www.bis.org/publications/working-paper-1318-auction-based-liquidity-saving-mechanisms.
[16] J. Mattern and C. Meyer, “Beyond interbank: Identifying critical participants in integrated RTGS systems using payment type and temporal dynamics,” Swiss National Bank Working Paper No. 2025-14, 2025. https://www.snb.ch/en/publications/research/working-papers/2025/working_paper_2025_14.
[17] A. Capponi and J.-W. Chang, “Settlement speed and financial stability,” Federal Reserve Finance and Economics Discussion Series, No. 2025-101, revised June 2026. https://doi.org/10.17016/FEDS.2025.101r1.
[18] B. Nguyen Thanh, T. Nguyen Vu Hong, H. Pham, T. Nguyen Cong, and T. Pham Thi Anh, “Are the stabilities of stablecoins connected?,” Journal of Industrial and Business Economics, vol. 50, pp. 515–525, 2023. https://doi.org/10.1007/s40812-022-00207-3.
[19] F. Schär, A. Kosse, T. Rice, T. Shirakami, and J. Siridhasanakul, “The anatomy of stablecoin transactions,” BIS Working Paper No. 1359, 2026. https://www.bis.org/publications/working-paper-1359-anatomy-stablecoin-transactions.
[20] M. J. Lee and D. Tou, “Stablecoin disintermediation,” Federal Reserve Bank of New York Staff Report No. 1185, 2026. https://doi.org/10.59576/sr.1185.
[21] M. M. Güntzer, D. Jungnickel, and M. Leclerc, “Efficient algorithms for the clearing of interbank payments,” European Journal of Operational Research, vol. 106, no. 1, pp. 212–219, 1998. https://www.sciencedirect.com/science/article/pii/S0377221797002658
[22] Stanford Network Analysis Project (SNAP), “Ethereum ERC-20 stablecoin token transfers (USDT, USDC, DAI).” https://snap.stanford.edu/data/ERC20-stablecoins.html (accessed November 10, 2026).
[23] S. Kumar, F. Spezzano, V. S. Subrahmanian, and C. Faloutsos, “Edge weight prediction in weighted signed networks,” in Proceedings of the IEEE International Conference on Data Mining, 2016, pp. 221–230. Bitcoin OTC/Alpha datasets: https://snap.stanford.edu/data/soc-sign-bitcoinotc.html and https://snap.stanford.edu/data/soc-sign-bitcoinalpha.html.
[24] A.-L. Barabási and R. Albert, “Emergence of scaling in random networks,” Science, vol. 286, no. 5439, pp. 509–512, 1999. https://doi.org/10.1126/science.286.5439.509
[25] S. Holm, “A simple sequentially rejective multiple test procedure,” Scandinavian Journal of Statistics, vol. 6, no. 2, pp. 65–70, 1979. https://doi.org/10.2307/4615733