# Total Steel Balance
s.t. steel_balance{t in T}:
    steel_eaf[t] + steel_bof[t] + steel_scrap_eaf[t] - total_steel[t]= 0;    # eq77
