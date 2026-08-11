# EAF-I (DRI-EAF) 

# Fraction of total steel going to EAF
s.t. eaf_steel_fraction{t in T}:
    f_eaf[t] * dem[t] - steel_eaf[t] = 0;                 # eq61  

# Power consumption
s.t. eaf_power_balance{t in T}:
    n7_e_eaf[t] * steel_eaf[t] - eaf_power_in[t] = 0;             # eq62

s.t. eaf_scrap_balance{t in T}:
    coaldri_scrap_in[t] + ngdri_scrap_in[t] + h2dri_scrap_in[t] - eaf_scrap_in[t] = 0;   # eq63

# Electrode consumption
s.t. eaf_electrode_balance{t in T}:
    n7_eltrd * steel_eaf[t] - eaf_electrode_in[t] = 0;            # eq64
    
# Lime balance
s.t. eaf_lime_balance{t in T}:
    n7_ls * steel_eaf[t] - eaf_lime_in[t] = 0;                    # eq65

# Coal balance
s.t. eaf_coal_balance{t in T}:
    n7_cs * steel_eaf[t] - eaf_coal_in[t] = 0;                    # eq66

# Slag generation
s.t. eaf_slag_balance{t in T}:
    n7_ss * steel_eaf[t] - eaf_slag_out[t] = 0;                   # eq67

# EAF off-gas
s.t. eaf_gas_out{t in T}:
    n7_eafg * steel_eaf[t] - eafgas_out[t] = 0;                   # eq68
    
s.t. dri_eaf_steel_relation{t in T}:
    steel_eaf[t] - dri_eaf_steel_out[t] = 0;    # eq69












