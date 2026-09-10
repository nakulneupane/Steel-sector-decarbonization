# =====================================================================
# Unified Section A design matrix: post-solve accounting.
#
# Included AFTER solve. This file only COMPUTES -- it writes nothing.
# run_matrix.py emits the printf with a per-worker shard path, because
# many workers append concurrently and an AMPL `>>` to one shared file
# would interleave rows.
#
# Column order is defined once, in run_matrix.py:REPORT_COLUMNS. Keep the
# two in step.
#
# Union of the six original studies' report.mod files, plus:
#   - grid_ef_2050 / tariff_2050  : read back from the model so every row
#     PROVES the swept grid axis actually propagated (see the warm-reuse
#     hazard in run_matrix.py -- a frozen n9_grid_ef_end would show up here
#     as a constant column while the requested target still varied).
#   - ccoal_bind_yrs / ng_bind_yrs : years in which the availability cap is
#     binding. These are the companions to import_bill: a LOW bill with a
#     BINDING cap is forced scarcity, not a good outcome. import_bill itself
#     is left exactly as the original studies defined it.
# =====================================================================

param ng_domestic    := 0.5 * 5348550;                     # flat domestic NG to steel, t/yr
param ccoal_domestic{t in T} := 6000000 * 1.075^(t-2025);  # domestic coking coal, +7.5%/yr

param m_cum_ccoal_bill;
param m_cum_ng_bill;
param m_cum_ng_import;
param m_cum_ccoal_import;
param m_ccoal_bind;
param m_ng_bind;

let m_cum_ccoal_bill   := sum{t in T} max(0, coking_coal_in[t] - ccoal_domestic[t]) * ng_cost_ccoal;
let m_cum_ng_bill      := sum{t in T} max(0, ngdri_ng_in[t] - ng_domestic) * n5_cost_NG[t] * 50;
let m_cum_ng_import    := sum{t in T} max(0, ngdri_ng_in[t] - ng_domestic);
let m_cum_ccoal_import := sum{t in T} max(0, coking_coal_in[t] - ccoal_domestic[t]);

# Binding = usage within 0.1% of the cap. ccoal_cap defaults to 1e12 when
# unbounded, so this reads 0 there, which is the honest answer.
let m_ccoal_bind := sum{t in T} (if coking_coal_in[t] >= 0.999 * ccoal_cap[t] then 1 else 0);
let m_ng_bind    := sum{t in T} (if ngdri_ng_in[t]   >= 0.999 * n5_ng_cap[t]  then 1 else 0);

# --- H2 route emission credit (identical in all six original reports) ---
param m_e_h2_2050;
param m_red_h2_2050;
let m_e_h2_2050 :=
    scope1_h2dri[2050]
  + n9_grid_ef[2050] * ( h2dri_power_in[2050] + pellets_power_h2dri[2050]
      + (if dri_eaf_steel_out[2050] > 0
         then h2dri_output[2050]/dri_eaf_steel_out[2050] else 0) * eaf_power_in[2050] );
let m_red_h2_2050 :=
    if h2dri_output[2050] > 1 and total_steel[2050] > h2dri_output[2050]
    then h2dri_output[2050]
         * (scope1_emissions[2050] + scope2_emissions[2050] - m_e_h2_2050)
         / (total_steel[2050] - h2dri_output[2050])
         - m_e_h2_2050
    else 0;

# --- cost / emissions aggregates ---
param m_lcop;
param m_cum_co2;
param m_avg_emis;
let m_lcop :=
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0);
let m_cum_co2  := sum{t in T} total_emissions[t];
let m_avg_emis :=
    (if (sum{t in T} total_steel[t]) > 0
        then (sum{t in T} total_emissions[t]) / (sum{t in T} total_steel[t]) else 0);

# --- CCS / WHR accounting (from the whr study) ---
param m_pv_captured;
param m_eff_capture_cost;
param m_cum_captured;
param m_boiler_steam_sh;
let m_pv_captured := sum{t in T} discount_factor[t]*total_ccs[t];
let m_eff_capture_cost :=
    (sum{t in T} discount_factor[t]*
        ( cost_ccs[t] + whr_gas_to_steam[t]*277.78*n9_eta*ng_cost_power[t] ))
    / max(m_pv_captured, 1);
let m_cum_captured := sum{t in T} total_ccs[t];
let m_boiler_steam_sh :=
    (sum{t in T} ccs_steam_boiler[t])
    / max(sum{t in T} (ccs_steam_whr[t] + ccs_steam_boiler[t]), 1);

# --- 2050 route shares ---
param m_sh_bof;
param m_sh_cdri;
param m_sh_ngdri;
param m_sh_h2;
param m_sh_scrap;
let m_sh_bof   := if total_steel[2050] > 0 then steel_bof[2050]/total_steel[2050] else 0;
let m_sh_cdri  := if total_steel[2050] > 0 then coaldri_output[2050]/total_steel[2050] else 0;
let m_sh_ngdri := if total_steel[2050] > 0 then ngdri_output[2050]/total_steel[2050] else 0;
let m_sh_h2    := if total_steel[2050] > 0 then h2dri_output[2050]/total_steel[2050] else 0;
let m_sh_scrap := if total_steel[2050] > 0 then steel_scrap_eaf[2050]/total_steel[2050] else 0;

# --- scrap headroom (from the scrap study) ---
param m_scrap_use_2050;
let m_scrap_use_2050 := bof_scrap_in[2050] + eaf_scrap_in[2050] + scrap_eaf_scrap_in[2050];
