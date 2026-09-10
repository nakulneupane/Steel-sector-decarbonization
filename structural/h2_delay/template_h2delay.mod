# =====================================================================
# h2_delay.mod -- fixed backdrop for the H2 Delay study.
#
# Include AFTER core/model.mod. Fixes everything the H2 Delay figure does
# NOT vary; run_h2_delay.py sets the three axes that DO vary (avg_emi,
# h2_ref_cap via the "H2 supply" level, ng_h2_start_year) per cell.
#
# Backdrop matches h2delay_assumptions.txt: coking coal and natural gas
# both abundant, scrap growth 6%/yr, grid learning theta_grid=0.5, shared
# build budget at "mid" (30 Mt/yr), legacy fleet on run-life retirement,
# and the two Section-B learning rates held at their Section-A default
# (0.5) since this is a structural, not Monte Carlo, study.
# =====================================================================

include structural/axes/ccoal_abundant.mod;
include structural/axes/ng_policy.mod;

let n8_scrap_rate     := 0.06;
let theta_grid        := 0.5;
let cap_add_common    := 30000000;   # build_cap = mid
let legacy_phaseout   := 0;          # run-life
let theta_tech        := 0.5;
let theta_ccs         := 0.5;
let whr_ccs_integration := 1;
