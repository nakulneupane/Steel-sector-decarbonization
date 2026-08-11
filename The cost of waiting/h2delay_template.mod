reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

# sweep tokens 
let cap_add_common   := RAMPVAL;    # common route build slab, t-steel/yr
let h2_ref_cap       := H2REFVAL;   # H2 envelope scale, t-H2/yr (peak = 0.25x)
let avg_emi          := EFVAL;      # cumulative-average emission cap, tCO2/tCS
let ng_h2_start_year := H2YRVAL;    # green-H2 debut year

let h2_peak_year := ng_h2_start_year + 5;   # Gaussian buildout crest follows debut

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

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t];

option solver gurobi;
option gurobi_options 'Threads=10 TimeLimit=300 mipgap=0.002';

solve;

param e_h2_2050;      # H2 route gross emissions in 2050 (scope1 + its scope2 share)
param red_h2_2050;    # tCO2 avoided by H2-DRI in 2050
let e_h2_2050 :=
    scope1_h2dri[2050]
  + n9_grid_ef[2050] * ( h2dri_power_in[2050] + pellets_power_h2dri[2050]
      + (if dri_eaf_steel_out[2050] > 0
         then h2dri_output[2050]/dri_eaf_steel_out[2050] else 0) * eaf_power_in[2050] );
let red_h2_2050 :=
    if h2dri_output[2050] > 1 and total_steel[2050] > h2dri_output[2050]
    then h2dri_output[2050]
         * (scope1_emissions[2050] + scope2_emissions[2050] - e_h2_2050)
         / (total_steel[2050] - h2dri_output[2050])
         - e_h2_2050
    else 0;

printf "%.2f,%s,%.0f,%.0f,%d,%s,%.0f,%.0f,%.2f,%.0f\n",
    avg_emi,
    "RAMPLABEL",
    cap_add_common,
    h2_ref_cap,
    ng_h2_start_year,
    solve_result,
    cap_h2dri[2050],
    total_ccs[2050],
    (if (sum{t in T} discount_factor[t]*total_steel[t]) > 0
        then (sum{t in T} discount_factor[t]*total_cost[t])
           / (sum{t in T} discount_factor[t]*total_steel[t]) else 0),
    red_h2_2050
    >> "Plots/H2_Delay/results/h2delay_summary.csv";
printf "H2DELAYRESULT EF=%.2f ramp=%s h2start=%d -> %s\n",
    avg_emi, "RAMPLABEL", ng_h2_start_year, solve_result;

include yreport.mod;
