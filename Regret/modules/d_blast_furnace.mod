# Blast Furnace balances
    
s.t. power_bf_in{t in T}:
    n2_e_hm * bf_hot_metal[t] - bf_power_in[t] = 0;      # eq18
    
s.t. sinter_bf_in{t in T}:
    n2_sint_hm * bf_hot_metal[t] - bf_sinter_in[t] = 0;     # eq19
    
s.t. lime_bf_in{t in T}:
    n2_lime_hm * bf_hot_metal[t] - bf_lime_in[t] = 0;    # eq20
    
s.t. slag_bf_out{t in T}:
    n2_slag_hm * bf_hot_metal[t] - bf_slag_out[t] = 0;   # eq21
    
s.t. pellets_bf_in{t in T}:
    n2_pel_hm * bf_hot_metal[t] - bf_pellets_in[t] = 0;  # eq22
    
s.t. lumpore_bf_in{t in T}:
    n2_ore_hm * bf_hot_metal[t] - bf_lumpore_in[t] = 0;   # eq23
     
s.t. bfg_bf_in{t in T}:
    n2_rec_bfg * ng_bfg_cv * bf_hot_metal[t] - bfg_in[t] = 0;          # eq24

s.t. cog_bf_in{t in T}:
    n2_rec_cog * ng_cog_cv * bf_hot_metal[t] - bf_cog_in[t] = 0;          # eq25

s.t. bfg_bf_out{t in T}:
    n2_bfg_hm * ng_bfg_cv * bf_hot_metal[t] - bfg_out[t] = 0;          # eq26
    
s.t. trt_power_out{t in T}:
    n2_trt_whr * bf_hot_metal[t] - bf_trt_out[t] = 0;                     # eq27

s.t. bf_coal_pci_balance {t in T}:
   (n2_coalpci_hm_25 + (n2_coalpci_hm_50 - n2_coalpci_hm_25) * (t - 2025) / 25) * bf_hot_metal[t] -  bf_coalpci_in[t] = 0;   # eq28

s.t. bf_bio_pci_balance {t in T}:
   (n2_biopci_hm_25 + (n2_biopci_hm_50 - n2_biopci_hm_25) * (t - 2025) / 25) * bf_hot_metal[t] -  bf_biopci_in[t] = 0;       # eq29

s.t. bf_coke_balance {t in T}:
   (n2_coke_hm_25 + (n2_coke_hm_50 - n2_coke_hm_25) * (t - 2025) / 25) * bf_hot_metal[t] -  bf_coke_in[t] = 0;               # eq30

s.t. bf_h2_balance {t in T}:
   (n2_h2_hm_25 + (n2_h2_hm_50 - n2_h2_hm_25) * (t - 2025) / (2050 - 2025)) * bf_hot_metal[t] - bf_h2_in[t] = 0;   # eq31
      
s.t. bf_hot_metal_out{t in T}:
    bf_hot_metal[t] = n3_metallic_bof * steel_bof[t] - bof_scrap_in[t];  # eq32

  
  
