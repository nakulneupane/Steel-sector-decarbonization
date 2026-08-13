"""
Reads  results/grid_summary.csv   (written by grid.bat / gridresult.mod)
Writes results/grid_summary.xlsx  with two sheets:
  "offset_required" = one matrix per metric, rows = H2 start year, columns =
                       scrap growth rate (sheet 2):
                         (a) required grid offset, % relative to the 2025 EF
                             (0.000886 tCO2/kWh),
                         (b) the corresponding dirtiest feasible 2050 EF.
                       For each combo the requirement is the DIRTIEST swept
                       grid_ef_end whose run solved (the cap avg_emi stays
                       feasible); combos where NO swept grid solves- not
                       even the cleanest- read "INFEASIBLE".

"""

from pathlib import Path

import pandas as pd

EF_2025 = 0.000886          # 2025 grid emission factor, tCO2/kWh (n9_grid_ef_start)

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "grid_summary.csv"
XLSX = HERE / "results" / "grid_summary.xlsx"


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run grid.bat first.")

    solved = df[df["solve_result"] == "solved"]

    # Required offset per (h2_start, scrap_rate): dirtiest feasible 2050 EF.
    req_ef = (
        solved.groupby(["h2_start", "scrap_rate"])["grid_ef_end"]
        .max()
        .unstack("scrap_rate")
    )
    # Reindex onto the FULL swept grid so all-infeasible combos appear as NaN.
    full_h2 = sorted(df["h2_start"].unique())
    full_scrap = sorted(df["scrap_rate"].unique())
    req_ef = req_ef.reindex(index=full_h2, columns=full_scrap)

    offset_pct = (1 - req_ef / EF_2025) * 100

    offset_disp = offset_pct.round(1).astype(object).where(req_ef.notna(), "INFEASIBLE")
    ef_disp = req_ef.round(5).astype(object).where(req_ef.notna(), "INFEASIBLE")

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        df.to_excel(xl, sheet_name="runs", index=False)

        sheet = "offset_required"
        pd.DataFrame(
            {0: ["Required grid offset by 2050, % of the 2025 EF "
                 f"({EF_2025} tCO2/kWh). Rows = H2 start year, columns = scrap "
                 "growth rate. INFEASIBLE = the avg_emi cap cannot be met at "
                 "ANY swept grid EF (even zero)."]}
        ).to_excel(xl, sheet_name=sheet, index=False, header=False, startrow=0)
        offset_disp.rename_axis(index="h2_start \\ scrap_rate").to_excel(
            xl, sheet_name=sheet, startrow=2
        )

        r2 = len(offset_disp) + 5
        pd.DataFrame(
            {0: ["Same matrix as the dirtiest feasible 2050 grid EF (tCO2/kWh):"]}
        ).to_excel(xl, sheet_name=sheet, index=False, header=False, startrow=r2)
        ef_disp.rename_axis(index="h2_start \\ scrap_rate").to_excel(
            xl, sheet_name=sheet, startrow=r2 + 2
        )

    n_inf = int(req_ef.isna().sum().sum())
    print(f"Wrote {XLSX}")
    print(f"  {len(df)} runs ({len(solved)} solved); "
          f"{req_ef.size} combos, {n_inf} INFEASIBLE at every swept grid EF.")


if __name__ == "__main__":
    main()
