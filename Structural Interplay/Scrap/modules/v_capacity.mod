
# Build (capacity added in year t)
var build_bof   {T} >= 0;
var build_cdri  {T} >= 0;
var build_ngdri {T} >= 0;
var build_h2dri {T} >= 0;
var build_scrap {T} >= 0;

# Surviving incumbent (2025) fleet
var legacy_bof   {T} >= 0;
var legacy_cdri  {T} >= 0;
var legacy_ngdri {T} >= 0;
var legacy_h2dri {T} >= 0;
var legacy_scrap {T} >= 0;

# Total installed capacity
var cap_bof   {T} >= 0;
var cap_cdri  {T} >= 0;
var cap_ngdri {T} >= 0;
var cap_h2dri {T} >= 0;
var cap_scrap {T} >= 0;

# Annual cost pieces fed to total_cost_def
var capex_cost   {T} >= 0;   # overnight capex booked on this year's builds
var fixopex_cost {T} >= 0;   # fixed O&M on installed capacity

# SUPPLY-CHAIN 
var scrapchain_cap   {T} >= 0;   # scrap-handling capacity (t scrap/yr)
var build_scrapchain {T} >= 0;   # capacity added this year (t scrap/yr)
var coalchain_cap    {T} >= 0;   # coal supply capacity (t coal/yr, all coal types)
var build_coalchain  {T} >= 0;
var ngchain_cap      {T} >= 0;   # natural-gas supply capacity (t NG/yr)
var build_ngchain    {T} >= 0;

# Green-H2 supply chain
var build_h2elec {T} >= 0;   # electrolyser capacity added (t-H2/yr)
var cap_h2elec   {T} >= 0;   # installed electrolyser capacity (t-H2/yr)
var build_h2re   {T} >= 0;   # dedicated renewable capacity added (kW)
var cap_h2re     {T} >= 0;   # installed dedicated renewable capacity (kW)

# Cap = surviving legacy + builds still within their life L.
# A build in year j contributes until year j+L-1, then retires automatically.
s.t. cap_def_bof{t in T}:
    cap_bof[t] = legacy_bof[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_bof+1}   build_bof[j];
s.t. cap_def_cdri{t in T}:
    cap_cdri[t] = legacy_cdri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_cdri+1}  build_cdri[j];
s.t. cap_def_ngdri{t in T}:
    cap_ngdri[t] = legacy_ngdri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_ngdri+1} build_ngdri[j];
s.t. cap_def_h2dri{t in T}:
    cap_h2dri[t] = legacy_h2dri[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_h2dri+1} build_h2dri[j];
s.t. cap_def_scrap{t in T}:
    cap_scrap[t] = legacy_scrap[t]
      + sum{j in T: ord(j) <= ord(t) and ord(j) >= ord(t)-life_scrap+1} build_scrap[j];

# Legacy retirement
s.t. legacy_ceil_bof  {t in T}: legacy_bof[t]   <= cap0_bof   * (2050 - t)/25;
s.t. legacy_ceil_cdri {t in T}: legacy_cdri[t]  <= cap0_cdri  * (2050 - t)/25;
s.t. legacy_ceil_ngdri{t in T}: legacy_ngdri[t] <= cap0_ngdri * (2050 - t)/25;
s.t. legacy_ceil_h2dri{t in T}: legacy_h2dri[t] <= cap0_h2dri * (2050 - t)/25;
s.t. legacy_ceil_scrap{t in T}: legacy_scrap[t] <= cap0_scrap * (2050 - t)/25;

s.t. legacy_noninc_bof  {t in T: ord(t)>1}: legacy_bof[t]   <= legacy_bof[prev(t)];
s.t. legacy_noninc_cdri {t in T: ord(t)>1}: legacy_cdri[t]  <= legacy_cdri[prev(t)];
s.t. legacy_noninc_ngdri{t in T: ord(t)>1}: legacy_ngdri[t] <= legacy_ngdri[prev(t)];
s.t. legacy_noninc_h2dri{t in T: ord(t)>1}: legacy_h2dri[t] <= legacy_h2dri[prev(t)];
s.t. legacy_noninc_scrap{t in T: ord(t)>1}: legacy_scrap[t] <= legacy_scrap[prev(t)];

s.t. legacy_init_bof:   legacy_bof[first(T)]   = cap0_bof;
s.t. legacy_init_cdri:  legacy_cdri[first(T)]  = cap0_cdri;
s.t. legacy_init_ngdri: legacy_ngdri[first(T)] = cap0_ngdri;
s.t. legacy_init_h2dri: legacy_h2dri[first(T)] = cap0_h2dri;
s.t. legacy_init_scrap: legacy_scrap[first(T)] = cap0_scrap;

s.t. cap_lim_bof  {t in T}: steel_bof[t]       <= (if h2_ramp_mode = 0 then 1 else util_max) * cap_bof[t];
s.t. cap_lim_cdri {t in T}: coaldri_output[t]  <= (if h2_ramp_mode = 0 then 1 else util_max) * cap_cdri[t];
s.t. cap_lim_ngdri{t in T}: ngdri_output[t]    <= (if h2_ramp_mode = 0 then 1 else util_max) * cap_ngdri[t];
s.t. cap_lim_h2dri{t in T}: h2dri_output[t]    <= (if h2_ramp_mode = 0 then 1 else util_max) * cap_h2dri[t];
s.t. cap_lim_scrap{t in T}: steel_scrap_eaf[t] <= (if h2_ramp_mode = 0 then 1 else util_max) * cap_scrap[t];

# Per-route capacity-addition ceiling
s.t. cap_add_bof  {t in T: t > first(T)}: build_bof[t]   <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);
s.t. cap_add_cdri {t in T: t > first(T)}: build_cdri[t]  <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);
s.t. cap_add_ngdri{t in T: t > first(T)}: build_ngdri[t] <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);
s.t. cap_add_scrap{t in T: t > first(T)}: build_scrap[t] <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);

s.t. cap_add_bof0:   build_bof[first(T)]   = 0;
s.t. cap_add_cdri0:  build_cdri[first(T)]  = 0;
s.t. cap_add_ngdri0: build_ngdri[first(T)] = 0;
s.t. cap_add_scrap0: build_scrap[first(T)] = 0;

# Minimum capacity utilisation
s.t. min_util_bof  {t in T: t > first(T)}: steel_bof[t]       >= (if h2_ramp_mode = 0 then 0 else util_min_bof)   * cap_bof[t];
s.t. min_util_cdri {t in T: t > first(T)}: coaldri_output[t]  >= (if h2_ramp_mode = 0 then 0 else util_min_cdri)  * cap_cdri[t];
s.t. min_util_ngdri{t in T: t > first(T)}: ngdri_output[t]    >= (if h2_ramp_mode = 0 then 0 else util_min_ngdri) * cap_ngdri[t];
s.t. min_util_h2dri{t in T: t > first(T)}: h2dri_output[t]    >= (if h2_ramp_mode = 0 then 0 else util_min_h2dri) * cap_h2dri[t];
s.t. min_util_scrap{t in T: t > first(T)}: steel_scrap_eaf[t] >= (if h2_ramp_mode = 0 then 0 else util_min_scrap) * cap_scrap[t];

# scrap-chain 
s.t. scrapchain_legacy{t in T: ord(t) = 1}:
    scrapchain_cap[t] = bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t];
s.t. scrapchain_cover{t in T: ord(t) > 1}:
    scrapchain_cap[t] >= bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t];
s.t. scrapchain_mono{t in T: ord(t) > 1}:
    scrapchain_cap[t] >= scrapchain_cap[prev(t)];
s.t. scrapchain_build_def{t in T: ord(t) > 1}:
    build_scrapchain[t] >= scrapchain_cap[t] - scrapchain_cap[prev(t)];

# coal supply chain
s.t. coalchain_legacy{t in T: ord(t) = 1}:
    coalchain_cap[t] = coking_coal_in[t] + bf_coalpci_in[t] + coaldri_coal_in[t]
                     + eaf_coal_in[t] + scrap_eaf_coal_in[t];
s.t. coalchain_cover{t in T: ord(t) > 1}:
    coalchain_cap[t] >= coking_coal_in[t] + bf_coalpci_in[t] + coaldri_coal_in[t]
                      + eaf_coal_in[t] + scrap_eaf_coal_in[t];
s.t. coalchain_mono{t in T: ord(t) > 1}:
    coalchain_cap[t] >= coalchain_cap[prev(t)];
s.t. coalchain_build_def{t in T: ord(t) > 1}:
    build_coalchain[t] >= coalchain_cap[t] - coalchain_cap[prev(t)];

# natural-gas supply chain
s.t. ngchain_legacy{t in T: ord(t) = 1}:
    ngchain_cap[t] = ngdri_ng_in[t];
s.t. ngchain_cover{t in T: ord(t) > 1}:
    ngchain_cap[t] >= ngdri_ng_in[t];
s.t. ngchain_mono{t in T: ord(t) > 1}:
    ngchain_cap[t] >= ngchain_cap[prev(t)];
s.t. ngchain_build_def{t in T: ord(t) > 1}:
    build_ngchain[t] >= ngchain_cap[t] - ngchain_cap[prev(t)];

s.t. capex_cost_def{t in T}:
    capex_cost[t] =
      sunk * (   ocapex_bof      * build_bof[t]          # sunk: overnight capex on builds
               + ocapex_cdri     * build_cdri[t]
               + ocapex_ngdri    * build_ngdri[t]
               + ocapex_h2dri[t] * build_h2dri[t]
               + ocapex_scrap    * build_scrap[t]
               + ocapex_scrapchain * build_scrapchain[t]   # scrap collection+yard expansion
               + ocapex_coalchain * build_coalchain[t]     # coal supply-network growth (default 0)
               + ocapex_ngchain   * build_ngchain[t]       # NG supply-network growth  (default 0)
               + ocapex_h2elec[t] * build_h2elec[t]        # green-H2: electrolyser builds
               + ocapex_h2re[t]   * build_h2re[t] )        # green-H2: dedicated renewable builds
    + (1-sunk) * ( acapex_bof    * steel_bof[t]          # not sunk: annualized capex on production
               + acapex_cdri     * coaldri_output[t]
               + acapex_ngdri    * ngdri_output[t]
               + acapex_h2dri[t] * h2dri_output[t]
               + acapex_scrap    * steel_scrap_eaf[t]
               + acapex_h2elec[t] * h2dri_h2_in[t]
               + acapex_h2re[t]   * h2dri_h2_in[t] * h2_kwh_per_t/(8760*re_cf) );

# Fixed opex (labour + maintenance) on installed capacity
s.t. fixopex_cost_def{t in T}:
    fixopex_cost[t] =
      sunk * (   fopex_bof   * cap_bof[t]                          # sunk: fixed opex on capacity
               + fopex_cdri  * cap_cdri[t]
               + fopex_ngdri * cap_ngdri[t]
               + fopex_h2dri * cap_h2dri[t]
               + fopex_scrap * cap_scrap[t]
               + fopex_h2elec * cap_h2elec[t]                      # green-H2: electrolyser fixed O&M
               + fopex_h2re   * cap_h2re[t] )                      # green-H2: renewable fixed O&M
    + (1-sunk) * ( fopex_bof   * steel_bof[t]                      # not sunk: fixed opex on production
               + fopex_cdri  * coaldri_output[t]
               + fopex_ngdri * ngdri_output[t]
               + fopex_h2dri * h2dri_output[t]
               + fopex_scrap * steel_scrap_eaf[t]
               + fopex_h2elec * h2dri_h2_in[t]
               + fopex_h2re   * h2dri_h2_in[t] * h2_kwh_per_t/(8760*re_cf) );

# CCS retrofit capacity 
var build_ccs_bf   {T} >= 0;
var build_ccs_cdri {T} >= 0;
var build_ccs_ngdri{T} >= 0;
var ccs_cap_bf     {T} >= 0;
var ccs_cap_cdri   {T} >= 0;
var ccs_cap_ngdri  {T} >= 0;

s.t. ccs_cap_def_bf{t in T}:
    ccs_cap_bf[t]    = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_bf[j];
s.t. ccs_cap_def_cdri{t in T}:
    ccs_cap_cdri[t]  = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_cdri[j];
s.t. ccs_cap_def_ngdri{t in T}:
    ccs_cap_ngdri[t] = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_ccs+1} build_ccs_ngdri[j];

s.t. ccs_caplim_bf{t in T}:    ccs_bf[t]    <= ccs_cap_bf[t];
s.t. ccs_caplim_cdri{t in T}:  ccs_cdri[t]  <= ccs_cap_cdri[t];
s.t. ccs_caplim_ngdri{t in T}: ccs_ngdri[t] <= ccs_cap_ngdri[t];

# Green-H2 supply chain 
s.t. cap_def_h2elec{t in T}:
    cap_h2elec[t] = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_h2elec+1} build_h2elec[j];
s.t. cap_def_h2re{t in T}:
    cap_h2re[t]   = sum{j in T: ord(j)<=ord(t) and ord(j)>=ord(t)-life_re+1}     build_h2re[j];
s.t. h2elec_predebut{t in T: t < ng_h2_start_year}: cap_h2elec[t] = 0;
s.t. h2re_predebut  {t in T: t < ng_h2_start_year}: cap_h2re[t]   = 0;
s.t. h2elec_cover{t in T}:
    h2dri_h2_in[t] <= cap_h2elec[t];
s.t. h2re_cover{t in T}:
    h2_kwh_per_t * h2dri_h2_in[t] <= cap_h2re[t] * 8760 * re_cf;

s.t. h2elec_growth{t in T: t > first(T)}:
    cap_h2elec[t] - cap_h2elec[prev(t)] <=
        ( if   h2_ramp_mode = 0 then H2_BIGM
          else if h2_ramp_mode = 1 then ramp_frac * H2_cap
          else h2_ref_cap * ( h2_base[t]
                             + (h2_peak_rate
                                - (h2_base_start + (h2_base_end - h2_base_start)
                                                   *(h2_peak_year-2025)/25))
                               * exp( -((t - h2_peak_year)^2)
                                      / (2*h2_gauss_sigma^2) ) ) );

s.t. h2elec_first{t in T: t = first(T)}:
    cap_h2elec[t] <=
        ( if   h2_ramp_mode = 0 then H2_BIGM
          else if h2_ramp_mode = 1 then ramp_frac * H2_cap
          else h2_ref_cap * ( h2_base[t]
                             + (h2_peak_rate
                                - (h2_base_start + (h2_base_end - h2_base_start)
                                                   *(h2_peak_year-2025)/25))
                               * exp( -((t - h2_peak_year)^2)
                                      / (2*h2_gauss_sigma^2) ) ) );
