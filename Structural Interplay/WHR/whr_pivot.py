"""
Reads  results/whr_summary.csv   (written by whr.bat)
Writes results/whr_summary.xlsx:
Theta (CCS+grid) | Steam sourcing | Effective capture cost
               ($/tCO2) | Cumulative capture (MtCO2) | CCS 2050 (MtCO2) |
               Boiler steam share | LCOP ($/t). X on infeasible rows.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "whr_summary.csv"
XLSX = HERE / "results" / "whr_summary.xlsx"


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run whr.bat first.")

    out = pd.DataFrame({
        "Theta (CCS+grid)": df["theta"],
        "Steam sourcing": df["mode"],
        "Effective capture cost ($/tCO2)": df["eff_capture_cost"].round(2),
        "Cumulative capture (MtCO2)": (df["cum_captured"] / 1e6).round(1),
        "CCS 2050 (MtCO2)": (df["ccs_2050"] / 1e6).round(1),
        "Boiler steam share": df["boiler_steam_share"].round(3),
        "LCOP ($/t)": df["lcop"].round(2),
    })
    bad = df["solve_result"] != "solved"
    vcols = [c for c in out.columns if c not in ("Theta (CCS+grid)", "Steam sourcing")]
    out[vcols] = out[vcols].astype(object)
    out.loc[bad, vcols] = "X"
    out = out.sort_values(["Theta (CCS+grid)", "Steam sourcing"]).reset_index(drop=True)

    ok = df[df["solve_result"] == "solved"]
    piv = ok.pivot_table(index="theta", columns="mode", values="eff_capture_cost")
    if {"integrated", "boiler-only"} <= set(piv.columns):
        val = pd.DataFrame({
            "Theta (CCS+grid)": piv.index,
            "Integration value ($/tCO2)": (piv["boiler-only"] - piv["integrated"]).round(2),
        }).reset_index(drop=True)
    else:
        val = pd.DataFrame()

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="summary", index=False)
        if not val.empty:
            val.to_excel(xl, sheet_name="summary", index=False,
                         startrow=len(out) + 3)
        df.to_excel(xl, sheet_name="runs", index=False)

    print(f"Wrote {XLSX}")
    print(f"  {len(df)} runs, {int(bad.sum())} infeasible (marked X).")


if __name__ == "__main__":
    main()
