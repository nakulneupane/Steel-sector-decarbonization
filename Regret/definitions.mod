
# Crude Steel Production
param base_demand default 152200000;  # Steel production at year 2025
param growth_rate default 0.05;
param dem{t in T} := base_demand * (1 + growth_rate)^(ord(t) - 1);

# TECHNICAL PARAMETERS 
# Global parameters
param ng_e_pell default 200;         # Electricity (kWh) per ton of pellets   
param ng_ore_pell default 1.1;       # Iron ore (ton) per ton of pellets
param ng_cog_cv default 0.018;       # Calorific value (GJ/Nm3) of COG
param ng_bfg_cv default 0.0033;      # Calorific value (GJ/Nm3) of BFG 
param ng_bofg_cv default 0.008;      # Calorific value (GJ/Nm3) of BOFG
param ng_sintgas_cv default 0.0006;  # Calorific value (GJ/Nm3) of sinter
#param ng_biochar_cv default 18;     # Calorific value (GJ/t) of biochar
#param ng_breeze_cv default 28;      # Calorific value (GJ/t) of breeze
#param ng_coke_cv default 30;        # Calorific value (GJ/t) of coke
#param ng_pci_cv default 26;         # Calorific value (GJ/t) of pulverized coal
#param ng_nccoal_cv default 24;      # Calorific value (GJ/t) of non coking coal
#param ng_ccoal_cv default 25;       # Calorific value (GJ/t) of coking coal

# Coke Oven
param n0_e_c default 75;             # Electricity (kWh) per ton of coke     
param n0_cf default 1.47;            # Coal (ton) required per ton of coke      
param n0_br_c default 0.056;         # Breeze produced (ton) per ton of coke                
param n0_tar_c default 0.04;         # Tar produced (ton) per ton of coke  
param n0_cdq_whr default 80;        # Waste heat power (kWh)produced per ton of coke from CDQ
param n0_cog_c default 440;          # Coke Oven Gas (Nm3) formed per ton of coke (mass eqv gas- 0.2 tons)
param n0_rec_cog default 190;        # Recovered COG as fuel(energy) (Nm3/t coke)
param n0_rec_bfg default 270;        # Recovered BFG as fuel (energy) (Nm3/t coke)
# Remaining COG goes to power plant

# Sinter
param n1_e_sint default 50;          # Electricity (kWh) per ton of sinter    
param n1_lime_sint default 0.04;     # Lime (ton)per ton of sinter                              
param n1_ore_sint default 0.9;       # Iron ore (ton) per ton of sinter      
param n1_brz_sint_25 default 0.09;   # Breeze (ton) per ton sinter in 2025                   
param n1_bio_sint_25 default 0;      # Biochar (ton) per ton sinter in 2025  
param n1_brz_sint_50 default 0.058;  # Breeze (ton) per ton sinter by 2050                   
param n1_bio_sint_50 default 0.022;  # Biochar (ton) per ton sinter by 2050
param n1_sintcool_whr default 30;    # Waste heat power (kWh) produced per ton of sinter from sinter cooler and sinter machine    
param n1_sintgas_sint default 1800;  # Sinter gas (Nm3) per ton sinter
#Remaining sinter gas is waste with very low energy value
#Biochar replacement is limited to 20%


# Blast Furnace
param n2_e_hm default 55;            # Electricity (kWh) per ton hot metal  
param n2_sint_hm default 1.15;       # Sinter (ton) per thm                                              
param n2_lime_hm default 0.025;      # Lime (ton) per thm
param n2_slag_hm default 0.3;        # Slag (ton) per thm    
param n2_pel_hm default 0.35;        # Pellets (ton) per thm   
param n2_ore_hm default 0.15;        # Lump ore (ton) per thm   
param n2_bfg_hm default 1500;        # BFG (Nm3) per thm            
param n2_rec_bfg default 500;        # Recovered BFG as fuel (Nm3/thm)   
param n2_rec_cog default 30;         # Recovered COG as fuel (Nm3/thm) 
param n2_trt_whr default 35;         # Top pressure recovery turbine (kWh/thm)   
param n2_coalpci_hm_25 default 0.15; # PCI (ton) per thm in 2025 
param n2_biopci_hm_25 default 0;     # Biomass injection (ton) per thm in 2025
param n2_coalpci_hm_50 default 0.16; # PCI (ton) per thm by 2050
param n2_biopci_hm_50 default 0.053; # Biomass injection (ton) per thm by 2050
param n2_coke_hm_25 default 0.53;    # Coke (ton) per thm in 2025 
param n2_coke_hm_50 default 0.48;    # Coke (ton) per thm by 2050 (+0.04 vs 0.44: makes up the removed BF H2 co-injection, ~3 t coke / t H2 reduction-equivalent)
param n2_h2_hm_25 default 0;         # Hydrogen in blast furnace in 2025 (t/thm)
param n2_h2_hm_50 default 0;         # Hydrogen in blast furnace by 2050 (t/thm) -- BF H2 co-injection removed; H2-DRI is the only H2 consumer
#Biochar replacement is limited to 20%
#Remaining BFG goes to power plant              


# BOF
param n3_e_bof default 174;         # Electricity (kWh) per ton crude steel from BOF
param n3_metallic_bof default 1.1;  # Total metallic charge (hot metal + scrap, ton) per tCS in BOF
param n3_ls_bof default 0.075;      # Limestone (ton) per tCS in BOF
param n3_sl_bof default 0.1;        # Slag (ton) per tCS in BOF
param n3_bofg_bof default 100;      # BOFG gas (Nm3) formed per tCS in BOF
param n3_rec_cog default 65;        # Recovered COG as fuel (Nm3/tCS)

#All BOFG gas assumed being routed to power plant
#Converting power plant streams to electricity and subtracting from energy input will 
#reduce specific energy consumption

#Coal DRI
param n4_e_dri default 217;         # Electricity (kWh) per ton DRI (100 base + 117 for coal-DRI's IF-heavy secondary: 129 kWh/tCS / 1.1 t-DRI)
param n4_pel_dri default 1.5;       # Pellets (tons) per ton DRI 
param n4_ore_dri default 0.1;       # Ore (tons) per ton DRI 
param n4_c_dri default 1;           # Coal (tons) per ton DRI                 

# NG DRI
param n5_e_dri default 120;         # Electricity (kWh) per ton DRI 
param n5_pel_dri default 1.5;       # Pellets (tons) per ton DRI  
param n5_ore_dri default 0.1;       # Ore (tons) per ton DRI 
param n5_ng_dri default 0.35;       # Natural gas (tons) per ton DRI      


#H2 DRI
param n6_e_dri default 110;         # Electricity (kWh) per ton DRI 
param n6_pel_dri default 1.5;       # Pellets (tons) per ton DRI 
param n6_ore_dri default 0.1;       # Ore (tons) per ton DRI     
param n6_h2_dri default 0.07;       # Hydrogen (tons) per ton DRI (conservative incl. energy efficiency / shaft losses)

# EAF (DRI-Based)
param n7_e_eaf {t in T} :=
    664;    # Electricity (kWh) per tCS: DRI-EAF/IF weighted on the gas-DRI all-EAF basis (coal-DRI's extra IF power is carried in n4_e_dri)
param n7_dri_ratio default 1.1;            # Metallic charge (ton DRI + scrap) per tCS in DRI-EAF
param n7_eltrd default 0.003;              # Electrode (ton) per tCS  
param n7_ls default 0.06;                  # Limestone (ton) per tCS 
param n7_cs default 0.01;                  # Coal (ton) per tCS  
param n7_ss default 0.15;                  # Slag (ton) per tCS   
param n7_eafg default 3;                   # EAF Gas (GJ) per tCS                           
 

# EAF (Scrap-Based)
param n8_e_eaf {t in T} :=
    785; # Electricity (kWh) per tCS: scrap secondary, 75% IF @825 + 25% EAF @664 weighted (India IF-heavy secondary route)
param n8_phi_eaf default 1.1;            # Scrap (ton) per tCS
param n8_eltrd default 0.003;            # Electrode (ton) per tCS  
param n8_ls default 0.06;                # Limestone (ton) per tCS 
param n8_cs default 0.01;                # Coal (ton) per tCS 
param n8_ss default 0.15;                # Slag (ton) per tCS 
param n8_eafg default 3;                 # EAF Gas (GJ) per tCS                          
param phi0_bof      default 0.09;    # 2025 baseline scrap share of BOF metallic charge
param phi0_cdri     default 0.382;   # 2025 baseline scrap share, Coal DRI-EAF/IF charge
param phi0_ngdri    default 0.13;    # 2025 baseline scrap share, NG DRI-EAF charge
param phi_min_bof   default 0.05;    # min scrap share of BF-BOF charge (converter coolant)
param phi_min_cdri  default 0;       # min scrap share, Coal DRI-EAF (none required)
param phi_min_ngdri default 0;       # min scrap share, NG DRI-EAF
param phi_min_h2dri default 0;       # min scrap share, H2 DRI-EAF
param phi_max_bof   default 0.20;    # max scrap share of BF-BOF metallic charge
param phi_max_cdri  default 0.40;    # max scrap share of Coal DRI-EAF charge
param phi_max_ngdri default 0.40;    # max scrap share of NG DRI-EAF charge
param phi_max_h2dri default 0.40;    # max scrap share of H2 DRI-EAF charge
param blend_ramp    default 0.05;


param theta_tech default 0;              # global tech learning speed (H2 axis)
param theta_grid default 0;              # India grid outcome speed (EF + tariff)
param grid_price_start    default 0.07;    # 2025 grid tariff, $/kWh (fixed anchor)
param grid_price_end_slow default 0.085;   # 2050 grid tariff, slow (straddles flat)
param grid_price_end_fast default 0.055;   # 2050 grid tariff, fast
param grid_ef_end_slow    default 0.0006; # 2050 grid EF, slow (tCO2/kWh)
param grid_ef_end_fast    default 0.0003; # 2050 grid EF, fast
param h2elec_capex_end_slow default 550;   # 2050 electrolyser capex $/kW, slow
param h2elec_capex_end_fast default 150;   # 2050 electrolyser capex $/kW, fast (DOE optimistic)
param re_capex_end_slow   default 600;     # 2050 renewable capex $/kW, slow
param re_capex_end_fast   default 200;     # 2050 renewable capex $/kW, fast (IRENA optimistic solar)
param theta_ccs default 0;                 # capture-plant learning speed
param ccs_capex_fall_slow default 0.30;    # 2050 overnight-capex decline vs 2025, slow
param ccs_capex_fall_fast default 0.80;    # 2050 overnight-capex decline vs 2025, fast

# Waste Heat Recovery
param n9_eta default 0.15;                              # WHRS efficiency including losses
param n9_whr {t in T} :=
    0.05 +(0.3 - 0.05) * (t - 2025) / 25;               # WHRS penetration level from 30% in 2025 to 70% by 2050
param n9_grid_ef_start default 0.000886; #0.000757 from grid having 36% share and 0.00096 from CPP having 64% share
param n9_grid_ef_end default
    grid_ef_end_slow + theta_grid * (grid_ef_end_fast - grid_ef_end_slow);   # theta_grid-coupled (0.0003 at 0.5)
param n9_grid_ef{t in T} :=
    n9_grid_ef_start + (n9_grid_ef_end - n9_grid_ef_start) * (t - 2025) /25;   # Grid emission factor from 2025 to 2050

# Carbon capture
param n10_ccs_eta default 0.85;                        # Carbon capture efficiency                      


# COST PARAMETERS 
#Global parameters (all costs are in $)
param ng_cost_ccoal default 184;          # Cost per ton of coking coal
param ng_cost_power{t in T} :=
    grid_price_start
    + ( (grid_price_end_slow + theta_grid*(grid_price_end_fast - grid_price_end_slow))
        - grid_price_start ) * (t - 2025)/25;
param ng_credit_power default 0.03;       # Selling cost per kWh of generated power
param ng_cost_fineore default 65;         # Cost per ton of fineore
param ng_cost_lime default 60;            # Cost per ton of lime
param ng_cost_biochar default 60;         # Cost per ton of biomass
param ng_capex_pell default 10;           # CAPEX of pellets plant per tCS production
param ng_cost_lumpore default 70;         # Cost per ton of lumpore
param ng_cost_pcoal default 110;          # Cost per ton of PCI coal
param ng_credit_slag default 15;          # Selling cost per ton of slag
param ng_cost_scrap default 350;          # Cost per ton of scrap
param ng_cost_ncoal default 98;          # Cost per ton of non coking coal
param n0_credit_breeze default 55;        # Selling cost per ton of breeze
param n0_credit_tar default 20;           # Selling cost per ton of tar
param n0_capex default 40;                # CAPEX of cokeoven per tCS rpoduction
param n1_cost_breeze default 85;          # Cost per ton of breeze                         
param n1_capex default 30;                # CAPEX of sinter plant per tCS production
param n2_capex default 80;               # CAPEX of blast furnace per tCS production
param n3_capex default 40;                # CAPEX of BOF per tCS production                              
param n4_capex_coal default 110;          # CAPEX of Coal-DRI per tCS production
param n5_capex_ng := 90;                  # CAPEX of NG-DRI per tCS production
param n5_cost_NG {t in T} default 10;     # Cost of natural gas per MMBtu
param ng_h2_start_year default 2040;
param n6_capex_h2{t in T} :=
    if t <= 2025 then 120
    else 120+ (90-120) * (t-2025)/25;     # CAPEX of H2-DRI per tCS from 2025 to 2050
param n7_capex default 70;                # CAPEX of EAF plant (DRI based) per tCS
param n7_cost_electrode default 600;      # Cost per ton of electrode
param n8_capex default 70;                # CAPEX of EAF plant (Scrap-based) per tCS     
param n8_cost_electrode default 600;      # Cost per ton of electrode 
param n9_whr_capex default 0.009;         # CAPEX of WHR system per kWh of power generated
param n9_whr_opex default 0.003;          # OPEX of WHR system per kWh of power generated
param n10_ccs_cost_start default 125;
param n10_ccs_cost_end default 75;   # DEPRECATED (no effect); CCS 2050 axis = theta_ccs
param carbon_tax default 0; 
param labor_cost default 20;              # Labor cost per tCS
param maintenance_cost default 15;        # Maintenance cost per tCS
param other_opex default 10;              # Other opex per tCS

# OTHER PARAMETERS
param real_discount_rate := 0.06;
param n8_scrap_rate default 0.06;
param n8_scrap_limit{t in T};
param n5_ng_cap {T};
param ccoal_cap {T} default 1e12;


# CAPACITY-EXPANSION PARAMETERS 
param cap0_bof   default 90.00e6;             # steel_bof
param cap0_cdri  default 104.10e6;            # coaldri_output (coal-DRI + IF fleet)
param cap0_ngdri default 12.90e6;             # ngdri_output   (crude steel)
param cap0_h2dri default 0;                   # h2dri_output   (none in 2025)
param cap0_scrap default 0.75e6;              # steel_scrap_eaf (dedicated 100% scrap-EAF)

# Asset lifetimes (yr) 
param life_bof   default 25;
param life_cdri  default 20;
param life_ngdri default 20;
param life_h2dri default 25;
param life_scrap default 15;

# capacity-addition ceiling 

param cap_add_common default 10e6;
param util_min_bof   default 0.85;
param util_min_cdri  default 0.75;
param util_min_ngdri default 0.70;
param util_min_h2dri default 0.70;
param util_min_scrap default 0.60;
param util_max default 0.95;


param fopex_bof   default labor_cost + maintenance_cost;
param fopex_cdri  default labor_cost + maintenance_cost;
param fopex_ngdri default labor_cost + maintenance_cost;
param fopex_h2dri default labor_cost + maintenance_cost;
param fopex_scrap default labor_cost + maintenance_cost;

# Capital recovery factor CRF(L) at the real discount rate.
param crf_bof   := real_discount_rate*(1+real_discount_rate)^life_bof  /((1+real_discount_rate)^life_bof  -1);
param crf_cdri  := real_discount_rate*(1+real_discount_rate)^life_cdri /((1+real_discount_rate)^life_cdri -1);
param crf_ngdri := real_discount_rate*(1+real_discount_rate)^life_ngdri/((1+real_discount_rate)^life_ngdri-1);
param crf_h2dri := real_discount_rate*(1+real_discount_rate)^life_h2dri/((1+real_discount_rate)^life_h2dri-1);
param crf_scrap := real_discount_rate*(1+real_discount_rate)^life_scrap/((1+real_discount_rate)^life_scrap-1);

# Annualised capital charge per unit route output 
param acapex_bof   := n0_capex + n1_capex + ng_capex_pell + n2_capex + n3_capex;          # $/tCS/yr
param acapex_cdri  := n4_capex_coal + ng_capex_pell + n7_capex;                           # $/tCS/yr
param acapex_ngdri := n5_capex_ng   + ng_capex_pell + n7_capex;                           # $/tCS/yr
param acapex_h2dri {t in T} := n6_capex_h2[t] + ng_capex_pell + n7_capex;                 # $/tCS/yr
param acapex_scrap := n8_capex;                                                           # $/tCS/yr

#  Overnight capex per unit capacity = annualised charge / CRF.
param ocapex_bof   := acapex_bof   / crf_bof;
param ocapex_cdri  := acapex_cdri  / crf_cdri;
param ocapex_ngdri := acapex_ngdri / crf_ngdri;
param ocapex_h2dri {t in T} := acapex_h2dri[t] / crf_h2dri;
param ocapex_scrap := acapex_scrap / crf_scrap;
param ocapex_scrapchain default 100;
param ocapex_coalchain default 0;     # $/(t-coal/yr)
param ocapex_ngchain   default 0;     # $/(t-NG/yr)

#Structural
param ramp_frac default 0.15;
param sunk default 1;


# CCS retrofit 
param life_ccs default 15;                       # retrofit asset life (yr)
param crf_ccs := real_discount_rate*(1+real_discount_rate)^life_ccs/((1+real_discount_rate)^life_ccs-1);
param ccs_fom_pct default 0.04;                  # fixed O&M as fraction of overnight capex, /yr
param ccs_vopex_solvent default 5;               # solvent makeup, $/tCO2 (placeholder)
param ccs_ts_cost default 20;                    # transport + storage, $/tCO2 (volume cost, NOT %capex)
param ccs_mult_bf    default 1.0;    # baseline (concentrated BFG ~20-25% CO2)
param ccs_mult_cdri  default 1.2;    # leaner coal kiln off-gas -> a bit dearer than BFG
param ccs_kwh_bf     default 130;    # kWh/tCO2, compression + auxiliaries
param ccs_kwh_cdri   default 150;    # leaner -> more blower/aux power
param ccs_steam_bf   default 3.0;    # GJ regen steam per tCO2 (amine, BFG stream)
param ccs_steam_cdri default 3.3;    # leaner -> more regen steam
param ccs_ngdri_proc_share default 0.6;   # share of NG-DRI capturable CO2 in the process stream
param ccs_kwh_ng_proc   default 110;      # process stream: mostly compression
param ccs_kwh_ng_flue   default 170;      # NG flue (~4-8% CO2): leanest -> most aux power
param ccs_steam_ng_proc default 0.3;      # process stream: negligible regen
param ccs_steam_ng_flue default 3.6;      # NG flue: most regen steam per tCO2
param ccs_mult_ng_proc  default 0.5;      # process stream: cheap retrofit
param ccs_mult_ng_flue  default 1.3;      # NG flue: dearest capture plant per tCO2
param ccs_kwh_ngdri   := ccs_ngdri_proc_share*ccs_kwh_ng_proc   + (1-ccs_ngdri_proc_share)*ccs_kwh_ng_flue;
param ccs_steam_ngdri := ccs_ngdri_proc_share*ccs_steam_ng_proc + (1-ccs_ngdri_proc_share)*ccs_steam_ng_flue;
param ccs_mult_ngdri  := ccs_ngdri_proc_share*ccs_mult_ng_proc  + (1-ccs_ngdri_proc_share)*ccs_mult_ng_flue;
param ccs_ref_elec  default 0.07;    # $/kWh used only to back out capex from the anchor
param ccs_ref_steam default 5;       # $/GJ  ditto (~waste-heat steam opportunity cost)
param ccs_boiler_eff default 0.85;   # backup boiler efficiency (GJ steam / GJ NG fuel)
param ng_gj_per_mmbtu := 1.055;      # GJ per MMBtu (NG price unit conversion)
param ng_co2_gj default 0.0521;      # tCO2 per GJ NG fuel (= 0.055 t/MMBtu)
param whr_steam_eff default 0.85;    # waste-heat pool gas (GJ) -> LP steam (GJ)
param ocapex_ccs_2025 :=
    max( n10_ccs_cost_start
         - ccs_ts_cost - ccs_vopex_solvent
         - ccs_kwh_bf*ccs_ref_elec - ccs_steam_bf*ccs_ref_steam, 10 )
    / (crf_ccs + ccs_fom_pct);                    # overnight $ per (tCO2/yr), ~531 central

param ccs_capex_fall := ccs_capex_fall_slow + theta_ccs*(ccs_capex_fall_fast - ccs_capex_fall_slow);
param ocapex_ccs {t in T} := ocapex_ccs_2025 * (1 - ccs_capex_fall*(t - 2025)/25);
param fom_ccs    {t in T} := ccs_fom_pct * ocapex_ccs[t];   # fixed O&M $/tCO2-cap/yr


# GREEN-H2 SUPPLY CHAIN: electrolyser + dedicated renewable (sunk capacity)
param h2_kwh_per_t default 55000;     # electrolyser electricity, kWh per t H2 (~55 kWh/kg incl BoP)
param re_cf        default 0.35;      # dedicated renewable capacity factor (India solar/wind hybrid)
param h2_opex{t in T} default 300;    # residual H2 variable opex (water + stack O&M), $/t H2
param h2_capex_mult default 1;
param h2elec_capex_start default 850;
param h2elec_capex_kw{t in T} :=
    h2elec_capex_start
    + ( (h2elec_capex_end_slow + theta_tech*(h2elec_capex_end_fast - h2elec_capex_end_slow))
        - h2elec_capex_start )*(t-2025)/25;
param life_h2elec default 15;         # electrolyser plant life (incl stack replacement)
param crf_h2elec := real_discount_rate*(1+real_discount_rate)^life_h2elec/((1+real_discount_rate)^life_h2elec-1);
param fopex_h2elec default 400;       # fixed O&M, $/(t-H2/yr)/yr (placeholder ~3% of capex)
param re_capex_kw{t in T} :=
    800 + ( (re_capex_end_slow + theta_tech*(re_capex_end_fast - re_capex_end_slow))
            - 800 )*(t-2025)/25;
param life_re default 25;             # renewable plant life
param crf_re := real_discount_rate*(1+real_discount_rate)^life_re/((1+real_discount_rate)^life_re-1);
param fopex_h2re default 15;          # fixed O&M, $/kW/yr (placeholder ~2% of capex)
param lcoh_2025_target default 5000;  # $/t H2 (= $5/kg) calibration anchor
param h2_kw_per_t := h2_kwh_per_t/(8760*re_cf);   # kW of dedicated RE per (t-H2/yr)
param h2_lcoh_base_2025 :=            # 2025 LCOH of the bare build-up (no firming, mult=1)
      h2elec_capex_kw[2025]/(8760*re_cf/h2_kwh_per_t) * crf_h2elec + fopex_h2elec
    + h2_kw_per_t * (re_capex_kw[2025]*crf_re + fopex_h2re)
    + h2_opex[2025];
param h2_firm_capex{t in T} :=        # overnight $ per (t-H2/yr), declines with electrolyser capex
    max(lcoh_2025_target - h2_lcoh_base_2025, 0)/crf_h2elec
    * h2elec_capex_kw[t]/h2elec_capex_kw[2025];

param ocapex_h2elec{t in T} := h2_capex_mult * ( h2elec_capex_kw[t]/(8760*re_cf/h2_kwh_per_t)
                                                 + h2_firm_capex[t] );
param acapex_h2elec{t in T} := ocapex_h2elec[t] * crf_h2elec;   # annualized (for the 1-sunk branch)
param ocapex_h2re{t in T} := h2_capex_mult * re_capex_kw[t];    # overnight $/kW (charged on build, in kW)
param acapex_h2re{t in T} := ocapex_h2re[t] * crf_re;           # annualized $/kW/yr (for the 1-sunk branch)
param h2_ramp_mode  default 2;          # 0 none (inf ceiling) | 1 linear | 2 gaussian (default, realistic)
param H2_BIGM       := 1e10;            # deactivates whichever limiter is off (~300x max cap)
param h2_ref_cap    default 4000000;
param h2_peak_rate  := 0.25;            # the pinned mode-2 peak rate (base(peak)+surge = 25%)
param h2_base_start := 0.00;            # mode 2 baseline coeff at 2025 (x h2_ref_cap, per yr)
param h2_base_end   := 0.05;            # mode 2 baseline coeff at 2050 (rising -> capital efficiency)
param h2_gauss_sigma := 2;              # Gaussian width (years); narrower -> sharper ramp, surge concentrated at peak
param h2_base{t in T} := h2_base_start + (h2_base_end - h2_base_start)*(t-2025)/25;  # rising baseline rate
param h2_peak_year  default 2035;
