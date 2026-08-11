
# Pellets for Hydrogen DRI 

s.t. pellets_h2dri_fineore_balance{t in T}:
    h2dri_pellets_in[t] / ng_ore_pell - pellets_fineore_h2dri[t] = 0;    # eq44
    
s.t. pellets_h2dri_power_balance{t in T}:
    ng_e_pell * h2dri_pellets_in[t] - pellets_power_h2dri[t] = 0;        # eq45