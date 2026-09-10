# =====================================================================
# template.mod -- fixed backdrop for the Sectoral Synergy (grid-offset)
# study.
#
# Include AFTER core/model.mod. Matches the master matrix's baseline
# cell: coking coal and natural gas both abundant, emissions target
# fixed at 1.8 (this study does not vary the target -- it asks, at a
# fixed 1.8 target, how much grid decarbonization is REQUIRED to stay
# feasible), shared build budget at "mid" (30 Mt/yr), H2 supply ramp at
# "medium" (4 Mt/yr), legacy fleet on run-life retirement, and the two
# Section-B learning rates at their Section-A default (0.5).
#
# VARYING per cell (set by run.py): n8_scrap_rate, ng_h2_start_year,
# and theta_grid itself -- theta_grid is the quantity being bisected,
# not a fixed backdrop value.
# =====================================================================

include structural/axes/ccoal_abundant.mod;
include structural/axes/ng_policy.mod;

let avg_emi              := 1.8;
let cap_add_common       := 30000000;   # build_cap = mid
let h2_ref_cap           := 4000000;    # ramp = medium
let legacy_phaseout      := 0;          # run-life
let theta_tech           := 0.5;
let theta_ccs            := 0.5;
let whr_ccs_integration  := 1;
