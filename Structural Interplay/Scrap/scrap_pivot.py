"""
Reads  results/scrap_summary.csv   (written by scrap.bat)
Writes results/scrap_summary.xlsx:
  EF | Scrap growth (%/yr) | H2 DRI Capacity (Mt/yr) |
               CCS 2050 (MtCO2) | D | LCOP ($/t) | Scrap use 2050 (Mt) |
               Scrap limit 2050 (Mt) | Scrap-EAF share 2050
     D = red_H2/(red_H2 + red_CCS) in 2050 (0 = CCS-driven, 1 = H2-driven).
     Infeasible runs read 'X'. Sorted by EF, scrap growth.
"""

from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "scrap_summary.csv"
XLSX = HERE / "results" / "scrap_summary.xlsx"


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run scrap.bat first.")

    red_total = df["red_h2_2050"] + df["ccs_2050"]
    out = pd.DataFrame({
        "EF": df["avg_emi"],
        "Scrap growth (%/yr)": (df["scrap_rate"] * 100).round(0).astype(int),
        "H2 DRI Capacity (Mt/yr)": (df["h2dri_cap_2050"] / 1e6).round(2),
        "CCS 2050 (MtCO2)": (df["ccs_2050"] / 1e6).round(2),
        "D": (df["red_h2_2050"] / red_total.where(red_total > 0)).round(3),
        "LCOP ($/t)": df["lcop"].round(2),
        "Scrap use 2050 (Mt)": (df["scrap_use_2050"] / 1e6).round(2),
        "Scrap limit 2050 (Mt)": (df["scrap_limit_2050"] / 1e6).round(2),
        "Scrap-EAF share 2050": df["scrapeaf_share_2050"].round(3),
    })
    bad = df["solve_result"] != "solved"
    value_cols = [c for c in out.columns if c not in ("EF", "Scrap growth (%/yr)")]
    out[value_cols] = out[value_cols].astype(object)
    out.loc[bad, value_cols] = "X"
    out = out.sort_values(["EF", "Scrap growth (%/yr)"]).reset_index(drop=True)

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        out.to_excel(xl, sheet_name="summary", index=False)
        df.to_excel(xl, sheet_name="runs", index=False)

    print(f"Wrote {XLSX}")
    print(f"  {len(df)} runs, {int(bad.sum())} infeasible (marked X).")


if __name__ == "__main__":
    main()
