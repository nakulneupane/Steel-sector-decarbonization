#!/usr/bin/env python3
"""Axis registry for the Feasibility Drivers (Sobol) study.

ORGANISING PRINCIPLE
--------------------
Sweeps ONLY what policy controls -- levers a ministry can decide through
investment or regulation. Everything else is either a constant
(background condition) or belongs to a Monte Carlo layer (things nobody
controls). Learning rates are the clearest example of the latter:
`theta_tech` and `theta_ccs` depend on global science, not Indian policy,
so they are fixed here.

Emissions targets are 1.6 / 1.8 / 2.0 -- the CONSTRAINT being tested
against, not a lever.
"""

# ---------------------------------------------------------------- levers ---
# (label, axis-file stem). Availability regimes are time-indexed tables.
CCOAL = [
    ("abundant", "ccoal_abundant"),   # imports grow ~6.5%/yr -> 293.6 Mt by 2050
    ("scarce",   "ccoal_scarce"),     # ~0.8%/yr -> 91.1 Mt
]

NG = [
    ("abundant", "ng_policy"),        # national gas -> 32.2 Mm3 by 2050
    ("scarce",   "ng_bau"),           # -> 10.7 Mm3
]

# Integer switch year for No_H2_Before. 5-year spacing, matching the original
# import-dependence and hydrogen-delay studies.
H2_START = [2030, 2035, 2040, 2045]

# Annual scrap-availability growth -> collection infrastructure, ELV rules.
# 0.10 added 2026-08-21: scrap-pool-limited ceiling on Scrap-EAF's 2050 share
# is 44.7% at 0.08, 70.7% at 0.10 (exclusive-claim upper bound, ignoring BOF's
# 5% floor and build-budget competition -- see core/definitions.mod n8_phi_eaf).
SCRAP_RATE = [0.02, 0.04, 0.06, 0.08, 0.10]

# Grid/power-system learning rate, swept DIRECTLY (theta_grid in [0,1]; no
# back-solve from a target EF -- see core/definitions.mod:165-179). theta_grid=0
# holds the 2025 tariff/EF flat to 2050; theta_grid=1 reaches the $0.055/kWh,
# 0 tCO2/kWh 2050 targets. Since the axis IS theta_grid, every level is
# in-band by construction -- no extrapolation concept applies here anymore.
THETA_GRID = [0.25, 0.5, 0.75]

# Electrolyser deployment rate: scales the Gaussian growth ceiling in
# v_capacity.mod. Genuinely H2-specific: it scales ONLY the electrolyser ramp.
# In the original studies this axis also moved cap_add_common (collinear, ratio
# 2.5), so any effect attributed to "H2 ramp" was partly conventional capacity.
# Conventional build rate is now its own lever, BUILD_CAP below.
#
# Recalibrated 2026-08-21: the old 4/6/8 Mt levels did not span a pessimistic
# case at all (even "low"=4 already lets H2-DRI cover ~48% of 2050 demand at
# the earliest debut year, "high"=8 nearly saturates the whole sector at 95%).
# First tried 1/3/5 Mt, but 1 Mt ("low") proved too restrictive in the solved
# matrix (P(feasible)=27.6%, the run's 5th-most-decisive lever) -- revised to
# 2/4/6 Mt, ceilings (share of 2050 demand H2-DRI COULD reach, debut=2030 /
# 2035 / 2040 / 2045):
#   low (pessimistic): 23.8% / 17.4% / 11.0% / 4.6%
#   medium (normal):   47.7% / 34.8% / 22.0% / 9.1%
#   high (optimistic): 71.5% / 52.3% / 33.0% / 13.7% -- largest single route,
#     but leaves real headroom for scrap-EAF/BOF+CCS rather than crowding
#     them out mechanically. These are CEILINGS the optimizer may not choose
#     to reach, not forced outcomes.
RAMP = [("low", 2_000_000), ("medium", 4_000_000), ("high", 6_000_000)]

# Shared annual build budget across the four conventional routes (Mt/yr).
# Finance and EPC capacity the sector can deploy in one year -- industrial
# policy, so a lever rather than a constant. Two levels, 20 and 30 Mt/yr.
# Note the four routes COMPETE for this budget (cap_add_total in
# v_capacity.mod); it is not a per-route allowance.
BUILD_CAP = [("tight", 20e6), ("mid", 30e6)]

# Retirement policy for the 2025 fleet (207.75 Mt). The fleet's vintage is
# unknown, so these two settings BRACKET it rather than estimating a middle.
# Note "run-life" is not "no retirement": coal-DRI and NG-DRI still go by 2045
# and scrap-EAF by 2040, so 117.75 of 207.75 Mt retires either way. The cases
# differ mainly over the fate of 90 Mt of BOF.
LEGACY = [("run-life", 0), ("mandated-phaseout", 1)]

# ---------------------------------------------------------------- target ---
# The constraint being tested against, not a lever. Matches EF_LEVELS in the
# original hydrogen-delay and scrap studies.
AVG_EMI = [1.6, 1.8, 2.0]


AXES = {
    "ccoal":      CCOAL,
    "ng":         NG,
    "h2_start":   H2_START,
    "scrap_rate": SCRAP_RATE,
    "theta_grid": THETA_GRID,
    "ramp":       RAMP,
    "build_cap":  BUILD_CAP,
    "legacy":     LEGACY,
    "avg_emi":    AVG_EMI,
}
