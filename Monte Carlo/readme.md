# Probabilistic Monte Carlo Steel Decarbonization Model
This module performs a probabilistic Monte Carlo assessment of steel-sector
decarbonization pathways using the steel optimization model. The Monte Carlo driver (`mc_run.py`) generates independent, seeded discrete
samples for each run, substitutes them into the AMPL model, solves the
optimization problem with Gurobi, and collects one machine-readable output row
per simulation.

## Monte Carlo sampling

Each simulation samples the following parameters independently:

| Parameter | Sample space |
|---|---|
| H₂ start year | 2030, 2035, 2040, 2045 |
| Technology learning (`theta_tech`) | 0, 0.1, ..., 1.0 |
| Grid + CCS learning (`theta_grid = theta_ccs`) | 0, 0.1, ..., 1.0 |
| Scrap growth rate | 2.0%, 2.5%, ..., 8.0%/yr |
| Natural-gas price | $5, $6, ..., $25/MMBtu |
| Coking-coal availability | Low, Mid, High |
| Natural-gas availability | BAU, Shock, Policy |

The four H₂ start years define four Monte Carlo clouds. Sampling within each
cloud is discrete-uniform and independently seeded for reproducibility.

## Fixed assumptions

The following parameters are held at the central case for all simulations:

- Average emissions constraint: **1.8 tCO₂/tCS**
- Capacity expansion: **Medium ramp**
  - Common capacity addition: 15 Mt/yr
  - H₂ reference capacity: 6 Mt
- Emission monotonicity constraint: **active**
- Optimization objective: discounted total system cost
- Solver: **Gurobi**
- MIP gap: **0.2%**
- Time horizon: **2025–2050**

## Model structure

The model is assembled from modular AMPL files covering:

- Coke, sinter and pellet production
- BF–BOF steelmaking
- Coal-, natural-gas- and H₂-DRI
- EAF steelmaking
- Scrap flows
- Carbon capture and storage (CCS)
- Waste-heat recovery
- Power balance
- Capacity expansion
- Cost and emissions accounting
- Additional system constraints

Scenario-specific coking-coal and natural-gas availability files are included
for each Monte Carlo realization.

## Reproducibility
All stochastic sampling is performed by `mc_run.py` using explicit seeds.
The AMPL model itself is deterministic; uncertainty is introduced entirely
through the sampled scenario and parameter inputs.
