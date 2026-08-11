# Abatement Anatomy

## Purpose

The **Abatement Anatomy** study identifies the main sources of emissions reduction in the steel-sector decarbonization pathway.

Rather than evaluating only the total emissions reduction, the study decomposes the reduction into contributions from major structural and technological changes:

* Hydrogen-based DRI
* CCS
* Increased scrap availability and utilization
* Natural-gas-based DRI
* Grid decarbonization
* Other/residual effects

The analysis uses the same underlying steel-sector optimization model and assumptions as the main model. Only the additional baseline and scenario definitions specific to this study are introduced here.

## Common Baseline

A single **common frozen-structure baseline** is used as the reference for all scenarios.

The baseline represents a continuation of the calibrated 2025 production structure without the major endogenous decarbonization transitions. Specifically:

* Hydrogen deployment is disabled.
* CCS is disabled.
* The emissions constraint is made non-binding.
* 2025 production-route shares are frozen through the study period.
* The aggregate scrap share is held at its calibrated 2025 level.

Using one common baseline ensures that all policy scenarios are compared against the same reference system. This is particularly important for the scrap sensitivity, where constructing a separate baseline for each scrap-availability assumption would change the reference itself.

## Policy Scenarios

Starting from the common central configuration, individual structural parameters are perturbed to examine their effect on the abatement pathway.

| Scenario | Perturbation                                        |
| -------- | --------------------------------------------------- |
| EF1.6    | Emissions target tightened from 1.8 to 1.6 tCO₂/tCS |
| EF1.8    | Central emissions target of 1.8 tCO₂/tCS            |
| S4       | Scrap availability growth reduced to 4%/yr          |
| S8       | Scrap availability growth increased to 8%/yr        |
| RL       | Lower deployment ramp: 10 Mt/yr, H₂ 4 Mt/yr         |
| RH       | Higher deployment ramp: 20 Mt/yr, H₂ 8 Mt/yr        |

All other model assumptions remain fixed at the central configuration.

## Abatement Accounting

Each policy scenario is compared with the **same common baseline**. Annual emissions differences are aggregated over 2025–2050 and separated into the major abatement wedges.

The decomposition is an accounting exercise applied to the optimized model outputs; the individual wedges are not separately optimized.

Route-level gross emissions are calculated to maintain consistent attribution of process and electricity-related emissions. Any component that cannot be uniquely assigned to the identified mechanisms is retained as **Other** rather than being forced into a specific wedge.

## Computational Structure

The study consists of:

* `abatement_baseline.mod` — common frozen-structure reference;
* `abatement_scenario.mod` — parameterized policy scenario;
* `abatement.bat` — runs the baseline and scenario sweep; and
* post-processing scripts that aggregate the annual model outputs for the abatement decomposition.

The abatement study is therefore a **controlled structural analysis built on the main steel-sector model**, designed specifically to answer:

> **Where does the sector's decarbonization come from, and how does that abatement mix change when key structural constraints are relaxed or tightened?**

