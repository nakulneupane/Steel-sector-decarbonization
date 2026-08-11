
# Coke Oven balances 

s.t. coke_power_balance{t in T}:
    n0_e_c * bf_coke_in[t] - coke_power_in[t] = 0;       # eq1
    
s.t. coke_coal_balance{t in T}:
    bf_coke_in[t] * n0_cf - coking_coal_in[t] = 0;       # eq2

s.t. coke_breeze_out_balance{t in T}:
    n0_br_c * bf_coke_in[t] - coke_breeze_out[t] = 0;  # eq3

s.t. coke_tar_balance{t in T}:
    n0_tar_c * bf_coke_in[t] - tar_out[t] = 0;            # eq4

s.t. coke_cog_out_balance{t in T}:
    n0_cog_c * ng_cog_cv * bf_coke_in[t] - cog_out[t] = 0;             # eq5 


s.t. coke_dry_quenching{t in T}:
    n0_cdq_whr * bf_coke_in[t] - cdq_power_out[t] = 0;       # eq6
    
s.t. coke_cog_recovered{t in T}:
    n0_rec_cog * ng_cog_cv* bf_coke_in[t] - cokeov_cog_in[t] = 0;        # eq7

s.t. coke_bfg_recovered{t in T}:
    n0_rec_bfg * ng_bfg_cv * bf_coke_in[t] - cokeov_bfg_in[t] = 0;   # eq8

    
