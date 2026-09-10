#!/usr/bin/env python3
"""Uncertainty study: 2050 route-share risk (P10-P90) under cost/tech
uncertainty -- the "shares" panel data.

Pure filter, no solving: reads the EF=1.8 sheet of ../../data/
mc_solves.xlsx (the single shared Monte Carlo solve behind every
uncertainty/ and violin/ study -- see ../../run_montecarlo.py) and keeps
just the columns this panel needs.

Output: data/shares.xlsx, sheet "plot_data" -- the 8 structural
coordinates, avg_emi, the 5 cost/tech draw values, lcop, and the 5 route
shares (share_bof/cdri/ngdri/h2/scrap).

    python run_shares.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
MC_SOLVES = ROOT / "monte_carlo" / "data" / "mc_solves.xlsx"
OUT = HERE / "data" / "shares.xlsx"

STRUCT_COLS = ["ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
               "ramp", "build_cap", "legacy", "avg_emi"]
DRAW_COLS = ["ccoal_price", "ng_price", "scrap_price", "theta_tech", "theta_ccs"]
SHARE_COLS = ["share_bof", "share_cdri", "share_ngdri", "share_h2", "share_scrap"]
COLUMNS = STRUCT_COLS + DRAW_COLS + ["lcop"] + SHARE_COLS


def main():
    import pandas as pd
    d = pd.read_excel(MC_SOLVES, sheet_name="ef1.8")
    d = d[d.solve_result == "solved"][COLUMNS]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_excel(OUT, sheet_name="plot_data", index=False)
    print(f"shares: {len(d):,} rows -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
