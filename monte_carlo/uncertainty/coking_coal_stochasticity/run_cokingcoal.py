#!/usr/bin/env python3
"""Uncertainty study: matched LCOP sensitivity to hydrogen-start delay,
split out by the draw's coking-coal price -- the "stochasticity of
coking coal" box/whisker panel data.

Pure filter, no solving: reads the EF=1.8 sheet of ../../data/
mc_solves.xlsx (the single shared Monte Carlo solve behind every
uncertainty/ and violin/ study -- see ../../run_montecarlo.py). No extra
solves are needed for the delay comparison itself -- h2_start is already
one of the 8 structural axes, so cells sharing every OTHER axis but
differing in h2_start are simply separate rows in this same sheet; the
plot pivots on h2_start to compare 2030 vs. 2035/2040/2045 at matched
(other-axes, draw_id) pairs, and splits each comparison by the draw's
ccoal_price.

Output: data/coking_coal_stochasticity.xlsx, sheet "plot_data" -- the 8
structural coordinates (including h2_start), avg_emi, the 5 cost/tech
draw values (including ccoal_price), lcop.

    python run_cokingcoal.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
MC_SOLVES = ROOT / "monte_carlo" / "data" / "mc_solves.xlsx"
OUT = HERE / "data" / "coking_coal_stochasticity.xlsx"

STRUCT_COLS = ["ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
               "ramp", "build_cap", "legacy", "avg_emi"]
DRAW_COLS = ["ccoal_price", "ng_price", "scrap_price", "theta_tech", "theta_ccs"]
COLUMNS = STRUCT_COLS + DRAW_COLS + ["lcop"]


def main():
    import pandas as pd
    d = pd.read_excel(MC_SOLVES, sheet_name="ef1.8")
    d = d[d.solve_result == "solved"][COLUMNS]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_excel(OUT, sheet_name="plot_data", index=False)
    print(f"coking_coal_stochasticity: {len(d):,} rows -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
