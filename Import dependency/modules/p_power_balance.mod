# Total Power Balance
# NOTE: the green-H2 electrolyser load is NOT included here. It is supplied by
# dedicated renewables (cap_h2re, sized to cover it in v_capacity.mod), behind the
# meter, so it draws no grid power and incurs no grid-EF Scope-2, this is what
# keeps the hydrogen green. The electrolyser CAPITAL is explicit (sunk builds);
# only its electricity is kept off the shared grid balance.

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
