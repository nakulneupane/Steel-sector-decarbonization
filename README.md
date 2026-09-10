# Steel Decarbonization Model

AMPL–Python framework for analyzing decarbonization pathways in the **Indian steel sector, 2025–2050**. The repository contains the core optimization model and computational pipelines used to generate the study results.

Current studies include **H2 Delay, Fuel Availability, Feasibility Drivers, Sectoral Synergy, Monte Carlo, Violin, and Adaptive Planning (Regret)**.

## Requirements

* AMPL with a licensed Gurobi installation, both available on `PATH`
* Python 3

```bash
pip install amplpy pandas openpyxl numpy matplotlib
```

## Repository Structure

```text
Steel-sector-decarbonization/
│
├── core/                              # Core AMPL model
│
├── structural/                       # Deterministic studies
│   ├── axes/
│   ├── report.mod
│   ├── solve_common.py
│   ├── h2_delay/
│   ├── fuel_availability/
│   └── feasibility_and_synergy/
│       ├── feasibility_drivers/
│       └── sectoral_synergy/
│
├── monte_carlo/                       # Uncertainty studies
│   ├── template_montecarlo.mod
│   ├── run_montecarlo.py
│   ├── data/
│   ├── uncertainty/
│   │   ├── shares/
│   │   ├── cost_risk/
│   │   ├── cost_distribution/
│   │   ├── coking_coal_stochasticity/
│   │   └── plot_uncertainty.py
│   └── violin/
│
└── adaptive_planning/                 # Adaptive planning and regret analysis
    ├── run_regret.py
    ├── plot_regret.py
    └── data/
```

## Running the Studies

Each study can be run from its own directory.

### H2 Delay

```bash
cd structural/h2_delay
python run_h2delay.py
python plot_h2delay.py
```

### Fuel Availability

```bash
cd structural/fuel_availability
python run_fuelavailability.py
python plot_fuelavailability.py
```

### Feasibility Drivers & Sectoral Synergy

```bash
cd structural/feasibility_and_synergy

python feasibility_drivers/run_feasibilitydrivers.py
python sectoral_synergy/run_sectoralsynergy.py
python plot_feasibility_and_synergy.py
```

### Monte Carlo

The Monte Carlo solve must be completed before running the downstream uncertainty and violin analyses.

```bash
cd monte_carlo
python run_montecarlo.py -j 6
```

Then:

```bash
cd uncertainty

python shares/run_shares.py
python cost_risk/run_costrisk.py
python coking_coal_stochasticity/run_cokingcoal.py
python cost_distribution/run_costdistribution.py
python plot_uncertainty.py

cd ../violin
python run_violin.py
python plot_violin.py
```

### Adaptive Planning (Regret)

The regret analysis studies the cost of committing to an H2-investment program before the true hydrogen arrival year is known, relative to perfect foresight.

Regret uses **1,000 sampled worlds** (50 worlds/year × 20 arrival years, 2030–2049). Each world is solved **10 ways**: once under **perfect foresight** (the baseline), once with **no recourse** (committed to the initial plan for the full horizon), and once at each of four **review checkpoints** (2030, 2035, 2040, and 2045). Each checkpoint contributes both a **re-planning solve** under the updated belief and a **settle solve** under the realized outcome.

* `run_regret.py` → `data/regret_ladder.csv`
* `plot_regret.py` → `fig_regret.png/pdf`


## Parallel Execution

The computationally intensive pipelines support parallel workers through `-j`:

```bash
python run_feasibilitydrivers.py -j 6
python run_sectoralsynergy.py -j 6
python run_montecarlo.py -j 6
python run_regret.py -j 6
```

The default is 6 workers. A value close to the number of available physical CPU cores is recommended.

The feasibility analysis can be resumed after interruption:

```bash
python run_feasibilitydrivers.py -j 6 --resume
```

## Reproducibility

The `structural/` studies are deterministic and should reproduce the same results across runs, apart from negligible solver and floating-point differences.

The Monte Carlo pipeline uses a fixed random seed (`20260824`) and draw sequence. The same uncertainty realizations are therefore generated on every run. Solver execution order may vary across machines, so intermediate files may not be byte-identical, but results for the same structural pathway and draw are reproducible.

The `adaptive_planning/` regret analysis uses independently seeded random number generators for each hydrogen arrival year, with the seed defined as `BASE_SEED + year`. This makes the same 1,000 worlds reproducible regardless of parallel solve order. 
