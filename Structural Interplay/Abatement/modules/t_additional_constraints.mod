# Initialization

s.t. init_f_bof: f_bof[first(T)] = 0.51;
s.t. init_f_eaf: f_eaf[first(T)] = 0.49;
s.t. init_scrap_eaf: steel_scrap_eaf[first(T)] = 0;
s.t. init_f_cdri: coaldri_output[first(T)] = 0.902 * dri_eaf_steel_out[first(T)];
    
# Demand and availability Constraints
s.t. meet_demand{t in T}:
    total_steel[t] = base_demand * (1 + growth_rate)^(ord(t) - 1);

# Scrap-EAF 
s.t. scrap_bound{t in T: t > first(T)}:
    bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t] <= n8_scrap_limit[t];

s.t. ng_bound{t in T}:
   ngdri_ng_in[t] <= n5_ng_cap[t];

# Coking-coal availability
s.t. coking_coal_bound{t in T: t > first(T)}:
   coking_coal_in[t] <= ccoal_cap[t];

# Policy constraint
s.t. avg_emis_cap_total:
    (sum {t in T} total_emissions[t]) <= avg_emi * (sum {t in T} total_steel[t]);

s.t. emission_monotonic {t in T: t > first(T)}:
    total_emissions[t] * total_steel[t-1]
    <=
    total_emissions[t-1] * total_steel[t];
