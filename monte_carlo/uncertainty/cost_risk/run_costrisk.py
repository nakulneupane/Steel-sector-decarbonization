#!/usr/bin/env python3
"""Uncertainty study: one-at-a-time LCOP sensitivity to each cost/tech
draw parameter -- the "drivers of cost risk" tornado-diagram data.

Pure filter, no solving: reads the EF=1.8 sheet of ../../data/
mc_solves.xlsx (the single shared Monte Carlo solve behind every
uncertainty/ and violin/ study -- see ../../run_montecarlo.py) and keeps
just the columns this panel needs: lcop, the 5 draw values, and the 8
structural coordinates as the cell-demeaning group key (so that pure
driver-sensitivity is isolated from cell-to-cell structural variation).

Output: data/cost_risk.xlsx, sheet "plot_data" -- the 8 structural
coordinates, avg_emi, the 5 cost/tech draw values, lcop.

    python run_costrisk.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
MC_SOLVES = ROOT / "monte_carlo" / "data" / "mc_solves.xlsx"
OUT = HERE / "data" / "cost_risk.xlsx"

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
    print(f"cost_risk: {len(d):,} rows -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
