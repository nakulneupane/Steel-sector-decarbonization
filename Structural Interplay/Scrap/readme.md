# Scrap-Growth Study

## Purpose

The **Scrap-Growth Study** examines how increasing scrap availability changes the composition of steel-sector decarbonization, particularly the relative contribution of **hydrogen and CCS**.

The study varies annual scrap-availability growth from **0–10%/yr** under three emissions-intensity targets: **1.6, 1.8, and 2.0 tCO₂/tCS**.

All other model assumptions are held at a fixed central configuration, including H₂ deployment, grid emissions factor, ramp limits, NG price, and learning parameters.

## Key Question

> **As scrap availability increases, does scrap primarily displace hydrogen-based abatement or CCS?**

The study tracks the resulting H₂ and CCS contributions to 2050 emissions reduction, together with scrap utilization and availability, to identify when scrap becomes a binding or substituting decarbonization resource.

## Computational Structure

The study performs **33 runs** (11 scrap-growth rates × 3 emissions targets) using:

* `scrap_template.mod` — parameterized model;
* `scrap.bat` — parameter sweep; and
