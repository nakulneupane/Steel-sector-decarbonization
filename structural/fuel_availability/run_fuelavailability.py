#!/usr/bin/env python3
"""Fuel Availability study: 2050 route shares and cumulative import bill
across coking-coal/natural-gas availability regimes and hydrogen start year.

16 cells = 2 coking-coal regimes x 2 natural-gas regimes x 4 hydrogen
start years. Everything else is fixed by template_fuelavailability.mod.

Output: data/fuel_availability.xlsx, sheet "plot_data" -- Regime, Coking
coal, NG, H2 start year, 5 route shares, Cumulative import bill 2025-50
($B). Infeasible cells are written as "X" in every metric column.

    python run_fuelavailability.py
"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import solve_common as SC  # noqa: E402

AXES_DIR = ROOT / "structural" / "axes"
OUT = HERE / "data" / "fuel_availability.xlsx"

# (label, axis-file stem, short code for the Regime string)
CCOAL = [("abundant", "ccoal_abundant", "Ab"), ("scarce", "ccoal_scarce", "Sc")]
NG = [("abundant", "ng_policy", "Ab"), ("scarce", "ng_bau", "Sc")]
H2_START = [2030, 2035, 2040, 2045]

SHARE_METRICS = [
    ("BF-BOF share 2050", "m_sh_bof"),
    ("Coal-DRI share 2050", "m_sh_cdri"),
    ("NG-DRI share 2050", "m_sh_ngdri"),
    ("H2-DRI share 2050", "m_sh_h2"),
    ("Scrap-EAF share 2050", "m_sh_scrap"),
]


def solve_cell(ccoal_file, ng_file, h2_start, solver="gurobi"):
    ampl = SC.new_ampl()
    ampl.eval("include core/model.mod;")
    ampl.eval(f"include {AXES_DIR.relative_to(ROOT)}/{ccoal_file}.mod;")
    ampl.eval(f"include {AXES_DIR.relative_to(ROOT)}/{ng_file}.mod;")
    ampl.eval("include structural/fuel_availability/template_fuelavailability.mod;")
    ampl.eval(f"let ng_h2_start_year := {h2_start};")

    status = SC.solve(ampl, solver=solver)
    shares = {}
    import_bill = None
    if status == "solved":
        ampl.eval("include structural/report.mod;")
        for _, expr in SHARE_METRICS:
            shares[expr] = ampl.get_value(expr)
        import_bill = ampl.get_value("m_cum_ccoal_bill + m_cum_ng_bill")
    ampl.close()
    return status, shares, import_bill


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--solver", default="gurobi")
    args = p.parse_args()

    rows = []
    n = len(CCOAL) * len(NG) * len(H2_START)
    i = 0
    for ccoal_label, ccoal_file, ccoal_code in CCOAL:
        for ng_label, ng_file, ng_code in NG:
            regime = f"{ccoal_code}Coal-{ng_code}NG"
            for h2_start in H2_START:
                i += 1
                status, shares, import_bill = solve_cell(ccoal_file, ng_file, h2_start,
                                                          solver=args.solver)
                row = {"Regime": regime, "Coking coal": ccoal_label,
                       "NG": ng_label, "H2 start year": h2_start}
                if status == "solved":
                    for col, expr in SHARE_METRICS:
                        row[col] = round(shares[expr], 4)
                    row["Cumulative import bill 2025-50 ($B)"] = round(import_bill / 1e9, 1)
                else:
                    for col, _ in SHARE_METRICS:
                        row[col] = "X"
                    row["Cumulative import bill 2025-50 ($B)"] = "X"
                rows.append(row)
                print(f"  {i:>2}/{n}  {regime}  h2_start={h2_start}  {status}", flush=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUT, sheet_name="plot_data", index=False)
    print(f"\nwritten: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
