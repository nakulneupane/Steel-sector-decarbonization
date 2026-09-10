#!/usr/bin/env python3
"""Feasibility Drivers study: total-effect Sobol index (S_T) of each
structural axis on feasibility, computed separately within each
emission target -- the radar-panel data.

Solves the full 8-structural-axis cross product at build_cap 20 and 30
Mt/yr (tight, mid). 8,640 cells = (2 ccoal x 2 ng x 4 h2_start x
5 scrap_rate x 3 theta_grid x 3 ramp x 2 build_cap x 2 legacy) x 3 avg_emi.

Output: data/feasibility_drivers.xlsx --
  sheet "raw_matrix"   one row per solved cell (coords + solve_result +
                        every report.mod metric)
  sheet "sobol_by_ef"  the derived S_T summary actually plotted: one row
                        per (driver, avg_emi), 8 drivers x 3 targets = 24
                        rows

    python run_feasibilitydrivers.py -j 6             # full 8,640-cell sweep
    python run_feasibilitydrivers.py -j 6 --resume    # continue a partial run
"""
import argparse
import csv
import itertools
import multiprocessing as mp
import pathlib
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent
STRUCTURAL = HERE.parent.parent
ROOT = STRUCTURAL.parent
sys.path.insert(0, str(HERE))
import axes as AX  # noqa: E402

AXES_DIR = STRUCTURAL / "axes"
OUT = HERE / "data" / "feasibility_drivers.xlsx"
CSV_OUT = HERE / "data" / "raw_matrix.csv"

# Same 8 axes as the original panel_sobol -- order fixes the radar spoke
# order (sorted by mean S_T descending, at plot time, not here).
SOBOL_AXES = ["build_cap", "scrap_rate", "h2_start", "ccoal",
              "theta_grid_target", "ramp", "legacy", "ng"]
SOBOL_EFS = [1.6, 1.8, 2.0]
SOBOL_NICE = {
    "build_cap": "Build budget", "scrap_rate": "Scrap growth",
    "h2_start": "H2 start year", "ccoal": "Coking-coal supply",
    "theta_grid_target": "Grid learning", "ramp": "H2 supply ramp",
    "legacy": "Legacy retirement", "ng": "NG supply",
}

COORD_COLUMNS = [
    "ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
    "ramp", "build_cap", "legacy", "avg_emi",
]
STATUS_COLUMNS = ["solve_result", "objective", "theta_grid"]
METRIC_COLUMNS = [
    ("grid_ef_2050",      "n9_grid_ef[2050]"),
    ("tariff_2050",       "ng_cost_power[2050]"),
    ("lcop",              "m_lcop"),
    ("emis2050",          "total_emissions[2050]/total_steel[2050]"),
    ("cum_co2",           "m_cum_co2"),
    ("avg_emis",          "m_avg_emis"),
    ("share_bof",         "m_sh_bof"),
    ("share_cdri",        "m_sh_cdri"),
    ("share_ngdri",       "m_sh_ngdri"),
    ("share_h2",          "m_sh_h2"),
    ("share_scrap",       "m_sh_scrap"),
    ("ccs_2050",          "total_ccs[2050]"),
]
COLUMNS = COORD_COLUMNS + STATUS_COLUMNS + [c for c, _ in METRIC_COLUMNS]

def cells():
    names = list(AX.AXES)
    for combo in itertools.product(*(AX.AXES[n] for n in names)):
        yield dict(zip(names, combo))


def coord_key(cell):
    return (cell["ccoal"][0], cell["ng"][0], cell["h2_start"],
            cell["scrap_rate"], cell["theta_grid"], cell["ramp"][0],
            cell["build_cap"][0], cell["legacy"][0], cell["avg_emi"])


def solve_cell(cell, solver="gurobi"):
    from amplpy import AMPL

    ccoal_label, ccoal_file = cell["ccoal"]
    ng_label, ng_file = cell["ng"]
    ramp_label, h2_ref = cell["ramp"]
    legacy_label, legacy_flag = cell["legacy"]
    build_label, build_cap = cell["build_cap"]
    theta_grid_target = cell["theta_grid"]

    ampl = AMPL()
    ampl.cd(str(ROOT))
    ampl.set_option("solver_msg", 0)
    try:
        ampl.set_option("TMPDIR", tempfile.mkdtemp(prefix="amplwk_"))
    except Exception:
        pass

    ampl.eval("include core/model.mod;")
    if ccoal_file:
        ampl.eval(f"include {AXES_DIR.relative_to(ROOT)}/{ccoal_file}.mod;")
    if ng_file:
        ampl.eval(f"include {AXES_DIR.relative_to(ROOT)}/{ng_file}.mod;")
    ampl.eval("include structural/feasibility_and_synergy/feasibility_drivers/template_feasibilitydrivers.mod;")

    ampl.eval(f"let ng_h2_start_year := {cell['h2_start']};")
    ampl.eval(f"let avg_emi := {cell['avg_emi']};")
    ampl.eval(f"let h2_ref_cap := {h2_ref};")
    ampl.eval(f"let n8_scrap_rate := {cell['scrap_rate']};")
    ampl.eval(f"let legacy_phaseout := {legacy_flag};")
    ampl.eval(f"let cap_add_common := {build_cap};")
    ampl.eval(f"let theta_grid := {theta_grid_target};")

    ampl.eval(f"option solver {solver};")
    if solver == "gurobi":
        ampl.eval("option gurobi_options 'Threads=1';")
    ampl.eval("drop emission_monotonic;")
    ampl.eval("solve;")

    status = ampl.get_value("solve_result")
    try:
        obj = ampl.get_objective("obj").value()
    except Exception:
        obj = float("nan")

    ampl.eval("include structural/report.mod;")

    row = {
        "ccoal": ccoal_label, "ng": ng_label, "h2_start": cell["h2_start"],
        "scrap_rate": cell["scrap_rate"], "theta_grid_target": theta_grid_target,
        "ramp": ramp_label, "build_cap": build_label,
        "legacy": legacy_label, "avg_emi": cell["avg_emi"],
        "solve_result": status, "objective": obj,
        "theta_grid": ampl.get_value("theta_grid"),
    }
    for col, expr in METRIC_COLUMNS:
        try:
            row[col] = ampl.get_value(expr)
        except Exception:
            row[col] = ""
    ampl.close()
    return row


def _worker(cell):
    try:
        return solve_cell(cell, solver=_worker.solver)
    except Exception as exc:
        row = {c: "" for c in COLUMNS}
        row.update({
            "ccoal": cell["ccoal"][0], "ng": cell["ng"][0],
            "h2_start": cell["h2_start"], "scrap_rate": cell["scrap_rate"],
            "theta_grid_target": cell["theta_grid"], "ramp": cell["ramp"][0],
            "build_cap": cell["build_cap"][0],
            "legacy": cell["legacy"][0], "avg_emi": cell["avg_emi"],
            "solve_result": f"ERROR: {type(exc).__name__}: {exc}"[:200],
        })
        return row


def _init(solver):
    _worker.solver = solver


def compute_sobol(df):
    """Reproduces synergy_plot.py's panel_sobol computation exactly."""
    df = df[df.solve_result != ""].copy()
    df["y"] = (df.solve_result == "solved").astype(float)
    rows = []
    for ef in SOBOL_EFS:
        sub = df[df.avg_emi == ef]
        V = sub["y"].var(ddof=0)
        mu = sub["y"].mean()
        for a in SOBOL_AXES:
            others = [x for x in SOBOL_AXES if x != a]
            cond = sub.groupby(others)["y"].mean()
            ST = 1 - ((cond - mu) ** 2).mean() / V
            rows.append({"avg_emi": ef, "driver": SOBOL_NICE[a], "S_T": round(ST, 4)})
    import pandas as pd
    return pd.DataFrame(rows)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-j", "--jobs", type=int, default=6)
    p.add_argument("--solver", default="gurobi")
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()

    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)

    todo = list(cells())

    done = set()
    if args.resume and CSV_OUT.exists():
        with open(CSV_OUT) as fh:
            for r in csv.DictReader(fh):
                done.add((r["ccoal"], r["ng"], int(r["h2_start"]),
                          float(r["scrap_rate"]), float(r["theta_grid_target"]),
                          r["ramp"], r["build_cap"], r["legacy"],
                          float(r["avg_emi"])))
        todo = [c for c in todo if coord_key(c) not in done]
        print(f"resume: {len(done):,} done, {len(todo):,} remaining")

    if not todo:
        print("nothing to do")
        return 0

    mode = "a" if (args.resume and CSV_OUT.exists()) else "w"
    t0 = time.time()
    n_solved = n_infeas = n_err = 0

    with open(CSV_OUT, mode, newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        if mode == "w":
            w.writeheader()
        with mp.Pool(args.jobs, initializer=_init, initargs=(args.solver,)) as pool:
            for i, row in enumerate(pool.imap_unordered(_worker, todo, chunksize=8), 1):
                w.writerow(row)
                sr = str(row["solve_result"])
                if sr == "solved":
                    n_solved += 1
                elif sr.startswith("ERROR"):
                    n_err += 1
                else:
                    n_infeas += 1
                if i % 500 == 0 or i == len(todo):
                    el = time.time() - t0
                    rate = i / el
                    eta = (len(todo) - i) / rate / 60
                    print(f"  {i:>7,}/{len(todo):,}  {rate:6.1f} cell/s  "
                          f"ETA {eta:6.1f} min  solved={n_solved:,} "
                          f"infeas={n_infeas:,} err={n_err:,}", flush=True)
                    fh.flush()

    el = time.time() - t0
    print(f"\n{len(todo):,} cells in {el/60:.1f} min ({len(todo)/el:.1f}/s)")
    print(f"solved={n_solved:,}  infeasible={n_infeas:,}  errors={n_err:,}")

    if n_err == 0:
        import pandas as pd
        raw = pd.read_csv(CSV_OUT)
        sobol = compute_sobol(raw)
        with pd.ExcelWriter(OUT) as xw:
            raw.to_excel(xw, sheet_name="raw_matrix", index=False)
            sobol.to_excel(xw, sheet_name="sobol_by_ef", index=False)
        print(f"written: {OUT.relative_to(ROOT)}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
