
# COST EQUATIONS 

# Coke Oven
s.t. cost_cokeov_def{t in T}:
    ng_cost_ccoal   * coking_coal_in[t]
  + ng_cost_power[t]  * coke_power_in[t]
  - n0_credit_breeze * coke_breeze_out[t]
  - n0_credit_tar    * tar_out[t]
  - ng_cost_power[t] * cdq_power_out[t]     
  - cost_cokeov[t] = 0;                              # eq89

# Sinter
s.t. cost_sinter_def{t in T}:
    n1_cost_breeze  * sinter_breeze_in[t]
  + ng_cost_fineore * sinter_fineore_in[t]
  + ng_cost_power[t]   * sinter_power_in[t]
  + ng_cost_lime    * sinter_lime_in[t]
  + ng_cost_biochar * sinter_biochar_in[t]
  - ng_cost_power[t] * sinterwaste_power_out[t]   
  - cost_sinter[t] = 0;                              # eq90

# Pellets BF
s.t. cost_pellet_bf_def{t in T}:
    ng_cost_fineore  * pellets_fineore_bf[t]
  + ng_cost_power[t]    * pellets_bf_power[t]
  - cost_pellet_bf[t] = 0;                           # eq91
  
# Blast Furnace
s.t. cost_bf_def{t in T}:
    ng_cost_lumpore * bf_lumpore_in[t]
  + ng_cost_pcoal     * bf_coalpci_in[t]
  + ng_cost_biochar * bf_biopci_in[t]
  + ng_cost_power[t]   * bf_power_in[t]
  + ng_cost_lime    * bf_lime_in[t]
  - ng_cost_power[t] * bf_trt_out[t]        
  - ng_credit_slag  * bf_slag_out[t]
  - cost_bf[t] = 0;                                  # eq92

# BOF
s.t. cost_bof_def{t in T}:
    ng_cost_scrap  * bof_scrap_in[t]
  + ng_cost_power[t]  * bof_power_in[t]
  + ng_cost_lime   * bof_lime_in[t]
  - ng_credit_slag * bof_slag_out[t]
  - cost_bof[t] = 0;                                 # eq93

# Pellets Coal DRI
s.t. cost_pellet_coaldri_def{t in T}:
    ng_cost_fineore  * pellets_fineore_coaldri[t]
  + ng_cost_power[t]    * pellets_power_coaldri[t]
  - cost_pellet_coaldri[t] = 0;                      # eq94

#  Pellets NG DRI
s.t. cost_pellet_ngdri_def{t in T}:
    ng_cost_fineore * pellets_fineore_ngdri[t]
  + ng_cost_power[t]   * pellets_power_ngdri[t]
  - cost_pellet_ngdri[t] = 0;                        # eq95
       
# Pellets H2 DRI
s.t. cost_pellet_h2dri_def{t in T}:
    ng_cost_fineore * pellets_fineore_h2dri[t]
  + ng_cost_power[t]   * pellets_power_h2dri[t]
  - cost_pellet_h2dri[t] = 0;                        # eq96
  
# Coal DRI
s.t. cost_coaldri_def{t in T}:
    ng_cost_power[t] * coaldri_power_in[t]
  + ng_cost_lumpore * coaldri_lumpore_in[t]
  + ng_cost_ncoal     * coaldri_coal_in[t]
  - cost_coaldri[t] = 0;                             # eq97

# NG DRI
s.t. cost_ngdri_def{t in T}:
    ng_cost_power[t]  * ngdri_power_in[t]
  + ng_cost_lumpore * ngdri_lumpore_in[t]
  + n5_cost_NG[t] *50     * ngdri_ng_in[t]
  - cost_ngdri[t] = 0;                               # eq98

# H2 DRI
s.t. cost_h2dri_def{t in T}:
    ng_cost_power[t]  * h2dri_power_in[t]
  + ng_cost_lumpore * h2dri_lumpore_in[t]
  + h2_opex[t]     * h2dri_h2_in[t]
  - cost_h2dri[t] = 0;                               # eq99
  
# EAF-I (DRI-EAF)
s.t. cost_eaf_def{t in T}:
    ng_cost_scrap    * eaf_scrap_in[t]
  + ng_cost_power[t]    * eaf_power_in[t]
  + ng_cost_lime     * eaf_lime_in[t]
  + ng_cost_ncoal     * eaf_coal_in[t]
  + n7_cost_electrode* eaf_electrode_in[t]
  - ng_credit_slag   * eaf_slag_out[t]
  - cost_eaf[t] = 0;                                # eq100
        
# Scrap EAF 
s.t. cost_scrap_eaf_def{t in T}:
    ng_cost_scrap   * scrap_eaf_scrap_in[t]
  + ng_cost_power[t]   * scrap_eaf_power_in[t]
  + ng_cost_lime    * scrap_eaf_lime_in[t]
  + ng_cost_ncoal    * scrap_eaf_coal_in[t]
  + n8_cost_electrode * scrap_eaf_electrode_in[t]
  - ng_credit_slag  * scrap_eaf_slag_out[t]
  - cost_scrap_eaf[t] = 0;                          # eq101

# WHR System
s.t. cost_wasteheat{t in T}:
   n9_whr_capex * whr_power_generated[t]
   + n9_whr_opex *  whr_power_generated[t]
   - whr_cost[t] = 0;                              #eq102
   
# Carbon capture 
s.t. cost_ccs_def{t in T}:
    cost_ccs[t] =
        ocapex_ccs[t] * (ccs_mult_bf*build_ccs_bf[t] + ccs_mult_cdri*build_ccs_cdri[t] + ccs_mult_ngdri*build_ccs_ngdri[t])
      + fom_ccs[t]    * (ccs_mult_bf*ccs_cap_bf[t]   + ccs_mult_cdri*ccs_cap_cdri[t]   + ccs_mult_ngdri*ccs_cap_ngdri[t])
      + ng_cost_power[t] * power_ccs[t]
      + ccs_vopex_solvent * total_ccs[t]
      + ccs_ts_cost * total_ccs[t]
      + (n5_cost_NG[t]/ng_gj_per_mmbtu) * ccs_steam_boiler[t]/ccs_boiler_eff;    #eq103
    
       
# Total cost
s.t. total_cost_def{t in T}:
      cost_cokeov[t]
    + cost_sinter[t]
    + cost_bf[t]
    + cost_bof[t]
    + cost_eaf[t]
    + cost_coaldri[t]
    + cost_pellet_coaldri[t]
    + cost_pellet_bf[t]
    + cost_pellet_ngdri[t]
    + cost_pellet_h2dri[t]
    + cost_scrap_eaf[t]
    + cost_ngdri[t]
    + cost_h2dri[t]
    + cost_ccs[t]
    + other_opex * total_steel[t]                                    # variable other-opex (labour+maint now fixed)
    + capex_cost[t]                                                  # overnight capex on builds (v_capacity.mod)
    + fixopex_cost[t]                                                # fixed opex (labour+maintenance) on capacity
    + whr_cost[t]
    - ng_cost_power[t] * whr_power_generated[t]    
    - total_cost[t] = 0;                            # eq104



    
    
