#!/usr/bin/env python3
"""Uncertainty study: matched-world LCOP distribution across all three
emission targets -- the "cost distribution" violin-panel data.

Pure filter + join, no solving: reads all three sheets of ../../data/
mc_solves.xlsx (the single shared Monte Carlo solve behind every
uncertainty/ and violin/ study -- see ../../run_montecarlo.py). The
matched-world population is exactly the EF=1.6-feasible cells (794 of
them) -- since feasibility only gets easier as the target loosens, every
EF=1.6-feasible cell is also feasible at EF=1.8 and EF=2.0, so it already
has a solved row in all three sheets. Joining those three rows by
(structural coords, draw_id) gives lcop_1.6/1.8/2.0 for the SAME world --
no extra solving needed.

Output: data/cost_distribution.xlsx, sheet "plot_data" -- the 8
structural coordinates, draw_id, the 5 cost/tech draw values,
lcop_1.6, lcop_1.8, lcop_2.0.

    python run_costdistribution.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
MC_SOLVES = ROOT / "monte_carlo" / "data" / "mc_solves.xlsx"
OUT = HERE / "data" / "cost_distribution.xlsx"

TARGETS = [1.6, 1.8, 2.0]
MATCH_EF = 1.6   # tightest target; its feasible set nests inside the other two
STRUCT_COLS = ["ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
               "ramp", "build_cap", "legacy"]
DRAW_COLS = ["ccoal_price", "ng_price", "scrap_price", "theta_tech", "theta_ccs"]
JOIN_KEY = STRUCT_COLS + ["draw_id"]


def main():
    import pandas as pd
    sheets = {ef: pd.read_excel(MC_SOLVES, sheet_name=f"ef{ef}")
              for ef in TARGETS}
    sheets = {ef: df[df.solve_result == "solved"] for ef, df in sheets.items()}

    matched_keys = set(map(tuple, sheets[MATCH_EF][STRUCT_COLS].values.tolist()))

    merged = sheets[MATCH_EF][JOIN_KEY + DRAW_COLS].copy()
    merged["lcop_1.6"] = sheets[MATCH_EF]["lcop"].values
    for ef in [1.8, 2.0]:
        sub = sheets[ef][sheets[ef][STRUCT_COLS].apply(tuple, axis=1).isin(matched_keys)]
        merged = merged.merge(sub[JOIN_KEY + ["lcop"]].rename(columns={"lcop": f"lcop_{ef}"}),
                              on=JOIN_KEY, how="inner")

    columns = STRUCT_COLS + ["draw_id"] + DRAW_COLS + [f"lcop_{ef}" for ef in TARGETS]
    merged = merged[columns]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_excel(OUT, sheet_name="plot_data", index=False)
    print(f"cost_distribution: {len(matched_keys):,} matched cells, "
          f"{len(merged):,} matched worlds -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
