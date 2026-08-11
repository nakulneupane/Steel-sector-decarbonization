# Pellets for BF 
s.t. pellets_bf_power_balance{t in T}:
    ng_e_pell * bf_pellets_in[t] - pellets_bf_power[t] = 0;     # eq16
    
s.t. pellets_bf_fineore_balance{t in T}:
    bf_pellets_in[t] / ng_ore_pell - pellets_fineore_bf[t] = 0;        # eq17


