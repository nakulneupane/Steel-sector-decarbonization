#!/usr/bin/env python3
"""H2 Delay study: LCOP and 2050 H2-DRI share vs. hydrogen start year,
across emission targets and H2 supply-ramp levels.

36 cells = 3 emission targets (avg_emi) x 3 H2-ramp levels (h2_ref_cap)
x 4 hydrogen start years (ng_h2_start_year). Everything else is fixed
by template_h2delay.mod.

Output: data/h2_delay.xlsx, sheet "plot_data" -- EF, H2 supply, H2 start
year, LCOP ($/t), H2-DRI share 2050 (%). Infeasible cells are written as
"X" in both metric columns.

    python run_h2delay.py
"""
import argparse
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
import solve_common as SC  # noqa: E402

OUT = HERE / "data" / "h2_delay.xlsx"

AVG_EMI = [1.6, 1.8, 2.0]
RAMP = [("Low", 2_000_000), ("Mid", 4_000_000), ("High", 6_000_000)]
H2_START = [2030, 2035, 2040, 2045]


def solve_cell(avg_emi, ramp_value, h2_start, solver="gurobi"):
    ampl = SC.new_ampl()
    ampl.eval("include core/model.mod;")
    ampl.eval("include structural/h2_delay/template_h2delay.mod;")
    ampl.eval(f"let avg_emi := {avg_emi};")
    ampl.eval(f"let h2_ref_cap := {ramp_value};")
    ampl.eval(f"let ng_h2_start_year := {h2_start};")

    status = SC.solve(ampl, solver=solver)
    lcop = share_h2 = None
    if status == "solved":
        ampl.eval("include structural/report.mod;")
        lcop = ampl.get_value("m_lcop")
        share_h2 = ampl.get_value("m_sh_h2")
    ampl.close()
    return status, lcop, share_h2


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--solver", default="gurobi")
    args = p.parse_args()

    rows = []
    n = len(AVG_EMI) * len(RAMP) * len(H2_START)
    i = 0
    for ef in AVG_EMI:
        for ramp_label, ramp_value in RAMP:
            for h2_start in H2_START:
                i += 1
                status, lcop, share_h2 = solve_cell(ef, ramp_value, h2_start,
                                                    solver=args.solver)
                if status == "solved":
                    row = {
                        "EF": ef, "H2 supply": ramp_label,
                        "H2 start year": h2_start,
                        "LCOP ($/t)": round(lcop, 2),
                        "H2-DRI share 2050 (%)": round(share_h2 * 100, 2),
                    }
                else:
                    row = {
                        "EF": ef, "H2 supply": ramp_label,
                        "H2 start year": h2_start,
                        "LCOP ($/t)": "X", "H2-DRI share 2050 (%)": "X",
                    }
                rows.append(row)
                print(f"  {i:>2}/{n}  EF={ef} ramp={ramp_label:5s} "
                      f"h2_start={h2_start}  {status}", flush=True)

    import pandas as pd
    df = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUT, sheet_name="plot_data", index=False)
    print(f"\nwritten: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
