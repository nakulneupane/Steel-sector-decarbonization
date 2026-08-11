reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;
let n8_scrap_rate  := 0.06;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
let {t in T} n5_cost_NG[t] := 10;

let ng_h2_start_year := 2100;
let h2_peak_year     := 2105;
let avg_emi := 1e6;
let cap_add_common := 1e12;

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

s.t. base_f_bof     {t in T: ord(t) > 1}: f_bof[t] = 0.51;
s.t. base_f_eaf     {t in T: ord(t) > 1}: f_eaf[t] = 0.49;
s.t. base_scrap_eaf {t in T: ord(t) > 1}: steel_scrap_eaf[t] = 0;
s.t. base_cdri_split{t in T: ord(t) > 1}: coaldri_output[t] = 0.902 * dri_eaf_steel_out[t];
s.t. no_ccs{t in T}: total_ccs[t] = 0;
param base_scrap_share :=
    n3_metallic_bof * ( phi0_bof   * 0.51
                      + phi0_cdri  * 0.902 * 0.49
                      + phi0_ngdri * 0.098 * 0.49 );
s.t. base_scrap_total{t in T: ord(t) > 1}:
    bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t]
      = base_scrap_share * total_steel[t];

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t];

option solver gurobi;
option gurobi_options 'Threads=10 TimeLimit=300 mipgap=0.002';
# share pins are exactly collinear with meet_demand: tolerate the ~1e-16
# presolve rounding residual (see Baseline/main.mod)
option presolve_eps 1e-8;
drop emission_monotonic;

solve;

param fc{t in T} default 0;
param fn{t in T} default 0;
param gbf{t in T} default 0;
param gcd{t in T} default 0;
param gng{t in T} default 0;
param gsc{t in T} default 0;
let {t in T} fc[t] := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} fn[t] := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} gbf[t] := scope1_bf[t]
  + n9_grid_ef[t] * max(coke_power_in[t] + sinter_power_in[t] + bf_power_in[t]
        - (cdq_power_out[t] + sinterwaste_power_out[t] + bf_trt_out[t]), 0);
let {t in T} gcd[t] := scope1_cdri[t]
  + n9_grid_ef[t] * (coaldri_power_in[t] + fc[t]*eaf_power_in[t] + pellets_power_coaldri[t]);
let {t in T} gng[t] := scope1_ngdri[t]
  + n9_grid_ef[t] * (ngdri_power_in[t] + fn[t]*eaf_power_in[t] + pellets_power_ngdri[t]);
let {t in T} gsc[t] := scope1_scrapeaf[t] + n9_grid_ef[t] * scrap_eaf_power_in[t];

for {t in T} {
    printf "Baseline,%d,%s,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f,%.0f\n",
        t, solve_result,
        total_steel[t], steel_bof[t], coaldri_output[t], ngdri_output[t],
        h2dri_output[t], steel_scrap_eaf[t],
        scope1_emissions[t], scope2_emissions[t], total_ccs[t], total_emissions[t],
        0,
        bof_scrap_in[t], coaldri_scrap_in[t], ngdri_scrap_in[t],
        h2dri_scrap_in[t], scrap_eaf_scrap_in[t], n8_scrap_limit[t],
        total_cost[t],
        whr_power_generated[t],
        gbf[t], gcd[t], gng[t], gsc[t]
        >> "results/abatement_yearly.csv";
}
printf "ABATEMENT Baseline -> %s\n", solve_result;

include yreport.mod;
