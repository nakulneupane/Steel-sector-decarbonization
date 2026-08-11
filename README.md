# Model Framework

## Technology Learning

Future technology development is represented using three independent learning parameters, each ranging from **0** (slow progress) to **1** (fast progress). All technologies are calibrated to fixed 2025 values, while only the future (2050) performance changes.

- **`theta_tech`** controls global learning in green hydrogen technologies, including electrolyser and dedicated renewable costs.
- **`theta_grid`** controls the evolution of the Indian power system, affecting grid electricity prices, grid emission factors, electric steelmaking, waste heat recovery, and CCS operating costs.
- **`theta_ccs`** controls improvements in carbon capture technology by reducing CCS capital costs. The total capture cost is calculated from capital, electricity, steam, solvent, and transport & storage costs.

The three learning parameters are independent and can be combined to represent different future scenarios.

---

## Steel Demand

Future steel demand is exogenously specified using an annual growth rate. The optimizer must satisfy demand in every year by selecting the least-cost combination of production routes.

---

## Capacity Expansion

The model explicitly tracks installed capacity for every steelmaking route. Building new capacity requires capital investment, incurs fixed operating costs, and remains available throughout its lifetime.

Capacity expansion is represented using two different mechanisms:

- **Conventional technologies** (BF-BOF, Coal DRI, NG-DRI, and Scrap-EAF) share a common annual capacity addition limit (`cap_add_common`), representing realistic construction and industrial deployment constraints.

- **Hydrogen technologies** are constrained separately through an electrolyser deployment model that captures manufacturing and supply-chain limitations. By default, hydrogen deployment follows a **Gaussian transition**, representing slow initial deployment, rapid scale-up, and gradual stabilization.

Note: Alternative linear and unconstrained deployment modes are also available for sensitivity analysis.

---

## Capacity Utilization

Each production route operates within minimum and maximum utilization limits.

Minimum utilization represents the economic requirement for plants to operate above break-even levels, while maximum utilization accounts for maintenance shutdowns and operational limitations.

---

## Green Hydrogen Supply

Rather than prescribing a fixed hydrogen price, the model explicitly represents the complete green hydrogen supply chain.

This includes:

- Electrolyser capacity
- Dedicated renewable generation
- Hydrogen firming and storage
- Operating costs

Dedicated renewable electricity supplies hydrogen production independently of the grid, allowing hydrogen costs to evolve separately from electricity prices. Hydrogen investments are treated as physical assets that can later become underutilized or stranded.

---

## Carbon Capture and Storage (CCS)

CCS is modeled using a component-based cost framework rather than a fixed cost per tonne of CO₂ captured.

The total capture cost is calculated from:

- Capture plant capital cost
- Fixed operating cost
- Electricity for CO₂ compression
- Steam for solvent regeneration
- Solvent consumption
- Transport and storage

The model also accounts for differences in CO₂ concentration between process streams. CO₂-rich streams require less energy to capture than dilute flue gases, allowing each steelmaking route to have different CCS costs and energy requirements.

---

## Waste Heat Recovery

Waste heat generated throughout the steelmaking process can be recovered and used either to generate electricity or to supply regeneration steam for CCS. The model optimizes this allocation based on system economics.

---

## Scrap Blending

Scrap can be utilized in three ways:

- Blended into BF-BOF.
- Blended into DRI-EAF routes.
- Used directly in dedicated Scrap-EAF production.

Each route has minimum and maximum allowable scrap fractions, and annual changes in blending are limited to represent gradual operational changes.

---

## Supply Chain Expansion

The model can also invest in supporting infrastructure, including scrap processing facilities, hydrogen production assets, and optional fossil fuel supply networks, allowing supply-chain expansion costs to be included in transition planning.

---

## Sunk Capital

The model supports two investment formulations:

- **`sunk = 1` (default):** Investments are irreversible. Capital costs are incurred when capacity is built, even if the asset is later underutilized or stranded.
- **`sunk = 0`:** Capital and fixed operating costs are charged only on production. Capacity can be built and abandoned without financial penalty. This counterfactual setting isolates the effect of irreversible investments.
