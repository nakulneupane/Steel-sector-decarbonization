"""
Reads  results/abatement_yearly.csv (Baseline + six scenarios, yearly rows)
Writes results/abatement_summary.xlsx:
 cumulative CO2 emitted (Gt), abatement vs the
     common Baseline split into H2 / CCS / scrap / NG / grid / route-mix slices
     (Gt), PV LCOP, Delta PV cost, average abatement cost ($/tCO2).

Wedge conventions (cumulative). Every low-carbon lever is credited for
displacing a BASELINE-AVERAGE tonne :
  CCS   = CO2 captured (exact).
  H2    = H2 steel x (sigma_base - H2 route gross intensity), yearly summed.
          Baseline H2 = 0, so full output = increment.
  NG    = NG-DRI INCREMENT over Baseline x (sigma_base - NG-DRI gross intensity),
          i_ng recovered from the dumped gross_ngdri. The coal->gas fuel switch,
          named out of the old "others".
  SCRAP = scrap INCREMENT/1.1 x (sigma_base - scrap-processing intensity), where
          scrap processing ~ scrap-EAF coefficients (0.0708 tCO2/tCS scope-1
          + 785 kWh x grid EF at theta_grid = 0.5).
  GRID  = ADDITIONAL grid abatement vs the Baseline: (scenario grid power -
          Baseline grid power) x (2025 EF - EF_t). The Baseline's own draw
          benefits both runs equally and cancels, so the Baseline bar has NO
          grid slice and every bar stacks to the Baseline's ACTUAL cumulative
          emissions (same convention as the Transition study).
  ROUTE MIX = scrap ALLOCATION (the scrap-EAF route term minus the
          increment-based scrap wedge: reallocating scrap from dilute BOF/DRI
          blends into the dedicated near-zero route), coal-DRI & BF-BOF SURVIVORS 
          (surviving coal-DRI is 1 tCO2/t DIRTIER than the baseline average: negative), baseline-level NG,
          CCS energy & unattributed (compression power + boiler NG, plus
          scope-1/2 items in no route gross - EAF electrodes, power-balance
          residuals; the Baseline row's value shows the pure-unattributed
          scale), and the grid-overlap offset (the grid slice re-attributes
          benefit already embedded in route intensities).
          Identity: emitted + H2 + CCS + NG + scrap + grid + route mix = Baseline.
Abatement cost = (PV cost scenario - PV cost Baseline) / cumulative abatement.
"""

from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
CSV = HERE / "results" / "abatement_yearly.csv"
XLSX = HERE / "results" / "abatement_summary.xlsx"

ORDER = ["Baseline", "EF1.6", "EF1.8", "S4", "S8", "RL", "RH"]
DISC = 0.06
CHARGE = 1.1
# grid EF path at theta_grid = 0.5 (start 0.000886; end = 0.0006+0.5*(0.0003-0.0006))
def grid_ef(year):
    return 0.000886 + (0.00045 - 0.000886) * (year - 2025) / 25


def scrap_proc_intensity(year):
    """tCO2 per tCS of scrap processing (~scrap-EAF coefficients)."""
    return 0.0708 + 785 * grid_ef(year)


def main() -> None:
    df = pd.read_csv(CSV)
    if df.empty:
        raise SystemExit(f"{CSV} has no data rows -- run abatement.bat first.")
    df["scrap_use"] = (df["bof_scrap"] + df["cdri_scrap"] + df["ngdri_scrap"]
                       + df["h2dri_scrap"] + df["scrapeaf_scrap"])
    b = df[df["run"] == "Baseline"].set_index("year")
    dfac = pd.Series({y: 1 / (1 + DISC) ** (y - 2025) for y in b.index})
    # reference = the COMMON Baseline's AVERAGE gross intensity, per year; every
    # low-carbon lever is credited for displacing a baseline-average tonne
    # (sigma_base parity with the Transition study). Contrast the old sigma_non
    # same-run reference, which under-credited H2/scrap and inflated "others".
    sig_base = b["total_emissions"] / b["total_steel"]

    rows = []
    decomp_rows = []
    plot_rows = []
    for run in ORDER:
        s = df[df["run"] == run].set_index("year").sort_index()
        if s.empty:
            continue
        emitted = s["total_emissions"].sum()
        abated = b["total_emissions"].sum() - emitted
        ccs = s["ccs"].sum()
        h2s = s["h2dri"]
        with np.errstate(divide="ignore", invalid="ignore"):
            sig_h2 = (s["e_h2"] / h2s.where(h2s > 0)).fillna(0)
            sig_ng = (s["gross_ngdri"] / s["ngdri"].where(s["ngdri"] > 0)).fillna(0)
        w_h2 = float(((sig_base - sig_h2) * h2s).clip(lower=0).sum())
        w_ng = float(((sig_base - sig_ng) * (s["ngdri"] - b["ngdri"])).sum())
        d_scrap = (s["scrap_use"] - b["scrap_use"]) / CHARGE
        sig_scrap = pd.Series({y: scrap_proc_intensity(y) for y in s.index})
        w_scrap = float(((sig_base - sig_scrap) * d_scrap).sum())
        ef_series = pd.Series({y: grid_ef(y) for y in s.index})
        power_s = s["scope2"] / ef_series          # recover grid power draw
        power_b = b["scope2"] / ef_series
        w_grid = float(((power_s - power_b) * (grid_ef(2025) - ef_series)).sum())
        w_other = abated - ccs - w_h2 - w_ng - w_scrap - w_grid
        c_bf = float((s["steel_bof"] * sig_base - s["gross_bf"]).sum())
        c_cd = float((s["coaldri"] * sig_base - s["gross_cdri"]).sum())
        c_ngb = float((b["ngdri"] * (sig_base - sig_ng)).sum())
        c_scr_route = float((s["scrap_eaf"] * sig_base - s["gross_scrapeaf"]).sum())
        c_scr_xt = c_scr_route - w_scrap          
        ccs_en = float(((s["scope1"] + s["scope2"])
                        - (s["gross_bf"] + s["gross_cdri"] + s["gross_ngdri"]
                           + s["gross_scrapeaf"] + s["e_h2"])).sum())
        decomp_rows.append({
            "Scenario": run,
            "BF-BOF survivors (Gt)": round(c_bf / 1e9, 3),
            "Coal-DRI survivors (Gt)": round(c_cd / 1e9, 3),
            "Baseline-level NG (Gt)": round(c_ngb / 1e9, 3),
            "Scrap allocation (Gt)": round(c_scr_xt / 1e9, 3),
            "CCS energy & unattributed (Gt)": round(-ccs_en / 1e9, 3),
            "Grid overlap offset (Gt)": round(-w_grid / 1e9, 3),
            "sum (= wedge route mix)": round((c_bf + c_cd + c_ngb + c_scr_xt
                                              - ccs_en - w_grid) / 1e9, 3),
        })
        lcop = float((s["total_cost"] * dfac).sum() / (s["total_steel"] * dfac).sum())
        dcost = float(((s["total_cost"] - b["total_cost"]) * dfac).sum())
        rows.append({
            "Scenario": run,
            "solve_result": s["solve_result"].iloc[0],
            "Cumulative CO2 emitted (Gt)": round(emitted / 1e9, 3),
            "Abatement vs Baseline (Gt)": round(abated / 1e9, 3),
            "wedge H2 (Gt)": round(w_h2 / 1e9, 3),
            "wedge CCS (Gt)": round(ccs / 1e9, 3),
            "wedge scrap (Gt)": round(w_scrap / 1e9, 3),
            "wedge NG (Gt)": round(w_ng / 1e9, 3),
            "wedge grid (Gt)": round(w_grid / 1e9, 3),
            "wedge route mix (Gt)": round(w_other / 1e9, 3),
            "LCOP (PV $/t)": round(lcop, 2),
            "Delta PV cost ($B)": round(dcost / 1e9, 2),
            "Abatement cost ($/tCO2)": (round(dcost / abated, 2) if abated > 1 else None),
        })

        plot_rows.append({
            "Scenario": run,
            "CO2 emitted (Gt)": round(emitted / 1e9, 4),
            "H2 (Gt)": round(w_h2 / 1e9, 4),
            "CCS (Gt)": round(ccs / 1e9, 4),
            "Scrap (Gt)": round(w_scrap / 1e9, 4),
            "NG-DRI (Gt)": round(w_ng / 1e9, 4),
            "Grid (Gt)": round(w_grid / 1e9, 4),
            "Route mix (Gt)": round(w_other / 1e9, 4),
            "Abatement cost ($/tCO2)": (round(dcost / abated, 2)
                                        if abated > 1 else None),
        })
    summary = pd.DataFrame(rows)

    y = df.copy()
    y["blend_bof"] = (y["bof_scrap"] / (CHARGE * y["steel_bof"])).round(4)
    y["blend_cdri"] = (y["cdri_scrap"] / (CHARGE * y["coaldri"])).round(4)
    y["blend_ngdri"] = (y["ngdri_scrap"] / (CHARGE * y["ngdri"])).round(4)
    y["scrap_use_Mt"] = (y["scrap_use"] / 1e6).round(3)

    with pd.ExcelWriter(XLSX, engine="openpyxl") as xl:
        summary.to_excel(xl, sheet_name="summary", index=False)
        pd.DataFrame(plot_rows).to_excel(xl, sheet_name="plot_data", index=False)
        pd.DataFrame(decomp_rows).to_excel(xl, sheet_name="route_mix_decomp", index=False)
        y.to_excel(xl, sheet_name="yearly", index=False)

    print(f"Wrote {XLSX}")
    print(summary.drop(columns="solve_result").to_string(index=False))


if __name__ == "__main__":
    main()

