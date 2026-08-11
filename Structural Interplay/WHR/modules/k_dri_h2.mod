# H2 DRI
s.t. dri_route_split{t in T}:
    coaldri_output[t] + ngdri_output[t] + h2dri_output[t] - dri_eaf_steel_out[t] = 0;   # eq56

s.t. h2dri_metallic_balance{t in T}:
    h2dri_dri_out[t] + h2dri_scrap_in[t] = n7_dri_ratio * h2dri_output[t];

s.t. h2dri_scrap_blend_max{t in T}:
    h2dri_scrap_in[t] <= phi_max_h2dri * n7_dri_ratio * h2dri_output[t];

# Power consumption for H2 DRI
s.t. h2dri_power_balance{t in T}:
    n6_e_dri * h2dri_dri_out[t] - h2dri_power_in[t] = 0;         # eq57

# Pellets required for H2 DRI
s.t. h2dri_pellets_balance{t in T}:
    n6_pel_dri * h2dri_dri_out[t] - h2dri_pellets_in[t] = 0;      # eq58

# Lump ore requirement
s.t. h2dri_lumpore_balance{t in T}:
    n6_ore_dri * h2dri_dri_out[t] - h2dri_lumpore_in[t] = 0;     # eq59

# Hydrogen consumption
s.t. h2dri_h2_balance{t in T}:
    n6_h2_dri * h2dri_dri_out[t] - h2dri_h2_in[t] = 0;           # eq60
