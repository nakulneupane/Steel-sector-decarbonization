
reset;
set T ordered := 2025..2050;

include definitions.mod;
include variables.mod;
include parameters.mod;

# H2 debut 
let ng_h2_start_year := H2READYVAL;
let h2_peak_year := ng_h2_start_year + 5;

let theta_tech := 0.5;
let theta_grid := 0.5;
let theta_ccs  := 0.5;
let n8_scrap_rate := 0.06;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] := n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);
let {t in T} n5_cost_NG[t] := 10;
let avg_emi := 1.8;
let cap_add_common := 15000000;
let h2_ref_cap     := 6000000;

include scenarios/ccoal_mid.mod;
include scenarios/ng_shock.mod;

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

# committed plan
param committed_build_bof        {T} default 0;
param committed_build_cdri       {T} default 0;
param committed_build_ngdri      {T} default 0;
param committed_build_h2dri      {T} default 0;
param committed_build_scrap      {T} default 0;
param committed_build_scrapchain {T} default 0;
param committed_build_coalchain  {T} default 0;
param committed_build_ngchain    {T} default 0;
param committed_build_h2elec     {T} default 0;
param committed_build_h2re       {T} default 0;
param committed_build_ccs_bf     {T} default 0;
param committed_build_ccs_cdri   {T} default 0;
param committed_build_ccs_ngdri  {T} default 0;
include PLANFILE;

s.t. commit_bof   {t in T: t < TSTARVAL}: build_bof[t]   >= committed_build_bof[t];
s.t. commit_cdri  {t in T: t < TSTARVAL}: build_cdri[t]  >= committed_build_cdri[t];
s.t. commit_ngdri {t in T: t < TSTARVAL}: build_ngdri[t] >= committed_build_ngdri[t];
s.t. commit_h2dri {t in T: t < TSTARVAL}: build_h2dri[t] >= committed_build_h2dri[t];
s.t. commit_scrap {t in T: t < TSTARVAL}: build_scrap[t] >= committed_build_scrap[t];
s.t. commit_scrapchain{t in T: t < TSTARVAL}: build_scrapchain[t] >= committed_build_scrapchain[t];
s.t. commit_coalchain {t in T: t < TSTARVAL}: build_coalchain[t]  >= committed_build_coalchain[t];
s.t. commit_ngchain   {t in T: t < TSTARVAL}: build_ngchain[t]    >= committed_build_ngchain[t];
s.t. commit_ccs_bf    {t in T: t < TSTARVAL}: build_ccs_bf[t]     >= committed_build_ccs_bf[t];
s.t. commit_ccs_cdri  {t in T: t < TSTARVAL}: build_ccs_cdri[t]   >= committed_build_ccs_cdri[t];
s.t. commit_ccs_ngdri {t in T: t < TSTARVAL}: build_ccs_ngdri[t]  >= committed_build_ccs_ngdri[t];

# H2-supply commitment is FINANCIAL, not physical 
# The signed capex is paid on at least the committed units
# (sunk if unbuilt), charged in the objective AND the reported PV cost.
var pay_h2elec_extra{T} >= 0;
var pay_h2re_extra{T} >= 0;
s.t. pay_h2elec_def{t in T: t < TSTARVAL}:
    pay_h2elec_extra[t] >= committed_build_h2elec[t] - build_h2elec[t];
s.t. pay_h2re_def{t in T: t < TSTARVAL}:
    pay_h2re_extra[t] >= committed_build_h2re[t] - build_h2re[t];

# Min-utilisation floors dropped 
drop min_util_bof;
drop min_util_cdri;
drop min_util_ngdri;
drop min_util_h2dri;
drop min_util_scrap;

# Elastic demand: imports at a premium 
param IMPORT_P := 20000;
param IMPORT_REPORT := 650;
var steel_import{T} >= 0;
drop meet_demand;
s.t. meet_demand_elastic{t in T}:
    total_steel[t] + steel_import[t]
      = base_demand * (1 + growth_rate)^(ord(t) - 1);

# Elastic cumulative cap (monotonic dropped)
drop emission_monotonic;
drop avg_emis_cap_total;
param PEN := 5000;
var emis_slack >= 0;
param carbon_budget := avg_emi *
    sum{t in T} base_demand * (1 + growth_rate)^(ord(t) - 1);   # 14.003 Gt
s.t. cap_elastic:
    (sum{t in T} total_emissions[t]) <= carbon_budget + emis_slack;

param discount_factor{t in T} :=
    1 / (1 + real_discount_rate)^(ord(t) - 1);

minimize obj:
    sum {t in T} discount_factor[t] * (total_cost[t]
        + ocapex_h2elec[t]*pay_h2elec_extra[t]
        + ocapex_h2re[t]*pay_h2re_extra[t])
    + IMPORT_P * (sum{t in T} steel_import[t])
    + PEN * emis_slack;

option solver gurobi;
option gurobi_options 'Threads=1 TimeLimit=300 outlev=0 mipgap=0.002';
option presolve_eps 1e-5;

solve;

param com_u{c in 1..13} default 0;
param com_x{c in 1..13} default 0;
param use_u{c in 1..13} default 0;
let com_u[1] := sum{t in T: t < TSTARVAL} committed_build_bof[t];
let com_u[2] := sum{t in T: t < TSTARVAL} committed_build_cdri[t];
let com_u[3] := sum{t in T: t < TSTARVAL} committed_build_ngdri[t];
let com_u[4] := sum{t in T: t < TSTARVAL} committed_build_h2dri[t];
let com_u[5] := sum{t in T: t < TSTARVAL} committed_build_scrap[t];
let com_u[6] := sum{t in T: t < TSTARVAL} committed_build_scrapchain[t];
let com_u[7] := sum{t in T: t < TSTARVAL} committed_build_coalchain[t];
let com_u[8] := sum{t in T: t < TSTARVAL} committed_build_ngchain[t];
let com_u[9] := sum{t in T: t < TSTARVAL} committed_build_h2elec[t];
let com_u[10]:= sum{t in T: t < TSTARVAL} committed_build_h2re[t];
let com_u[11]:= sum{t in T: t < TSTARVAL} committed_build_ccs_bf[t];
let com_u[12]:= sum{t in T: t < TSTARVAL} committed_build_ccs_cdri[t];
let com_u[13]:= sum{t in T: t < TSTARVAL} committed_build_ccs_ngdri[t];
let com_x[1] := sum{t in T: t < TSTARVAL} ocapex_bof   * committed_build_bof[t];
let com_x[2] := sum{t in T: t < TSTARVAL} ocapex_cdri  * committed_build_cdri[t];
let com_x[3] := sum{t in T: t < TSTARVAL} ocapex_ngdri * committed_build_ngdri[t];
let com_x[4] := sum{t in T: t < TSTARVAL} ocapex_h2dri[t] * committed_build_h2dri[t];
let com_x[5] := sum{t in T: t < TSTARVAL} ocapex_scrap * committed_build_scrap[t];
let com_x[6] := sum{t in T: t < TSTARVAL} ocapex_scrapchain * committed_build_scrapchain[t];
let com_x[7] := sum{t in T: t < TSTARVAL} ocapex_coalchain  * committed_build_coalchain[t];
let com_x[8] := sum{t in T: t < TSTARVAL} ocapex_ngchain    * committed_build_ngchain[t];
let com_x[9] := sum{t in T: t < TSTARVAL} ocapex_h2elec[t]  * committed_build_h2elec[t];
let com_x[10]:= sum{t in T: t < TSTARVAL} ocapex_h2re[t]    * committed_build_h2re[t];
let com_x[11]:= sum{t in T: t < TSTARVAL} ocapex_ccs[t]*ccs_mult_bf   * committed_build_ccs_bf[t];
let com_x[12]:= sum{t in T: t < TSTARVAL} ocapex_ccs[t]*ccs_mult_cdri * committed_build_ccs_cdri[t];
let com_x[13]:= sum{t in T: t < TSTARVAL} ocapex_ccs[t]*ccs_mult_ngdri* committed_build_ccs_ngdri[t];
let use_u[1] := max{t in T} (steel_bof[t]       - legacy_bof[t]);
let use_u[2] := max{t in T} (coaldri_output[t]  - legacy_cdri[t]);
let use_u[3] := max{t in T} (ngdri_output[t]    - legacy_ngdri[t]);
let use_u[4] := max{t in T} (h2dri_output[t]    - legacy_h2dri[t]);
let use_u[5] := max{t in T} (steel_scrap_eaf[t] - legacy_scrap[t]);
let use_u[6] := max{t in T} (bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t])
                - (bof_scrap_in[2025] + eaf_scrap_in[2025] + scrap_eaf_scrap_in[2025]);
let use_u[7] := 0;
let use_u[8] := 0;
let use_u[9] := max{t in T} (h2dri_h2_in[t] + bf_h2_in[t]);
let use_u[10]:= h2_kw_per_t * use_u[9];
let use_u[11]:= max{t in T} ccs_bf[t];
let use_u[12]:= max{t in T} ccs_cdri[t];
let use_u[13]:= max{t in T} ccs_ngdri[t];
param idle{c in 1..13} := if com_u[c] > 1e-3
                          then max(0, com_u[c] - max(0, use_u[c])) / com_u[c]
                          else 0;
param stranded{c in 1..13} := com_x[c] * idle[c];

printf "REGROW,%s,%.3f,%.4f,%.2f,%.2f,%.1f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,%.5f\n",
    solve_result,
    (sum{t in T} discount_factor[t]
        *(total_cost[t] + ocapex_h2elec[t]*pay_h2elec_extra[t]
          + ocapex_h2re[t]*pay_h2re_extra[t]
          + IMPORT_REPORT*steel_import[t])) / 1e9,
    (sum{t in T} discount_factor[t]
        *(total_cost[t] + ocapex_h2elec[t]*pay_h2elec_extra[t]
          + ocapex_h2re[t]*pay_h2re_extra[t]
          + IMPORT_REPORT*steel_import[t]))
      / (sum{t in T} discount_factor[t]*(total_steel[t]+steel_import[t])),
    emis_slack / 1e6,
    (sum{t in T} steel_import[t]) / 1e6,
    (sum{t in T} total_ccs[t]) / 1e6,
    (sum{c in 1..13} com_x[c]) / 1e9,
    (sum{c in 1..13} stranded[c]) / 1e9,
    (stranded[1]+stranded[2]+stranded[3]+stranded[5]) / 1e9,
    stranded[4] / 1e9,
    (stranded[9]+stranded[10]) / 1e9,
    (stranded[11]+stranded[12]+stranded[13]) / 1e9,
    stranded[6] / 1e9,
    (stranded[7]+stranded[8]) / 1e9,
    (sum{t in T} total_emissions[t]) / (sum{t in T} total_steel[t]);

printf "# executed window from TSTARVAL (H2 gate H2READYVAL)\n" > "DUMPOUT";
for {t in T: t >= TSTARVAL and t <= TSTARVAL + 9} {
    printf "let committed_build_bof[%d] := %.17g;\n", t, build_bof[t] >> "DUMPOUT";
    printf "let committed_build_cdri[%d] := %.17g;\n", t, build_cdri[t] >> "DUMPOUT";
    printf "let committed_build_ngdri[%d] := %.17g;\n", t, build_ngdri[t] >> "DUMPOUT";
    printf "let committed_build_h2dri[%d] := %.17g;\n", t, build_h2dri[t] >> "DUMPOUT";
    printf "let committed_build_scrap[%d] := %.17g;\n", t, build_scrap[t] >> "DUMPOUT";
    printf "let committed_build_scrapchain[%d] := %.17g;\n", t, build_scrapchain[t] >> "DUMPOUT";
    printf "let committed_build_coalchain[%d] := %.17g;\n", t, build_coalchain[t] >> "DUMPOUT";
    printf "let committed_build_ngchain[%d] := %.17g;\n", t, build_ngchain[t] >> "DUMPOUT";
    printf "let committed_build_h2elec[%d] := %.17g;\n", t, build_h2elec[t] >> "DUMPOUT";
    printf "let committed_build_h2re[%d] := %.17g;\n", t, build_h2re[t] >> "DUMPOUT";
    printf "let committed_build_ccs_bf[%d] := %.17g;\n", t, build_ccs_bf[t] >> "DUMPOUT";
    printf "let committed_build_ccs_cdri[%d] := %.17g;\n", t, build_ccs_cdri[t] >> "DUMPOUT";
    printf "let committed_build_ccs_ngdri[%d] := %.17g;\n", t, build_ccs_ngdri[t] >> "DUMPOUT";
}
