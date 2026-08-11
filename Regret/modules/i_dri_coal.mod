# COAL DRI-EAF/IF

# Metallic charge: 
s.t. coaldri_metallic_balance{t in T}:
    coaldri_dri_out[t] + coaldri_scrap_in[t] = n7_dri_ratio * coaldri_output[t];  # eq46

# Blend:
s.t. coaldri_scrap_blend0:
    coaldri_scrap_in[first(T)] = phi0_cdri * n7_dri_ratio * coaldri_output[first(T)];
s.t. coaldri_scrap_blend_max{t in T: t > first(T)}:
    coaldri_scrap_in[t] <= phi_max_cdri * n7_dri_ratio * coaldri_output[t];
s.t. coaldri_scrap_blend_min{t in T: t > first(T)}:
    coaldri_scrap_in[t] >= phi_min_cdri * n7_dri_ratio * coaldri_output[t];
s.t. coaldri_scrap_ramp_up{t in T: t > first(T)}:
    coaldri_scrap_in[t] - coaldri_scrap_in[prev(t)] <= blend_ramp * n7_dri_ratio * coaldri_output[t];
s.t. coaldri_scrap_ramp_dn{t in T: t > first(T)}:
    coaldri_scrap_in[prev(t)] - coaldri_scrap_in[t] <= blend_ramp * n7_dri_ratio * coaldri_output[t];

# Power consumption (Coal DRI shaft + IF secondary share carried in n4_e_dri)
s.t. coaldri_power_balance{t in T}:
    n4_e_dri * coaldri_dri_out[t] - coaldri_power_in[t] = 0;       # eq47

# Pellet requirement for Coal DRI
s.t. coaldri_pellets_balance{t in T}:
    n4_pel_dri * coaldri_dri_out[t] - coaldri_pellets_in[t] = 0;      # eq48

# Lump ore requirement (Coal DRI)
s.t. coaldri_lumpore_balance{t in T}:
    n4_ore_dri * coaldri_dri_out[t] - coaldri_lumpore_in[t] = 0;   # eq49

# Coal consumption in Coal DRI
s.t. coaldri_coal_balance{t in T}:
    n4_c_dri * coaldri_dri_out[t] - coaldri_coal_in[t] = 0;        # eq50
