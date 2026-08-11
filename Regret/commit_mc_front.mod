
reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

let ng_h2_start_year := H2YEARVAL;
let h2_peak_year := ng_h2_start_year + 5;

let theta_tech := THETATECHVAL;
let theta_grid := THETAGCVAL;
let theta_ccs  := THETAGCVAL;
let n8_scrap_rate := SCRAPRATEVAL;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
let {t in T} n5_cost_NG[t] := NGPRICEVAL;
let avg_emi := AVGEMIVAL;
let cap_add_common := 15000000;
let h2_ref_cap     := 6000000;

include CCOALFILE;
include NGAVAILFILE;

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

drop min_util_bof;
drop min_util_cdri;
drop min_util_ngdri;
drop min_util_h2dri;
drop min_util_scrap;
drop emission_monotonic;
drop avg_emis_cap_total;
param IMPORT_P := 20000;
var steel_import{T} >= 0;
drop meet_demand;
s.t. meet_demand_elastic{t in T}:
    total_steel[t] + steel_import[t]
      = base_demand * (1 + growth_rate)^(ord(t) - 1);
param PEN := 5000;
var emis_slack >= 0;
param carbon_budget := avg_emi *
    sum{t in T} base_demand * (1 + growth_rate)^(ord(t) - 1);
s.t. cap_elastic:
    (sum{t in T} total_emissions[t]) <= carbon_budget + emis_slack;

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t]
    + IMPORT_P * (sum{t in T} steel_import[t])
    + PEN * emis_slack;

option solver gurobi;
option gurobi_options 'Threads=1 TimeLimit=300 outlev=0 mipgap=0.002';

solve;

printf "FRONTROW,%s,%.4f,%.5f,%.2f,%.1f\n",
    solve_result,
    (sum{t in T} discount_factor[t]*total_cost[t])
      / (sum{t in T} discount_factor[t]*total_steel[t]),
    (sum{t in T} total_emissions[t]) / (sum{t in T} total_steel[t]),
    emis_slack / 1e6,
    (sum{t in T} total_ccs[t]) / 1e6;
