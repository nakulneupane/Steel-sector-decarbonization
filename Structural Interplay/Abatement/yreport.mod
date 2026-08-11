param f_cdri{t in T} default 0;
param f_ngdri{t in T} default 0;
let {t in T} f_cdri[t]  := if dri_eaf_steel_out[t] > 1e-6 then coaldri_output[t]/dri_eaf_steel_out[t] else 0;
let {t in T} f_ngdri[t] := if dri_eaf_steel_out[t] > 1e-6 then ngdri_output[t]/dri_eaf_steel_out[t] else 0;

printf "\nAVERAGE STEEL PRODUCTION COST (2025â€“2050): %.2f $/ton\n",
    if sum{t in T} total_steel[t] > 0 then
        ( sum{t in T} discount_factor[t] * total_cost[t] )
      / ( sum{t in T} discount_factor[t] * total_steel[t] )
    else 0;
       
printf "2050: Cost = %.3f $/t CS, Emissions = %.3f tCO2/t CS\n",
    if total_steel[2050] > 0 then
        total_cost[2050] / total_steel[2050]
    else 0,
    if total_steel[2050] > 0 then
        total_emissions[2050] / total_steel[2050]
    else 0;      
       
printf "\nCO2 CAPTURED PER TON STEEL OVERALL (2025â€“2050): %.3f\n",
       if (sum{t in T} total_steel[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} total_steel[t] )
       else 0;

printf "\nLCOH BREAKDOWN ($/kg and share; electricity = RE + firming)\n";
printf "%-6s %-10s %-10s %-10s %-10s %-8s   %-12s %-12s\n",
       "YEAR", "Electrolyz", "RE", "Firming", "Other", "LCOH", "elec share", "elz share";
for {t in T: t = 2025 or t = 2035 or t = 2050} {
    printf "%4d %9.2f %9.2f %9.2f %9.2f %9.2f %11.1f%% %11.1f%%\n",
        t,
        ( h2elec_capex_kw[t]/(8760*re_cf/h2_kwh_per_t)*crf_h2elec + fopex_h2elec )/1000,
        ( h2_kw_per_t*(re_capex_kw[t]*crf_re + fopex_h2re) )/1000,
        ( h2_firm_capex[t]*crf_h2elec )/1000,
        h2_opex[t]/1000,
        ( ocapex_h2elec[t]*crf_h2elec + fopex_h2elec
          + h2_kw_per_t*(ocapex_h2re[t]*crf_re + fopex_h2re) + h2_opex[t] )/1000,
        100*( h2_kw_per_t*(re_capex_kw[t]*crf_re + fopex_h2re) + h2_firm_capex[t]*crf_h2elec )
           /( ocapex_h2elec[t]*crf_h2elec + fopex_h2elec
              + h2_kw_per_t*(ocapex_h2re[t]*crf_re + fopex_h2re) + h2_opex[t] ),
        100*( h2elec_capex_kw[t]/(8760*re_cf/h2_kwh_per_t)*crf_h2elec + fopex_h2elec )
           /( ocapex_h2elec[t]*crf_h2elec + fopex_h2elec
              + h2_kw_per_t*(ocapex_h2re[t]*crf_re + fopex_h2re) + h2_opex[t] );
}

printf "\nPOWER SCENARIO (theta_tech = %.2f, theta_grid = %.2f, theta_ccs = %.2f) -- derived cost paths\n",
       theta_tech, theta_grid, theta_ccs;
printf "%-6s %-12s %-14s %-12s %-15s\n",
       "YEAR", "Grid $/kWh", "Grid tCO2/kWh", "LCOH $/kg", "CCS all-in $/t";
for {t in T: t = 2025 or t = 2030 or t = 2035 or t = 2040 or t = 2045 or t = 2050} {
    printf "%4d %10.4f %14.6f %12.2f %15.2f\n",
        t, ng_cost_power[t], n9_grid_ef[t],
        ( ocapex_h2elec[t]*crf_h2elec + fopex_h2elec
          + h2_kw_per_t*(ocapex_h2re[t]*crf_re + fopex_h2re) + h2_opex[t] ) / 1000,
        ocapex_ccs[t]*(crf_ccs + ccs_fom_pct)                       # all-in incl T&S (BF ref stream)
          + ccs_kwh_bf*ng_cost_power[t] + ccs_steam_bf*ccs_ref_steam
          + ccs_vopex_solvent + ccs_ts_cost;
}
       
printf "\n%-20s %-20s\n", "Route", "Fraction";
printf "%-20s %10.4f\n", "BF-BOF", f_bof[2050];
printf "%-20s %10.4f\n", "Coal DRI-EAF", f_cdri[2050] * f_eaf[2050];
printf "%-20s %10.4f\n", "NG DRI-EAF", f_ngdri[2050] * f_eaf[2050];
printf "%-20s %10.4f\n", "H2 DRI-EAF", 
    (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "%-20s %10.4f\n", "Scrap-EAF", 
    1 - f_bof[2050] 
      - f_cdri[2050] * f_eaf[2050] 
      - f_ngdri[2050] * f_eaf[2050] 
      - (1 - f_cdri[2050] - f_ngdri[2050]) * f_eaf[2050];

printf "\nTOTAL H2 USED IN H2-DRI (2025â€“2050): %.3f million units\n",
       ( sum{t in T} steel_eaf[t] * (1 - f_cdri[t] - f_ngdri[t]) ) / 1e6;
printf "\n";
printf "\nSCRAP ALLOCATION (blend shares = scrap / metallic charge; flows in t)\n";
printf "%-6s %-8s %-8s %-8s %-8s   %-12s %-12s %-12s\n",
       "YEAR", "BOF", "CoalDRI", "NGDRI", "H2DRI", "Scrap-EAF t", "Total scrap", "Limit";
for {t in T} {
    printf "%4d %8.3f %8.3f %8.3f %8.3f   %12.0f %12.0f %12.0f\n",
        t,
        if steel_bof[t]       > 1e-6 then bof_scrap_in[t]    /(n3_metallic_bof*steel_bof[t])      else 0,
        if coaldri_output[t]  > 1e-6 then coaldri_scrap_in[t]/(n7_dri_ratio*coaldri_output[t])    else 0,
        if ngdri_output[t]    > 1e-6 then ngdri_scrap_in[t]  /(n7_dri_ratio*ngdri_output[t])      else 0,
        if h2dri_output[t]    > 1e-6 then h2dri_scrap_in[t]  /(n7_dri_ratio*h2dri_output[t])      else 0,
        steel_scrap_eaf[t],
        bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t],
        n8_scrap_limit[t];
}
printf "\n";
printf "\n%-6s %-20s %-37s %-18s %-10s",
       "YEAR",
       "BF-BOF (t/f)",
       "DRI-EAF (t/f split)",
       "Scrap-EAF (t/f)",
       "Total";

printf "\n%-6s %-12s %-15s %-15s %-20s %-10s %-10s",
       "", "", "Coal", "NG", "H2", "", "";

for {t in T} {
    printf "\n%4d %8.0f/%5.2f %8.0f/%5.2f %8.0f/%5.2f %8.0f/%5.2f %10.0f/%5.2f %10.0f",
        t,
        steel_bof[t], f_bof[t],                                  # BF-BOF
        steel_eaf[t] * f_cdri[t], f_cdri[t] * f_eaf[t],                            # Coal DRI
        steel_eaf[t] * f_ngdri[t] , f_ngdri[t] * f_eaf[t],                             # NG DRI
        steel_eaf[t] * (1 - f_cdri[t] - f_ngdri[t]), (1 - f_cdri[t] - f_ngdri[t]) * f_eaf[t],            # H2 DRI
        steel_scrap_eaf[t], 1 - f_bof[t] - f_cdri[t] * f_eaf[t] - f_ngdri[t] * f_eaf[t] - (1 - f_cdri[t] - f_ngdri[t]) * f_eaf[t],            # Scrap-EAF
        total_steel[t];                                          # Total
}

printf "\n";

# TABLE 2: CCS fractions and captured amounts
printf "\n%-6s %-20s %-20s %-20s %-15s %-12s",
       "YEAR",
       "BF-BOF CCS (t/f)",
       "Coal-DRI CCS (t/f)",
       "NG-DRI CCS (t/f)",
       "Total CCS",
       "CCS Fraction";


for {t in T} {
    printf "\n%4d %10.0f/%5.2f %10.0f/%5.2f %10.0f/%5.2f %20.0f %12.3f",
        t,

        # BFâ€“BOF CCS and share
        ccs_bf[t],
        if total_ccs[t] > 0 then ccs_bf[t] / steel_bof[t] else 0,

        # Coalâ€“DRI CCS and share
        ccs_cdri[t],
        if total_ccs[t] > 0 then ccs_cdri[t] / (steel_eaf[t] * f_cdri[t]) else 0,

        # NGâ€“DRI CCS and share
        ccs_ngdri[t],
        if total_ccs[t] > 0 then ccs_ngdri[t] / (steel_eaf[t] * f_ngdri[t])  else 0,

        # Total CCS
        total_ccs[t],

        # Capture rate relative to emissions
        if total_emissions[t] + total_ccs[t] > 0 then
            total_ccs[t] / (total_emissions[t] + total_ccs[t])
        else 0;
}



printf "\n";
printf "\nTOTAL FRACTION OF CO2 CAPTURED (2025â€“2050): %.3f\n",
       if (sum{t in T} total_emissions[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} total_emissions[t] + ( sum{t in T}total_ccs[t]) )
       else 0;


printf "\n";
printf "\nTOTAL FRACTION OF DIRECT CO2 CAPTURED (2025â€“2050): %.3f\n",
       if (sum{t in T} scope1_emissions[t]) > 0 then
           ( sum{t in T} total_ccs[t] )
         / ( sum{t in T} scope1_emissions[t] )
       else 0;


printf "\n";
printf "\n%-6s %-25s %-25s",
       "YEAR",
       "Avg Emissions (tCO2/ton)",
       "Avg Cost ($/ton)";

for {t in T} {
    printf "\n%4d %25.3f %25.3f",
        t,
        if total_steel[t] > 0 then
            total_emissions[t] / total_steel[t]
        else 0,
        if total_steel[t] > 0 then
            total_cost[t] / total_steel[t]
        else 0;
}

printf "\n";

printf "\nAVG (NON-LEVELIZED) STEEL PRODUCTION COST (2025â€“2050): %.2f $/ton\n",
       if sum{t in T} total_steel[t] > 0 then
           ( sum{t in T} total_cost[t] )
         / ( sum{t in T} total_steel[t] )
       else 0;

printf "\n";

# route costs per year
printf "\n%-6s %-12s %-15s %-15s %-15s %-15s",
       "YEAR",
       "BF-BOF ($/t)",
       "Coal DRI-EAF ($/t)",
       "NG DRI-EAF ($/t)",
       "H2 DRI-EAF ($/t)",
       "Scrap-EAF ($/t)";

for {t in T} {
    printf "\n%4d %12.2f %15.2f %15.2f %15.2f %15.2f",
        t,

        # BF-BOF 
        if steel_bof[t] > 0 then
           ( acapex_bof*(cap_bof[t]-legacy_bof[t]) + fopex_bof*cap_bof[t]
           + cost_cokeov[t] + cost_sinter[t] + cost_pellet_bf[t] + cost_bf[t] + cost_bof[t]
           + other_opex*steel_bof[t]
           + carbon_tax*scope1_bf[t]
           + (ocapex_ccs[t]*crf_ccs + fom_ccs[t])*ccs_mult_bf*ccs_cap_bf[t]
           + (ng_cost_power[t]*ccs_kwh_bf + ccs_steam_bf*ccs_ref_steam + ccs_vopex_solvent + ccs_ts_cost)*ccs_bf[t]
           - wasteheat_bf_bof[t]*0.9*277.78*n9_eta*n9_whr[t]*(ng_cost_power[t] - n9_whr_capex - n9_whr_opex))
           / steel_bof[t]
        else 0,

        # Coal DRI-EAF
        if steel_eaf[t]*f_cdri[t] > 0 then
           ( acapex_cdri*(cap_cdri[t]-legacy_cdri[t]) + fopex_cdri*cap_cdri[t]
           + cost_coaldri[t] + f_cdri[t]*cost_eaf[t] + cost_pellet_coaldri[t]
           + other_opex*(steel_eaf[t]*f_cdri[t])
           + carbon_tax*scope1_cdri[t]
           + (ocapex_ccs[t]*crf_ccs + fom_ccs[t])*ccs_mult_cdri*ccs_cap_cdri[t]
           + (ng_cost_power[t]*ccs_kwh_cdri + ccs_steam_cdri*ccs_ref_steam + ccs_vopex_solvent + ccs_ts_cost)*ccs_cdri[t]
           - wasteheat_eaf[t]*0.9*277.78*n9_eta*n9_whr[t]*(ng_cost_power[t] - n9_whr_capex - n9_whr_opex)*f_cdri[t] )
           / (steel_eaf[t]*f_cdri[t])
        else 0,

        # NG DRI-EAF
        if steel_eaf[t]*f_ngdri[t] > 0 then
           ( acapex_ngdri*(cap_ngdri[t]-legacy_ngdri[t]) + fopex_ngdri*cap_ngdri[t]
           + cost_ngdri[t] + f_ngdri[t]*cost_eaf[t] + cost_pellet_ngdri[t]
           + other_opex*(steel_eaf[t]*f_ngdri[t])
           + carbon_tax*scope1_ngdri[t]
           + (ocapex_ccs[t]*crf_ccs + fom_ccs[t])*ccs_mult_ngdri*ccs_cap_ngdri[t]
           + (ng_cost_power[t]*ccs_kwh_ngdri + ccs_steam_ngdri*ccs_ref_steam + ccs_vopex_solvent + ccs_ts_cost)*ccs_ngdri[t]
           - wasteheat_eaf[t]*0.9*277.78*n9_eta*n9_whr[t]*(ng_cost_power[t] - n9_whr_capex - n9_whr_opex)*f_ngdri[t] )
           / (steel_eaf[t]*f_ngdri[t])
        else 0,

        # H2 DRI-EAF  (no CCS stream). Includes the green-H2 SUPPLY capital
        # (electrolyser + dedicated renewable, annualized capex + fixed O&M) allocated
        # to this route by its share of total H2 use (DRI vs BF injection).
        if t >= ng_h2_start_year && steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]) > 0 then
           ( acapex_h2dri[t]*(cap_h2dri[t]-legacy_h2dri[t]) + fopex_h2dri*cap_h2dri[t]
           + ( (acapex_h2elec[t]+fopex_h2elec)*cap_h2elec[t] + (acapex_h2re[t]+fopex_h2re)*cap_h2re[t] )
             * ( if h2dri_h2_in[t]+bf_h2_in[t] > 0 then h2dri_h2_in[t]/(h2dri_h2_in[t]+bf_h2_in[t]) else 0 )
           + cost_h2dri[t] + (1-f_cdri[t]-f_ngdri[t])*cost_eaf[t] + cost_pellet_h2dri[t]
           + other_opex*(steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
           + carbon_tax*scope1_h2dri[t]
           - wasteheat_eaf[t]*0.9*277.78*n9_eta*n9_whr[t]*(ng_cost_power[t] - n9_whr_capex - n9_whr_opex)*(1-f_cdri[t]-f_ngdri[t]) )
           / (steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
        else 0,

        # Scrap-EAF  (no CCS stream)
        if steel_scrap_eaf[t] > 0 then
           ( acapex_scrap*(cap_scrap[t]-legacy_scrap[t]) + fopex_scrap*cap_scrap[t]
           + cost_scrap_eaf[t]
           + other_opex*steel_scrap_eaf[t]
           + carbon_tax*scope1_scrapeaf[t]
           - scrap_eaf_wasteheat[t]*0.9*277.78*n9_eta*n9_whr[t]*(ng_cost_power[t] - n9_whr_capex - n9_whr_opex))
           / steel_scrap_eaf[t]
        else 0;
}


# route emissions per year
printf "\n%-6s %-12s %-15s %-15s %-15s %-15s",
       "YEAR",
       "BF-BOF (tCO2/t)",
       "Coal DRI-EAF (tCO2/t)",
       "NG DRI-EAF (tCO2/t)",
       "H2 DRI-EAF (tCO2/t)",
       "Scrap-EAF (tCO2/t)";

for {t in T} {

    printf "\n%4d %12.3f %15.3f %15.3f %15.3f %15.3f",
        t,

        #  BF-BOF
        if steel_bof[t] > 0 then
            (scope1_bf[t] 
             + n9_grid_ef[t] * max(coke_power_in[t] + sinter_power_in[t] + bf_power_in[t]
                                    - (cdq_power_out[t] + sinterwaste_power_out[t] + bf_trt_out[t]),
                                    0)
             - ccs_bf[t])
            / steel_bof[t]
        else 0,

        # Coal DRI-EAF 
        if steel_eaf[t]*f_cdri[t] > 0 then
            (scope1_cdri[t]
             + n9_grid_ef[t] * (coaldri_power_in[t] + f_cdri[t]*eaf_power_in[t] + pellets_power_coaldri[t])
             - ccs_cdri[t])
            / (steel_eaf[t]*f_cdri[t])
        else 0,

        # NG DRI-EAF
        if steel_eaf[t]*f_ngdri[t] > 0 then
            (scope1_ngdri[t]
             + n9_grid_ef[t] * (ngdri_power_in[t] + f_ngdri[t]*eaf_power_in[t] + pellets_power_ngdri[t])
             - ccs_ngdri[t])
            / (steel_eaf[t]*f_ngdri[t])
        else 0,

        #  H2 DRI-EAF 
        if t >= ng_h2_start_year && steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]) > 0 then
            (( eaf_coal_in[t] * (1- f_cdri[t]-f_ngdri[t]) * 0.110*24+ eaf_lime_in[t] * (1- f_cdri[t]-f_ngdri[t]) * 0.44 + eaf_electrode_in[t] *  (1- f_cdri[t]-f_ngdri[t]) * 6)
             + n9_grid_ef[t] * ((1-f_cdri[t]-f_ngdri[t])*eaf_power_in[t] + pellets_power_h2dri[t] + h2dri_power_in[t]))
            / (steel_eaf[t]*(1-f_cdri[t]-f_ngdri[t]))
        else 0,

        #Scrap-EAF
        if steel_scrap_eaf[t] > 0 then
            (scope1_scrapeaf[t]
             + n9_grid_ef[t] * scrap_eaf_power_in[t])
            / steel_scrap_eaf[t]
        else 0;
}

printf "\n";

printf "\n";
       
