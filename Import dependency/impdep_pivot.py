"""
Reads  results/impdep_summary.csv   (written by impdep.bat)
Writes results/impdep_summary.xlsx:
Regime | H2 start year | Import bill ($B) | Coking-coal bill
               ($B) | NG import bill ($B) | NG imports (Mt) | Cumulative CO2
               (Gt) | LCOP ($/t) | D | 2050 route shares (BF-BOF, Coal-DRI,
               NG-DRI, H2-DRI, Scrap-EAF). X on infeasible rows.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "impdep_summary.csv"
XLSX = HERE / "results" / "impdep_summary.xlsx"

REG_ORDER = ["HiCoal-HiNG", "HiCoal-LoNG", "LoCoal-HiNG", "LoCoal-LoNG"]


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run impdep.bat first.")

    red_total = df["red_h2_2050"] + df["ccs_2050"]
    out = pd.DataFrame({
        "Regime": pd.Categorical(df["regime"], categories=REG_ORDER, ordered=True),
        "H2 start year": df["h2_start"],
        "Cumulative import bill 2025-50 ($B)": (df["import_bill"] / 1e9).round(2),
        "Cumulative coking-coal bill ($B)": (df["ccoal_bill"] / 1e9).round(2),
        "Cumulative NG import bill ($B)": (df["ng_import_bill"] / 1e9).round(2),
        "Cumulative NG imports 2025-50 (Mt)": (df["ng_import_qty"] / 1e6).round(2),
        "Cumulative CO2 (Gt)": (df["cum_co2"] / 1e9).round(3),
        "LCOP ($/t)": df["lcop"].round(2),
        "D": (df["red_h2_2050"] / red_total.where(red_total > 0)).round(3),
        "BF-BOF share 2050": df["share_bof"].round(3),
        "Coal-DRI share 2050": df["share_cdri"].round(3),
        "NG-DRI share 2050": df["share_ngdri"].round(3),
        "H2-DRI share 2050": df["share_h2"].round(3),
        "Scrap-EAF share 2050": df["share_scrap"].round(3),
    })
    bad = df["solve_result"] != "solved"
    vcols = [c for c in out.columns if c not in ("Regime", "H2 start year")]
    out[vcols] = out[vcols].astype(object)
    out.loc[bad, vcols] = "X"
    out = out.sort_values(["Regime", "H2 start year"]).reset_index(drop=True)

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="summary", index=False)
        df.to_excel(xl, sheet_name="runs", index=False)

    print(f"Wrote {XLSX}")
    print(f"  {len(df)} runs, {int(bad.sum())} infeasible (marked X).")


if __name__ == "__main__":
    main()
