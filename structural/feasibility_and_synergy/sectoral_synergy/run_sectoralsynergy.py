#!/usr/bin/env python3
"""Sectoral Synergy study: minimum grid-decarbonization rate (theta_grid)
required to keep the model feasible at a fixed EF=1.8 target, as a
function of hydrogen start year and scrap-availability growth rate --
the grid-offset contour panel.

Under the model's theta_grid coupling, the required 2050 grid-EF offset
vs. the 2025 anchor IS theta_grid (EF_2050 = EF_2025*(1-theta)), so this
is a direct bisection search, not a proxy: for each (h2_start,
scrap_rate) cell, find the minimum theta_grid in [0,1] that keeps the
model feasible, via binary search:

  1. If theta_grid=0 is already feasible, theta_min = 0 (no grid
     decarbonization needed at all for this cell).
  2. If theta_grid=1 is still infeasible, no achievable theta_min exists
     in [0,1] -- recorded as "INFEASIBLE".
  3. Otherwise, bisect: 7 iterations halving [0,1], converging to a
     final bracket width of 1/128 (~0.0078). theta_min is the smallest
     tested value confirmed feasible, rounded to 4 decimals.

This exact procedure (short-circuit checks + 7-iteration bisection) was
verified against the original project's saved raw output before being
finalized here -- all 6 spot-checked cells matched to 4 decimal places.

Grid: 6 hydrogen start years (2030, 2033, 2036, 2039, 2042, 2045) x 8
scrap-growth rates (1%-8%/yr in 1-point steps) = 48 cells. This is a
DELIBERATELY FINER grid than the standard H2_START/SCRAP_RATE axes used
elsewhere in structural/ -- it exists to trace a smooth contour, not to
test discrete policy levels.

Output: data/sectoral_synergy.xlsx, sheet "grid_offset" -- h2_start,
scrap_rate, theta_min, offset_pct (= 100*theta_min, or "INFEASIBLE").

    python run_sectoralsynergy.py
"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
STRUCTURAL = HERE.parent.parent
ROOT = STRUCTURAL.parent
OUT = HERE / "data" / "sectoral_synergy.xlsx"

H2_START = [2030, 2033, 2036, 2039, 2042, 2045]
SCRAP_RATE = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]
N_BISECT_ITER = 7


def is_feasible(theta_grid, h2_start, scrap_rate, solver="gurobi"):
    from amplpy import AMPL
    import tempfile

    ampl = AMPL()
    ampl.cd(str(ROOT))
    ampl.set_option("solver_msg", 0)
    try:
        ampl.set_option("TMPDIR", tempfile.mkdtemp(prefix="amplwk_"))
    except Exception:
        pass
    ampl.eval("include core/model.mod;")
    ampl.eval("include structural/feasibility_and_synergy/sectoral_synergy/template_sectoralsynergy.mod;")
    ampl.eval(f"let ng_h2_start_year := {h2_start};")
    ampl.eval(f"let n8_scrap_rate := {scrap_rate};")
    ampl.eval(f"let theta_grid := {theta_grid};")
    ampl.eval(f"option solver {solver};")
    if solver == "gurobi":
        ampl.eval("option gurobi_options 'Threads=1';")
    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")
    status = ampl.get_value("solve_result")
    ampl.close()
    return status == "solved"


def bisect_theta_min(h2_start, scrap_rate, solver="gurobi"):
    if is_feasible(0.0, h2_start, scrap_rate, solver):
        return 0.0
    if not is_feasible(1.0, h2_start, scrap_rate, solver):
        return None   # no feasible theta_grid in [0,1] -- "INFEASIBLE"
    lo, hi = 0.0, 1.0
    for _ in range(N_BISECT_ITER):
        mid = (lo + hi) / 2
        if is_feasible(mid, h2_start, scrap_rate, solver):
            hi = mid
        else:
            lo = mid
    return round(hi, 4)


def _worker(args):
    h2_start, scrap_rate, solver = args
    theta_min = bisect_theta_min(h2_start, scrap_rate, solver)
    return h2_start, scrap_rate, theta_min


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-j", "--jobs", type=int, default=6)
    p.add_argument("--solver", default="gurobi")
    args = p.parse_args()

    import multiprocessing as mp
    todo = [(h2s, sr, args.solver) for h2s in H2_START for sr in SCRAP_RATE]
    rows = []
    with mp.Pool(args.jobs) as pool:
        for i, (h2_start, scrap_rate, theta_min) in enumerate(
                pool.imap(_worker, todo), 1):
            offset_pct = "INFEASIBLE" if theta_min is None else round(theta_min * 100, 2)
            rows.append({"h2_start": h2_start, "scrap_rate": scrap_rate,
                        "theta_min": theta_min if theta_min is not None else float("nan"),
                        "offset_pct": offset_pct})
            print(f"  {i:>2}/{len(todo)}  h2_start={h2_start} scrap_rate={scrap_rate}"
                  f"  theta_min={theta_min}", flush=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUT, sheet_name="grid_offset", index=False)
    print(f"\nwritten: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
