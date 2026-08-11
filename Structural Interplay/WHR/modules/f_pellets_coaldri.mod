# Pellets for Coal DRI 

s.t. pellets_coaldri_fineore_balance{t in T}:
    coaldri_pellets_in[t] / ng_ore_pell - pellets_fineore_coaldri[t] = 0;    # eq40
    
s.t. pellets_coaldri_power_balance{t in T}:
    ng_e_pell * coaldri_pellets_in[t] - pellets_power_coaldri[t] = 0;        # eq41
    
