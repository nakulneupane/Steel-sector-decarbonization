
# Scrap-EAF    
s.t. scrap_eaf_power_balance{t in T}:
    n8_e_eaf[t] * steel_scrap_eaf[t] - scrap_eaf_power_in[t] = 0;       # eq70

s.t. scrap_eaf_scrap_balance{t in T}:
    n8_phi_eaf * steel_scrap_eaf[t] - scrap_eaf_scrap_in[t] = 0;        # eq71
    
s.t. scrap_eaf_electrode_balance{t in T}:
    n8_eltrd * steel_scrap_eaf[t] - scrap_eaf_electrode_in[t] = 0;      # eq72

s.t. scrap_eaf_lime_balance{t in T}:
    n8_ls * steel_scrap_eaf[t] - scrap_eaf_lime_in[t] = 0;              # eq73

s.t. scrap_eaf_coal_balance{t in T}:
    n8_cs * steel_scrap_eaf[t] - scrap_eaf_coal_in[t] = 0;              # eq74

s.t. scrap_eaf_slag_balance{t in T}:
    n8_ss * steel_scrap_eaf[t] - scrap_eaf_slag_out[t] = 0;             # eq75
            
s.t. scrap_eaf_gas_balance{t in T}:
    n8_eafg * steel_scrap_eaf[t] - scrap_eaf_gas_out[t] = 0;            # eq76
    





    




    

    
