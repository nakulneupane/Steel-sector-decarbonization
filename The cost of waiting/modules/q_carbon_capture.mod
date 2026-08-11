# Carbon capture 
param fc_max := 0.9;   # max physical capture rate per stream

# Physical capturable CO2 base per route 
s.t. co2_capturable_bf_def{t in T}:
    co2_capturable_bf[t] =
        coking_coal_in[t] * 0.1116 * 25 + bf_coalpci_in[t] * 0.106 * 26
      + (sinter_lime_in[t] + bf_lime_in[t] + bof_lime_in[t]) * 0.44;        # base for eq84

s.t. co2_capturable_cdri_def{t in T}:
    co2_capturable_cdri[t] =
        coaldri_coal_in[t] * 0.110 * 24 + (n7_cs*coaldri_output[t]) * 0.110 * 24
      + (n7_ls*coaldri_output[t]) * 0.44;                     # base for eq85

s.t. co2_capturable_ngdri_def{t in T}:
    co2_capturable_ngdri[t] =
        ngdri_ng_in[t] * 0.055 * 50 + (n7_cs*ngdri_output[t]) * 0.110 * 24
      + (n7_ls*ngdri_output[t]) * 0.44;                       # base for eq86

# per-route physical capture limit 
s.t. ccs_bf_cap{t in T}:
    ccs_bf[t]    <= n10_ccs_eta * fc_max * co2_capturable_bf[t];             # eq84
s.t. ccs_cdri_cap{t in T}:
    ccs_cdri[t]  <= n10_ccs_eta * fc_max * co2_capturable_cdri[t];           # eq85
s.t. ccs_ngdri_cap{t in T}:
    ccs_ngdri[t] <= n10_ccs_eta * fc_max * co2_capturable_ngdri[t];          # eq86

# Deployment-readiness fraction (infrastructure/logistics maturity) 
param phi_2050 := 0.50;
param ccs_avail{t in T} :=
    if t < 2027 then 0
    else phi_2050 * (t - 2027) / (2050 - 2027);   # 0 at 2027 -> 0.50 at 2050 (linear)

# sector-wide deployment ceiling 
s.t. ccs_sector_ceiling{t in T}:
    ccs_bf[t] + ccs_cdri[t] + ccs_ngdri[t]
      <= ccs_avail[t] * (co2_capturable_bf[t] + co2_capturable_cdri[t] + co2_capturable_ngdri[t]);

# Total captured CO2
s.t. total_captured_co2{t in T}:
   ccs_bf[t] +ccs_cdri[t] +ccs_ngdri[t]  - total_ccs[t] = 0;           # eq87
 
#Power used in capture (kWh/tCO2), stream-specific (depends on CO2 concentration).
s.t. power_capture{t in T}:
  ccs_kwh_bf*ccs_bf[t] + ccs_kwh_cdri*ccs_cdri[t] + ccs_kwh_ngdri*ccs_ngdri[t]
  - power_ccs[t] = 0;                                                   # eq88

# Solvent-regeneration STEAM balance
s.t. ccs_steam_balance{t in T}:
  ccs_steam_bf*ccs_bf[t] + ccs_steam_cdri*ccs_cdri[t] + ccs_steam_ngdri*ccs_ngdri[t]
  = ccs_steam_whr[t] + ccs_steam_boiler[t];                             # eq88b
   
   
