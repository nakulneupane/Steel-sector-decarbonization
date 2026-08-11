# Total Power Balance

s.t. total_power_balance{t in T}:
      coke_power_in[t]
    + sinter_power_in[t]
    + bf_power_in[t]
    + coaldri_power_in[t]
    + eaf_power_in[t]
    + bof_power_in[t]
    + pellets_power_coaldri[t]
    + pellets_bf_power[t]
    + scrap_eaf_power_in[t]
    + ngdri_power_in[t]
    + h2dri_power_in[t]
    + pellets_power_ngdri[t]
    + pellets_power_h2dri[t]
    + power_ccs[t]
    - cdq_power_out[t]
    - sinterwaste_power_out[t]
    - bf_trt_out[t]
    - whr_power_generated[t]
    - grid_power_in[t]
    = 0;                                # eq83
