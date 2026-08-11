# Technology learning
let theta_grid := 0.5;    # 1 means clean/mature grid ecosystem
let theta_tech := 0.5;    # 1 means cheap/matured hydrogen ecosystem
let theta_ccs  := 0.5;    # 1 means cheap/matured CCS ecosystem

# Crude Steel Production
let base_demand := 152200000;
let growth_rate := 0.05;
param avg_emi   default 1.8;  # cumulative average CO2-intensity CAP, tCO2/tCS

# NG DRI
let {t in T} n5_cost_NG[t] := 10;
# Shock period (2035–2040): only for shock case it is 1.5 times
# let {t in 2035..2040} n5_cost_NG[t] := 22.5;

# H2 DRI
let ng_h2_start_year := 2030;
param H2_cap := 1500000; # Capacity slab per year
s.t. No_H2_Before{t in T: t < ng_h2_start_year}:
    h2dri_h2_in[t] = 0;
let h2_peak_year := ng_h2_start_year + 5; # H2 peak year

# Scrap
let n8_scrap_rate := 0.06;      # Assumed annual growth rate of scrap
let ng_cost_scrap :=350;        # Assumed scrap cost
let n8_scrap_limit[first(T)] := 37000000;
let {t in T: ord(t) > 1}
    n8_scrap_limit[t] :=
        n8_scrap_limit[prev(t)] * (1 + n8_scrap_rate);  # scrap cap

# CCS
let n10_ccs_cost_start := 125;   # CCS anchor 2025 (capex+O&M+energy+solvent+T&S)

# NG cap (Shock case)
let n5_ng_cap[2025] := 5348550;
let n5_ng_cap[2026] := 5856675;
let n5_ng_cap[2027] := 6343875;
let n5_ng_cap[2028] := 6851550;
let n5_ng_cap[2029] := 7526175;
let n5_ng_cap[2030] := 8293950;
let n5_ng_cap[2031] := 8967150;
let n5_ng_cap[2032] := 9523425;
let n5_ng_cap[2033] := 10172625;
let n5_ng_cap[2034] := 10928175;
let n5_ng_cap[2035] := 7842225;
let n5_ng_cap[2036] := 7999125;
let n5_ng_cap[2037] := 8188200;
let n5_ng_cap[2038] := 8300550;
let n5_ng_cap[2039] := 8411025;
let n5_ng_cap[2040] := 8708775;
let n5_ng_cap[2041] := 11721825;
let n5_ng_cap[2042] := 12549000;
let n5_ng_cap[2043] := 13532700;
let n5_ng_cap[2044] := 14522775;
let n5_ng_cap[2045] := 15491025;
let n5_ng_cap[2046] := 16623450;
let n5_ng_cap[2047] := 17940750;
let n5_ng_cap[2048] := 19201050;
let n5_ng_cap[2049] := 20696025;
let n5_ng_cap[2050] := 21911625;
