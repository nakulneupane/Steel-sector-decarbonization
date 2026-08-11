# Variables

# Coke oven
var coke_power_in{T}            >= 0;  # X[1]
var coking_coal_in{T}           >= 0;  # X[2]
var coke_breeze_out{T}          >= 0;  # X[3]
var tar_out{T}                  >= 0;  # X[4]
var cog_out{T}                  >= 0;  # X[5]
var cdq_power_out{T}            >= 0;  # X[6]
var cokeov_cog_in{T}            >= 0;  # X[7]
var cokeov_bfg_in{T}            >= 0;  # X[8]

# Sinter plant
var sinter_power_in{T}          >= 0;  # X[9]
var sinter_lime_in{T}           >= 0;  # X[10]
var sinter_fineore_in{T}        >= 0;  # X[11]
var sinter_breeze_in{T}         >= 0;  # X[12]
var sinter_biochar_in{T}        >= 0;  # X[13]
var sinterwaste_power_out{T}    >= 0;  # X[14]
var sg_out{T}                   >= 0;  # X[15]

# Pellets plant (Blast furnace)
var pellets_bf_power{T}         >= 0;  # X[16]
var pellets_fineore_bf{T}       >= 0;  # X[17]

# Blast furnace
var bf_power_in{T}              >= 0;  # X[18]
var bf_sinter_in{T}             >= 0;  # X[19]
var bf_lime_in{T}               >= 0;  # X[20]
var bf_slag_out{T}              >= 0;  # X[21]
var bf_pellets_in{T}            >= 0;  # X[22]
var bf_lumpore_in{T}            >= 0;  # X[23]
var bfg_in{T}                   >= 0;  # X[24]
var bf_cog_in{T}                >= 0;  # X[25]
var bfg_out{T}                  >= 0;  # X[26]
var bf_trt_out{T}               >= 0;  # X[27]
var bf_coalpci_in{T}            >= 0;  # X[28]
var bf_biopci_in{T}             >= 0;  # X[29]
var bf_coke_in{T}               >= 0;  # X[30]
var bf_h2_in{T}                 >= 0;  # X[31]
var bf_hot_metal{T}             >= 0;  # X[32]

# Basic Oxygen Furnace (BOF)
var bof_power_in{T}             >= 0;  # X[33]
var bof_scrap_in{T}             >= 0;  # X[34]
var bof_lime_in{T}              >= 0;  # X[35]
var bof_slag_out{T}             >= 0;  # X[36]
var bofgas_out{T}               >= 0;  # X[37]
var steel_bof{T}                >= 0;  # X[38]
var bof_cog_in{T}               >= 0;  # X[39]

# Pellets (Coal DRI)
var pellets_fineore_coaldri{T}  >= 0;  # X[40]
var pellets_power_coaldri{T}    >= 0;  # X[41]

# Pellets (NG DRI)
var pellets_fineore_ngdri{T}    >= 0;  # X[42]
var pellets_power_ngdri{T}      >= 0;  # X[43]

# Pellets (H2 DRI)
var pellets_fineore_h2dri{T}    >= 0;  # X[44]
var pellets_power_h2dri{T}      >= 0;  # X[45]

# Coal DRI
var coaldri_output{t in T}      >= 0,  <= dem[t];  # X[46] 
var coaldri_dri_out{T}          >= 0;  # X[47] DRI (t) produced by the coal-DRI shaft
var coaldri_scrap_in{T}         >= 0;  # X[48] scrap (t) blended into the coal route's EAF charge
var coaldri_pellets_in{T}       >= 0;  # X[49]
var coaldri_coal_in{T}          >= 0;  # X[50]
var coaldri_power_in{T}         >= 0;  # X[51]
var coaldri_lumpore_in{T}       >= 0;  # X[52]

# NG DRI
var ngdri_output{t in T}        >= 0,  <= dem[t];  # X[53]
var ngdri_dri_out{T}            >= 0;  # X[54] DRI (t) produced by the NG-DRI shaft
var ngdri_scrap_in{T}           >= 0;  # X[55] scrap (t) blended into the NG route's EAF charge
var ngdri_pellets_in{T}         >= 0;  # X[56]
var ngdri_ng_in{T}              >= 0;  # X[57]
var ngdri_power_in{T}           >= 0;  # X[58]
var ngdri_lumpore_in{T}         >= 0;  # X[59]

# H2 DRI
var h2dri_output{T}             >= 0;  # X[60]
var h2dri_dri_out{T}            >= 0;  # X[61] DRI (t) produced by the H2-DRI shaft
var h2dri_scrap_in{T}           >= 0;  # X[62] scrap (t) blended into the H2 route's EAF charge
var h2dri_pellets_in{T}         >= 0;  # X[63]
var h2dri_h2_in{T}              >= 0;  # X[64]
var h2dri_power_in{T}           >= 0;  # X[65]
var h2dri_lumpore_in{T}         >= 0;  # X[66]

# EAF (DRI-based)
var steel_eaf{T}                >= 0;  # X[67]
var dri_eaf_steel_out{T}        >= 0;  # X[68]
var eaf_scrap_in{T}             >= 0;  # X[69]
var eaf_lime_in{T}              >= 0;  # X[70]
var eaf_coal_in{T}              >= 0;  # X[71]
var eaf_power_in{T}             >= 0;  # X[72]
var eaf_electrode_in{T}         >= 0;  # X[73]
var eaf_slag_out{T}             >= 0;  # X[74]
var eafgas_out{T}               >= 0;  # X[75]

# EAF (Scrap-based)
var steel_scrap_eaf{T}          >= 0;  # X[76]
var scrap_eaf_scrap_in{T}       >= 0;  # X[77]
var scrap_eaf_lime_in{T}        >= 0;  # X[78]
var scrap_eaf_coal_in{T}        >= 0;  # X[79]
var scrap_eaf_power_in{T}       >= 0;  # X[80]
var scrap_eaf_electrode_in{T}   >= 0;  # X[81]
var scrap_eaf_slag_out{T}       >= 0;  # X[82]
var scrap_eaf_gas_out{T}        >= 0;  # X[83]

# Steel Balance
var total_steel{T}              >= 0;  # X[84]

# Power Balance
var grid_power_in{T}            >= 0;  # X[85]

# Wasteheat Recovery
var wasteheat_bf_bof{T}         >= 0;  # X[86]
var wasteheat_eaf{T}            >= 0;  # X[87]
var scrap_eaf_wasteheat{T}      >= 0;  # X[88]
var whr_power_generated{T}      >= 0;  # X[89]
var whr_available_gas{T}        >= 0;  # X[90]
var whr_gas_to_power{T}         >= 0;  # X[91] pool GJ routed to WHR power
var whr_gas_to_steam{T}         >= 0;  # X[92] pool GJ routed to CCS regen steam

# Carbon capture
var ccs_bf{T}                   >= 0;  # X[93]
var ccs_cdri{T}                 >= 0;  # X[94]
var ccs_ngdri{T}                >= 0;  # X[95]
var total_ccs{T}                >= 0;  # X[96]
var power_ccs{T}                >= 0;  # X[97] (compression + auxiliaries, grid-powered)
var ccs_steam_whr{T}            >= 0;  # X[98] regen steam (GJ) raised from the waste-heat pool
var ccs_steam_boiler{T}         >= 0;  # X[99] regen steam (GJ) from the gas-fired backup boiler (CO2 emitted)

# Cost
var cost_cokeov{T}              >= 0;  # X[100] - Total cost in cokeoven
var cost_sinter{T}              >= 0;  # X[101] - Total cost in sinter plant
var cost_pellet_bf{T}           >= 0;  # X[102] - Total cost in BF pellets plant
var cost_bf{T}                  >= 0;  # X[103] - Total cost in BF
var cost_bof{T}                 >= 0;  # X[104] - Total cost in BOF
var cost_pellet_coaldri{T}      >= 0;  # X[105] - Total cost in CoalDRI Pellets plant
var cost_pellet_ngdri{T}        >= 0;  # X[106] - Total cost in NGDRI Pellets plant
var cost_pellet_h2dri{T}        >= 0;  # X[107] - Total cost in H2DRI Pellets plant
var cost_coaldri{T}             >= 0;  # X[108] - Total cost in Coal based DRI Plant
var cost_ngdri{T}               >= 0;  # X[109] - Total cost in NG based DRI Plant
var cost_h2dri{T}               >= 0;  # X[110] - Total cost in H2 based DRI Plant
var cost_eaf{T}                 >= 0;  # X[111] - Total cost in DRI based EAF plant
var cost_scrap_eaf{T}           >= 0;  # X[112] - Total cost in Scrap based EAF plant
var whr_cost{T}                 >= 0;  # X[113] - Cost of Waste heat recovery plant
var cost_ccs{T}                 >= 0;  # X[114] - Total cost in carbon capture plant
var total_cost{T}               >= 0;  # X[115] - Total cost

# Emissions
var scope1_bf{T}                >= 0;  # X[116] - Scope 1 CO2 from BF-BOF
var scope1_cdri{T}              >= 0;  # X[117] - Scope 1 CO2 from Coal DRI-EAF
var scope1_ngdri{T}             >= 0;  # X[118] - Scope 1 CO2 from NG DRI-EAF
var scope1_h2dri{T}             >= 0;  # X[119]
var scope1_scrapeaf{T}          >= 0;  # X[120]
var scope1_emissions{T}         >= 0;  # X[121] - Total Scope 1 CO2
var scope2_emissions{T}         >= 0;  # X[122] - Total Scope 2 CO2
var total_emissions{T}          >= 0;  # X[123] - Total CO2 emitted

# Additional decision variables
var co2_capturable_bf{T}        >= 0;  # X[124] physical capturable CO2, BF-BOF route
var co2_capturable_cdri{T}      >= 0;  # X[125] physical capturable CO2, Coal-DRI route
var co2_capturable_ngdri{T}     >= 0;  # X[126] physical capturable CO2, NG-DRI route
var f_bof{T}                    >= 0, <= 1;  # X[127] BF-BOF fraction
var f_eaf{T}                    >= 0, <= 1;  # X[128] DRI-EAF fraction
