# =====================================================================
# template.mod -- backdrop for the Feasibility Drivers (Sobol) study.
#
# Include AFTER core/model.mod. This study varies ALL EIGHT structural
# axes plus the emissions target -- there is no separate fixed backdrop
# to declare here, unlike h2_delay/fuel_availability. run.py applies
# every axis value directly via `let` (and the ccoal/ng axis-file
# includes) per cell; this file exists only so every study folder in
# structural/ follows the same "template.mod declares the backdrop"
# convention, and to hold the two Section-B learning-rate constants that
# stay fixed even though every structural axis moves.
# =====================================================================

let theta_tech          := 0.5;   # H2/RE learning -- Section B, not Section A
let theta_ccs           := 0.5;   # CCS learning   -- Section B, not Section A
let whr_ccs_integration := 1;
