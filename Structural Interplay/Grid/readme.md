# Grid-Offset Requirement

## Purpose

The **Grid-Offset Requirement** study determines how clean the electricity grid must become by 2050 for the steel sector to remain feasible under a fixed emissions-intensity target.

For each combination of:

* H₂ deployment start year (2030–2045), and
* annual scrap-availability growth (1–8%),

the model sweeps the **2050 grid emission factor** and identifies the **dirtiest grid that still satisfies the 1.8 tCO₂/tCS emissions constraint**.

## Coupled Grid Assumption

Grid carbon intensity and the industrial electricity tariff are treated as **coupled outcomes of the same grid-transition parameter**. Therefore, changing the 2050 grid emission factor also changes the corresponding tariff trajectory.

This avoids treating grid decarbonization and electricity cost as independent assumptions.

## Approach

The underlying steel-sector model and all other assumptions remain unchanged. For each H₂–scrap combination, multiple 2050 grid emission factors are tested.

A run is classified as feasible or infeasible based on whether the model can satisfy the emissions constraint. The required grid threshold is then identified from the sweep as the **highest (dirtiest) 2050 grid emission factor that remains feasible**.

The study therefore answers:

> **If H₂ deployment is delayed and/or scrap availability is limited, how much additional grid decarbonization is required to maintain the sector's emissions target?**

## Computational Structure
The study consists of **6 H₂ start years × 8 scrap-growth rates × 18 grid-emission-factor values = 864 model runs**.
