# PROBABILISTIC Monte-Carlo 
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

let avg_emi := 1.8;
let cap_add_common := 15000000;                # Medium ramp
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

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * total_cost[t];

option solver gurobi;
option gurobi_options 'Threads=1 TimeLimit=120 outlev=0 mipgap=0.002';

solve;

param e_h2y{T} default 0;
let {t in T} e_h2y[t] :=
    scope1_h2dri[t]
  + n9_grid_ef[t] * ( h2dri_power_in[t] + pellets_power_h2dri[t]
      + (if dri_eaf_steel_out[t] > 0
         then h2dri_output[t]/dri_eaf_steel_out[t] else 0) * eaf_power_in[t] );
param red_h2 default 0;
let red_h2 := sum{t in T: h2dri_output[t] > 1e-6}
    max( h2dri_output[t]
         * ( (scope1_emissions[t] + scope2_emissions[t] - e_h2y[t])
             / (total_steel[t] - h2dri_output[t])
             - e_h2y[t]/h2dri_output[t] ), 0);
param red_ccs default 0;
let red_ccs := sum{t in T} total_ccs[t];


printf "MCROW,%s,%.4f,%.1f,%.1f,%.5f,%.4f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n",
    solve_result,
    (sum{t in T} discount_factor[t]*total_cost[t])
      / (sum{t in T} discount_factor[t]*total_steel[t]),          # lcop_pv
    (sum{t in T} total_emissions[t]) / 1e6,                       # cum_emis_Mt
    red_ccs / 1e6,                                                # cum_ccs_Mt
    (if red_h2 + red_ccs > 1 then red_h2/(red_h2+red_ccs) else 0),# d_index
    avg_emis_cap_total.dual,                                      # cap_dual
    (sum{t in T} discount_factor[t]*capex_cost[t]
     + sum{t in T} discount_factor[t]*ocapex_ccs[t]
       *(ccs_mult_bf*build_ccs_bf[t] + ccs_mult_cdri*build_ccs_cdri[t]
         + ccs_mult_ngdri*build_ccs_ngdri[t])) / 1e9,             # invest_npv_B
    (max{t in T} coking_coal_in[t]) / 1e6,                        # peak_ccoal_Mt
    (max{t in T} ngdri_ng_in[t]) / 1e6,                           # peak_ng_Mt
    total_steel[2050] / 1e6,                                      # steel2050_Mt
    steel_bof[2050] / 1e6,                                        # bof2050_Mt
    coaldri_output[2050] / 1e6,                                   # cdri2050_Mt
    ngdri_output[2050] / 1e6,                                     # ngdri2050_Mt
    h2dri_output[2050] / 1e6,                                     # h2dri2050_Mt
    steel_scrap_eaf[2050] / 1e6,                                  # scrapeaf2050_Mt
    bof_scrap_in[2050] / 1e6,                                     # scrap_bof2050_Mt
    coaldri_scrap_in[2050] / 1e6,                                 # scrap_cdri2050_Mt
    ngdri_scrap_in[2050] / 1e6,                                   # scrap_ngdri2050_Mt
    h2dri_scrap_in[2050] / 1e6,                                   # scrap_h2dri2050_Mt
    scrap_eaf_scrap_in[2050] / 1e6;                               # scrap_scrapeaf2050_Mt
printf "MCROW2,%.1f,%.1f,%.2f,%.4f\n",
    n8_scrap_limit[2050] / 1e6,                                   # scrap_limit2050_Mt
    (sum{t in T} (bof_scrap_in[t] + eaf_scrap_in[t]
                  + scrap_eaf_scrap_in[t])) / 1e6,                # scrap_use_cum_Mt
    total_cost[2050] / total_steel[2050],                         # cost2050_pt ($/t, snapshot)
    total_emissions[2050] / total_steel[2050];                    # emis2050_pt (tCO2/t)
