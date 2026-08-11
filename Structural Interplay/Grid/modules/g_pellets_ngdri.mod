# Pellets for Natural Gas DRI 

s.t. pellets_ngdri_fineore_balance{t in T}:
    ngdri_pellets_in[t] / ng_ore_pell - pellets_fineore_ngdri[t] = 0;    # eq42
    
s.t. pellets_ngdri_power_balance{t in T}:
    ng_e_pell * ngdri_pellets_in[t] - pellets_power_ngdri[t] = 0;        # eq43