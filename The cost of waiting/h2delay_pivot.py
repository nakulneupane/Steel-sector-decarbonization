"""
Reads  Plots/H2_Delay/results/h2delay_summary.csv  (written by h2_delay.bat)
Writes Plots/H2_Delay/results/h2delay_summary.xlsx with:
  "summary" -- columns in order:
        EF | Ramp limit | H2 start year | H2 DRI Capacity (Mt/yr) |
        CCS 2050 (MtCO2) | D | LCOP ($/t)
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "h2delay_summary.csv"
XLSX = HERE / "results" / "h2delay_summary.xlsx"

RAMP_ORDER = ["Low", "Medium", "High"]


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run h2_delay.bat first.")

    red_total = df["red_h2_2050"] + df["ccs_2050"]
    out = pd.DataFrame({
        "EF": df["avg_emi"],
        "Ramp limit": pd.Categorical(df["ramp_label"], categories=RAMP_ORDER, ordered=True),
        "H2 start year": df["h2_start"],
        "H2 DRI Capacity (Mt/yr)": (df["h2dri_cap_2050"] / 1e6).round(2),
        "CCS 2050 (MtCO2)": (df["ccs_2050"] / 1e6).round(2),
        "D": (df["red_h2_2050"] / red_total.where(red_total > 0)).round(3),
        "LCOP ($/t)": df["lcop"].round(2),
    })
    bad = df["solve_result"] != "solved"
    value_cols = ["H2 DRI Capacity (Mt/yr)", "CCS 2050 (MtCO2)", "D", "LCOP ($/t)"]
    out[value_cols] = out[value_cols].astype(object)
    out.loc[bad, value_cols] = "X"
    out = out.sort_values(["EF", "Ramp limit", "H2 start year"]).reset_index(drop=True)

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="summary", index=False)
        df.to_excel(xl, sheet_name="runs", index=False)

    print(f"Wrote {XLSX}")
    print(f"  {len(df)} runs, {int(bad.sum())} infeasible (marked X).")


if __name__ == "__main__":
    main()
