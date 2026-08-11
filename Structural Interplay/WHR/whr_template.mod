# ============================================================================
# WHR-STEAM VALUE sweep template.
# Question: across CCS+grid ecosystem maturity (ONE theta applied jointly to
# theta_ccs and theta_grid: capture-plant learning + grid EF/tariff), what is
# the EFFECTIVE CAPTURE COST with the WHR steam pool integrated vs boiler-only
# regen steam -- i.e. what is waste-heat integration worth to CCS?
#
# Effective capture cost (PV, $/tCO2) counts everything capture causes:
#   [ PV( cost_ccs = capex+FOM+compression power+solvent+T&S+boiler fuel )
#     + PV( foregone WHR power value = gas diverted to steam x 277.78 x n9_eta
#           x tariff -- the opportunity cost the pool allocation hides ) ]
#   / PV( CO2 captured ).
# In boiler-only mode the toggle whr_ccs_integration = 0 forces all regen
# steam through the gas boiler (o_waste_heat.mod, this copy).
#
# SELF-CONTAINED: uses the model copy in THIS folder (Plots/WHR); whr.bat runs
# AMPL here, substituting THETAVAL (joint theta_ccs = theta_grid), WHRVAL
# (1 integrated / 0 boiler-only) and MODELABEL. Fixed backdrop:
#   theta_tech 0.5, H2 start 2030 (peak 2035), scrap growth 6%, MEDIUM ramp
#   (cap_add_common 15 Mt, h2_ref_cap 6 Mt), NG 10 $/MMBtu, avg_emi 1.8.
# ============================================================================
reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

# --- fixed study backdrop ---
let theta_tech := 0.5;
let ng_h2_start_year := 2030;
let h2_peak_year     := 2035;
let cap_add_common   := 15000000;    # Medium ramp
let h2_ref_cap       := 6000000;     # Medium H2 envelope
let n8_scrap_rate    := 0.06;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
let {t in T} n5_cost_NG[t] := 10;

# --- sweep tokens (substituted by whr.bat) ---
let theta_ccs  := THETAVAL;          # joint CCS+grid ecosystem maturity
let theta_grid := THETAVAL;
# (whr_ccs_integration is declared in modules/o_waste_heat.mod, so its let
#  comes AFTER the module includes below.)

include modules/a_coke.mod;
include modules/b_sinter.mod;
include modules/c_pellets_bf.mod;
include modules/d_blast_furnace.mod;
include modules/e_bof.mod;
include modules/f_pellets_coaldri.mod;
include modules/g_pellets_ngdri.mod;
include modules/h_pellets_h2dri.mod;
include modules/i_dri_coal.mod;
include modules/j_dri_ng.mod;
include modules/k_dri_h2.mod;
include modules/l_eaf_dri.mod;
include modules/m_scrap_eaf.mod;
include modules/n_steel_balance.mod;
include modules/q_carbon_capture.mod;
include modules/o_waste_heat.mod;
include modules/p_power_balance.mod;
include modules/v_capacity.mod;
include modules/r_cost.mod;
include modules/s_emissions.mod;
include modules/t_additional_constraints.mod;

# steam-sourcing mode (param declared in o_waste_heat.mod above):
# 1 = WHR steam pool integrated, 0 = boiler-only regen steam
let whr_ccs_integration := WHRVAL;

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t];

option solver gurobi;
option gurobi_options 'Threads=10 TimeLimit=300 mipgap=0.002';

solve;

# --- post-solve metrics ---
param pv_captured;      # PV-weighted captured CO2 (t)
param eff_capture_cost; # $/tCO2, incl. foregone WHR power value
param cum_captured;     # plain cumulative captured CO2 (t)
param boiler_steam_sh;  # share of regen steam that came from the boiler
let pv_captured := sum{t in T} discount_factor[t]*total_ccs[t];
let eff_capture_cost :=
    (sum{t in T} discount_factor[t]*
        ( cost_ccs[t]
        + whr_gas_to_steam[t]*277.78*n9_eta*ng_cost_power[t] ))
    / max(pv_captured, 1);
let cum_captured := sum{t in T} total_ccs[t];
let boiler_steam_sh :=
    (sum{t in T} ccs_steam_boiler[t])
    / max(sum{t in T} (ccs_steam_whr[t] + ccs_steam_boiler[t]), 1);

printf "%.2f,%s,%.0f,%s,%.2f,%.0f,%.0f,%.4f,%.2f\n",
    theta_ccs,
    "MODELABEL",
    whr_ccs_integration,
    solve_result,
    eff_capture_cost,
    cum_captured,
    total_ccs[2050],
    boiler_steam_sh,
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0)
    >> "results/whr_summary.csv";
printf "WHRRESULT theta=%.2f mode=%s -> %s (eff cost %.2f)\n",
    theta_ccs, "MODELABEL", solve_result, eff_capture_cost;

include yreport.mod;
