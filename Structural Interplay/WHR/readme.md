# WHR–CCS Integration Study

## Purpose

The **WHR–CCS Integration Study** evaluates the value of using waste heat recovery (WHR) to supply regeneration steam for CCS instead of relying entirely on a gas boiler.

Two steam-sourcing configurations are compared:

* **WHR-integrated:** waste heat can supply CCS regeneration steam.
* **Boiler-only:** CCS regeneration steam is supplied by the gas boiler.

The comparison is performed across different levels of joint **CCS and grid ecosystem maturity** while keeping the remaining model assumptions fixed.

## Key Question

> **How much does integrating waste heat reduce the effective cost of CCS?**

The study measures the effective capture cost while accounting for both CCS costs and the opportunity cost of WHR power that is diverted to steam production.

## Computational Structure

The study performs **10 runs**: 5 maturity levels × 2 steam-sourcing configurations.

* `whr_template.mod` — parameterized WHR–CCS model.
* `whr.bat` — parameter sweep.
