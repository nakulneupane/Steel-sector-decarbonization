# =====================================================================
# fuel_availability.mod -- fixed backdrop for the Fuel Availability study.
#
# Include AFTER core/model.mod. Fixes everything the Fuel Availability
# figure does NOT vary; run_fuel_availability.py includes the ccoal/ng
# axis files (which DO vary) and sets ng_h2_start_year (which also
# varies) per cell.
#
# Backdrop matches fuelavail_assumptions.txt: emissions target 1.8,
# scrap growth 6%/yr, grid learning theta_grid=0.5, H2 supply ramp at
# "medium" (4 Mt/yr), shared build budget at "mid" (30 Mt/yr), legacy
# fleet on run-life retirement, learning rates at their Section-A
# default (0.5).
# =====================================================================

let avg_emi           := 1.8;
let n8_scrap_rate     := 0.06;
let theta_grid        := 0.5;
let h2_ref_cap        := 4000000;    # ramp = medium
let cap_add_common    := 30000000;   # build_cap = mid
let legacy_phaseout   := 0;          # run-life
let theta_tech        := 0.5;
let theta_ccs         := 0.5;
let whr_ccs_integration := 1;
