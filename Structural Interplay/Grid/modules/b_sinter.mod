
# Sinter Plant 
# Power 
s.t. sinter_power_balance{t in T}:
    n1_e_sint * bf_sinter_in[t] - sinter_power_in[t] = 0;              # eq9

# Lime 
s.t. sinter_lime_balance{t in T}:
    n1_lime_sint * bf_sinter_in[t] - sinter_lime_in[t] = 0;            # eq10

# Fine ore 
s.t. sinter_fineore_balance{t in T}:
    n1_ore_sint * bf_sinter_in[t] - sinter_fineore_in[t] = 0;           # eq11

# Breeze
s.t. sinter_breeze_balance {t in T}:
   (n1_brz_sint_25 + (n1_brz_sint_50 - n1_brz_sint_25) * (t - 2025) / (2050 - 2025)) * bf_sinter_in[t] -  sinter_breeze_in[t] = 0;   # eq12

# Biochar
s.t. sinter_biochar_balance {t in T}:
   (n1_bio_sint_25 + (n1_bio_sint_50 - n1_bio_sint_25) * (t - 2025) / (2050 - 2025)) * bf_sinter_in[t] -  sinter_biochar_in[t] = 0;   # eq13

# Sinter waste heat recovery
s.t. sinter_whr_balance{t in T}:
    n1_sintcool_whr * bf_sinter_in[t] - sinterwaste_power_out[t] = 0;               # eq14

# Sinter gas (SG) output
s.t. sinter_gas_balance{t in T}:
    n1_sintgas_sint * ng_sintgas_cv * bf_sinter_in[t] - sg_out[t] = 0;              # eq15
