# NG DRI
# Metallic charge: 
s.t. ngdri_metallic_balance{t in T}:
    ngdri_dri_out[t] + ngdri_scrap_in[t] = n7_dri_ratio * ngdri_output[t];   # eq51

# Blend:
s.t. ngdri_scrap_blend0:
    ngdri_scrap_in[first(T)] = phi0_ngdri * n7_dri_ratio * ngdri_output[first(T)];
s.t. ngdri_scrap_blend_max{t in T: t > first(T)}:
    ngdri_scrap_in[t] <= phi_max_ngdri * n7_dri_ratio * ngdri_output[t];
s.t. ngdri_scrap_blend_min{t in T: t > first(T)}:
    ngdri_scrap_in[t] >= phi_min_ngdri * n7_dri_ratio * ngdri_output[t];
s.t. ngdri_scrap_ramp_up{t in T: t > first(T)}:
    ngdri_scrap_in[t] - ngdri_scrap_in[prev(t)] <= blend_ramp * n7_dri_ratio * ngdri_output[t];
s.t. ngdri_scrap_ramp_dn{t in T: t > first(T)}:
    ngdri_scrap_in[prev(t)] - ngdri_scrap_in[t] <= blend_ramp * n7_dri_ratio * ngdri_output[t];

# Power consumption for NG DRI
s.t. ngdri_power_balance{t in T}:
    n5_e_dri * ngdri_dri_out[t] - ngdri_power_in[t] = 0;        # eq52

# Pellet requirement for NG DRI
s.t. ngdri_pellets_balance{t in T}:
    n5_pel_dri * ngdri_dri_out[t] - ngdri_pellets_in[t] = 0;     # eq53

# Lump ore consumption
s.t. ngdri_lumpore_balance{t in T}:
    n5_ore_dri * ngdri_dri_out[t] - ngdri_lumpore_in[t] = 0;    # eq54

# Natural gas consumption
s.t. ngdri_ng_balance{t in T}:
    n5_ng_dri * ngdri_dri_out[t] - ngdri_ng_in[t] = 0;          # eq55
