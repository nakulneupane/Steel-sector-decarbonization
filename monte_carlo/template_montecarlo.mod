# Monte Carlo backdrop shared by every solve in this study: the two
# constants held fixed across all 50 shared cost/tech draws and every
# emission target. Everything else (structural axes, cost/tech draws,
# avg_emi) is set per-solve by run_montecarlo.py.
let whr_ccs_integration := 1;
let real_discount_rate := 0.06;
