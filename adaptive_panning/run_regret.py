#!/usr/bin/env python3
"""Regret study: H2-commitment checkpoint ladder.

A commitment program is signed once in 2030 under a fixed central-belief
backdrop (a single PLAN solve). Each world then draws a true hydrogen
arrival year R (2030-2049, uniform over years) plus 9 uncertain inputs
(WORLD_AXES below) and is solved 10 ways:

  * pf     -- perfect foresight: solved with h2ready=R directly, no
              commitment floors. This is the regret BASELINE.
  * norec  -- no recourse: solved under the 2030 program's floors for the
              whole horizon (tstar=2051), no adjustment ever allowed.
  * a ladder of 4 checkpoints (2030, 2035, 2040, 2045): at each, the
      planner's belief about R updates if arrival has already happened,
      re-solves under that belief with floors locked from prior history,
      then SETTLES (locks the just-decided window, re-solves under the
      TRUE R with the full horizon committed) to get the recourse-
      corrected result.

Regret for a world = LCOP(recourse) - LCOP(perfect foresight).

1,000 worlds (50/year x 20 arrival years 2030-2049) x 10 solves each =
10,000 solves. 50/year is a deliberately round, directly-chosen sample
size (not back-derived from a target total) -- the finalized figure bins
arrival years into four 5-year cohorts (2030-34/35-39/40-44/45-49) for
plotting, so the sample size that actually matters is per-BIN
(50 x 5 = 250), not per individual arrival year.

Sample-size choice was checked empirically, not just assumed: pilot runs
at 10/25/50 worlds/year were compared against each other on both the
regret-decay and stranded-asset statistics. Aggregate (magnitude-
weighted) error relative to 50/year was ~1.8%/2.3% at 10/year and
~1.4%/0.9% at 25/year (regret/stranded-assets respectively) -- the
decay SHAPE and cohort ordering were identical at every sample size
tested, only exact magnitudes drifted by a percent or two. 50/year was
chosen as a comfortable margin above the point where that drift becomes
visible, without paying for the 10x cost of the original 500/year design
(whose only justification was landing close to a round total, not any
convergence evidence).

NOTE on the R=2049 cohort: the model horizon ends in 2050, so a world
whose true arrival is 2049 has only 1 year of horizon left for the
"settle" solve to react to -- there is essentially no room left to
recourse into. This cohort is intentionally included (for a clean
50 x 20 = 1,000 total) but is a genuinely lower-information case than
the other 19 cohorts; treat it as such in any per-cohort analysis, not
as equivalent evidence about recourse value.

WORLD_AXES draws use the SAME value levels as the Monte Carlo study
(theta_tech, theta_grid, theta_ccs, scrap_rate, ccoal/ng/scrap price,
ccoal/ng availability) but are resampled independently per world -- this
study characterizes risk across a distribution of H2-arrival-year
outcomes, not matched comparisons against specific structural cells, so
it does not reuse Monte Carlo's shared draw list.

Reproducibility: each arrival-year cohort of worlds is drawn from its own
numpy Generator seeded as BASE_SEED + year, so the worlds themselves are
identical on every rerun regardless of solve order or machine. Every
solve uses a fresh AMPL() instance and Threads=1, matching the
reproducibility discipline used everywhere else in this repository.

Output: data/regret_ladder.csv -- one row per solve (run_id, kind,
n_reviews, wid, realized, belief, tstar, the 9 world-axis values, solve
status/metrics, solve_s).

    python run_regret.py                # full 1,000-world study
    python run_regret.py -j 6            # set parallel worker count
"""
import argparse
import csv
import multiprocessing as mp
import os
import pathlib
import sys
import tempfile
import time

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
RES = HERE / "data"
TMP = RES / "tmp"

C = 2030                                    # the single commitment year studied
CHECKPOINTS = [2030, 2035, 2040, 2045]
ARRIVAL_YEARS = list(range(2030, 2050))     # 2030..2049 (20 years)
BASE_SEED = 20260821                        # matches this project's MC draw-seed convention
END = 2051

WORKERS = int(os.environ.get("MC_WORKERS", "10"))
N_PER_YEAR = int(os.environ.get("LADDER_WORLDS_PER_YEAR", "50"))

# study backdrop for the single C-year commitment PLAN (central belief world)
BACKDROP = {"theta_tech": 0.5, "theta_grid": 0.5, "theta_ccs": 0.5,
            "scrap_rate": 0.06, "ccoal_price": 250, "ng_price": 15,
            "scrap_price": 350, "ccoal": "abundant", "ng": "abundant"}

WORLD_AXES = {
    "theta_tech": [0, 0.25, 0.5, 0.75, 1.0],
    "theta_grid": [0.25, 0.5, 0.75],
    "theta_ccs": [0, 0.25, 0.5, 0.75, 1.0],
    "scrap_rate": [0.02, 0.04, 0.06, 0.08, 0.10],
    "ccoal_price": [100, 250, 400],
    "ng_price": [5, 15, 25],
    "scrap_price": [250, 350, 450],
    "ccoal": ["abundant", "scarce"],
    "ng": ["abundant", "scarce"],
}
BUILD_CLASSES = ["bof", "cdri", "ngdri", "h2dri", "scrap", "scrapchain",
                 "coalchain", "ngchain", "h2elec", "h2re",
                 "ccs_bf", "ccs_cdri", "ccs_ngdri"]
# ocapex expression per class, used both in the objective (h2elec/h2re
# financial term) and in post-solve stranding valuation
OCAPEX_EXPR = {
    "bof": "ocapex_bof", "cdri": "ocapex_cdri", "ngdri": "ocapex_ngdri",
    "h2dri": "ocapex_h2dri[t]", "scrap": "ocapex_scrap",
    "scrapchain": "ocapex_scrapchain", "coalchain": "ocapex_coalchain",
    "ngchain": "ocapex_ngchain", "h2elec": "ocapex_h2elec[t]",
    "h2re": "ocapex_h2re[t]", "ccs_bf": "ocapex_ccs[t]*ccs_mult_bf",
    "ccs_cdri": "ocapex_ccs[t]*ccs_mult_cdri",
    "ccs_ngdri": "ocapex_ccs[t]*ccs_mult_ngdri",
}
# peak-use expression per class (post-solve, for stranding's "idle" calc)
USE_EXPR = {
    "bof": "steel_bof[t] - legacy_bof[t]",
    "cdri": "coaldri_output[t] - legacy_cdri[t]",
    "ngdri": "ngdri_output[t] - legacy_ngdri[t]",
    "h2dri": "h2dri_output[t] - legacy_h2dri[t]",
    "scrap": "steel_scrap_eaf[t] - legacy_scrap[t]",
    "scrapchain": "bof_scrap_in[t] + eaf_scrap_in[t] + scrap_eaf_scrap_in[t]",
    "h2elec": "h2dri_h2_in[t] + bf_h2_in[t]",
    "ccs_bf": "ccs_bf[t]", "ccs_cdri": "ccs_cdri[t]", "ccs_ngdri": "ccs_ngdri[t]",
}
CCOAL_FILE = {"abundant": "structural/axes/ccoal_abundant.mod",
              "scarce": "structural/axes/ccoal_scarce.mod"}
NG_FILE = {"abundant": "structural/axes/ng_policy.mod",
           "scarce": "structural/axes/ng_bau.mod"}

REGROW_FIELDS = ["status", "pv_cost_B", "lcop_pv", "slack_Mt", "import_Mt",
                 "ccs_Mt", "committed_B", "stranded_B",
                 "str_conv_B", "str_h2dri_B", "str_h2supply_B", "str_ccs_B",
                 "str_scrapchain_B", "str_othchain_B", "int_achieved"]
WORLD_FIELDS = list(WORLD_AXES)
FIELDS = (["run_id", "kind", "n_reviews", "wid", "realized", "belief", "tstar"]
          + WORLD_FIELDS + REGROW_FIELDS + ["solve_s"])


def worlds_for(year, n):
    rng = np.random.default_rng(BASE_SEED + year)
    out = []
    for i in range(n):
        w = {k: rng.choice(v) for k, v in WORLD_AXES.items()}
        for k in ("theta_tech", "theta_grid", "theta_ccs", "scrap_rate"):
            w[k] = float(w[k])
        for k in ("ccoal_price", "ng_price", "scrap_price"):
            w[k] = int(w[k])
        w["ccoal"] = str(w["ccoal"])
        w["ng"] = str(w["ng"])
        out.append((f"{year}_{i}", w))
    return out


def belief_at(t_k, R, prior_belief, next_t):
    """R if already observed by t_k; else roll forward to the next
    checkpoint. Last checkpoint (next_t=None) with no observation: freeze
    at prior_belief -- there's no further checkpoint to act on a new guess
    (this is what makes N=1 sometimes worse than N=0 for near-miss
    arrivals, a documented property of the ladder, not a bug)."""
    if R <= t_k:
        return R
    if next_t is None:
        return prior_belief
    return max(prior_belief, next_t)


def case_text(world, h2ready, tstar, committed):
    """Build the full AMPL command text for one solve: base model + world
    overrides + commitment floors/financial-H2 + relaxations + elastic
    objective. `committed` is {class: {year: value}} (missing = 0)."""
    lines = ["reset;", "set T ordered := 2025..2050;",
             "include core/model.mod;"]

    lines.append(f"let ng_h2_start_year := {int(h2ready)};")
    lines.append(f"let theta_tech := {world['theta_tech']};")
    lines.append(f"let theta_grid := {world['theta_grid']};")
    lines.append(f"let theta_ccs := {world['theta_ccs']};")
    lines.append(f"let n8_scrap_rate := {world['scrap_rate']};")
    lines.append(f"let ng_cost_ccoal := {world['ccoal_price']};")
    lines.append(f"let {{t in T}} n5_cost_NG[t] := {world['ng_price']};")
    lines.append(f"let ng_cost_scrap := {world['scrap_price']};")
    lines.append("let avg_emi := 1.8;")
    lines.append("let cap_add_common := 30000000;")   # build_cap fixed at 'mid'
    lines.append("let h2_ref_cap := 4000000;")          # ramp fixed at 'medium'
    lines.append("let legacy_phaseout := 0;")           # legacy fixed at 'run-life'
    lines.append(f"include {CCOAL_FILE[world['ccoal']]};")
    lines.append(f"include {NG_FILE[world['ng']]};")

    for c in BUILD_CLASSES:
        lines.append(f"param committed_build_{c}{{T}} default 0;")
    for c in BUILD_CLASSES:
        for yr, val in committed.get(c, {}).items():
            if val > 1e-9:
                lines.append(f"let committed_build_{c}[{yr}] := {val:.6f};")

    # H2-DRI plants are FINANCIAL commitments too (not physical): the
    # cap_add_h2dri0 gate (v_capacity.mod) hard-zeros build_h2dri before
    # the world's TRUE h2_start, which would directly contradict a
    # physical floor set under an earlier belief. Same logic as H2 supply
    # (elz/RE) -- pay the committed capex even if construction can't
    # physically happen yet.
    FINANCIAL_CLASSES = ("h2elec", "h2re", "h2dri")
    floor_classes = [c for c in BUILD_CLASSES if c not in FINANCIAL_CLASSES]
    for c in floor_classes:
        lines.append(f"s.t. commit_{c}{{t in T: t < {int(tstar)}}}: "
                     f"build_{c}[t] >= committed_build_{c}[t];")

    for c in FINANCIAL_CLASSES:
        lines.append(f"var pay_{c}_extra{{T}} >= 0;")
        lines.append(f"s.t. pay_{c}_def{{t in T: t < {int(tstar)}}}: "
                     f"pay_{c}_extra[t] >= committed_build_{c}[t] - build_{c}[t];")

    # cap_add_total is a SHARED competing-EPC-budget ceiling across
    # bof/cdri/ngdri/scrap/h2dri (v_capacity.mod). Floors assembled from
    # DIFFERENT checkpoint windows are each individually valid under their
    # own originating solve's cap_add_total, but stitching them together
    # can jointly exceed it in bookkeeping even though nothing was
    # over-budget in reality when each window was decided. Fix: the shared
    # ceiling only binds years NOT YET locked in (t >= tstar) -- already-
    # committed history doesn't need re-validating against it.
    lines.append("drop cap_add_total;")
    lines.append(f"s.t. cap_add_total_free{{t in T: t > first(T) and t >= {int(tstar)}}}: "
                 f"build_bof[t] + build_cdri[t] + build_ngdri[t] + build_scrap[t] "
                 f"+ build_h2dri[t] <= (if h2_ramp_mode = 0 then H2_BIGM else cap_add_common);")

    for c in ("bof", "cdri", "ngdri", "h2dri", "scrap"):
        lines.append(f"drop min_util_{c};")

    lines.append("param IMPORT_P := 20000;")
    lines.append("var steel_import{T} >= 0;")
    lines.append("drop meet_demand;")
    lines.append("s.t. meet_demand_elastic{t in T}: total_steel[t] + steel_import[t] "
                 "= base_demand*(1+growth_rate)^(ord(t)-1);")

    lines.append("drop emission_monotonic;")
    lines.append("drop avg_emis_cap_total;")
    lines.append("param PEN := 5000;")
    lines.append("var emis_slack >= 0;")
    lines.append("param carbon_budget := avg_emi * sum{t in T} "
                 "base_demand*(1+growth_rate)^(ord(t)-1);")
    lines.append("s.t. cap_elastic: sum{t in T} total_emissions[t] "
                 "<= carbon_budget + emis_slack;")

    lines.append(
        "minimize obj2: sum {t in T} discount_factor[t] * (total_cost[t] "
        "+ ocapex_h2elec[t]*pay_h2elec_extra[t] + ocapex_h2re[t]*pay_h2re_extra[t] "
        "+ ocapex_h2dri[t]*pay_h2dri_extra[t] "
        "+ IMPORT_P*steel_import[t]) + PEN*emis_slack;")
    lines.append("objective obj2;")
    lines.append("option solver gurobi;")
    lines.append("option gurobi_options 'Threads=1 TimeLimit=300 outlev=0 mipgap=0.002';")
    lines.append("solve;")
    return "\n".join(lines)


def solve_case(world, h2ready, tstar, committed):
    """Run one case solve. Returns (ok, result_dict, build_dict) where
    build_dict is {class: {year: value}} for the FULL horizon (for
    handoff), and result_dict has the regret-ladder fields plus
    stranding, computed only when tstar-locked history exists (tstar>2025)."""
    from amplpy import AMPL
    ampl = AMPL()
    ampl.set_option("solver_msg", 0)
    ampl.cd(str(ROOT))
    try:
        ampl.set_option("TMPDIR", tempfile.mkdtemp(prefix="regret_"))
    except Exception:
        pass
    try:
        ampl.eval(case_text(world, h2ready, tstar, committed))
        status = ampl.get_value("solve_result")
        if status != "solved":
            return False, {"status": status}, {}

        IMPORT_REPORT = 650.0
        pv_cost = ampl.get_value(
            "sum {t in T} discount_factor[t] * (total_cost[t] "
            "+ ocapex_h2elec[t]*pay_h2elec_extra[t] + ocapex_h2re[t]*pay_h2re_extra[t] "
            "+ ocapex_h2dri[t]*pay_h2dri_extra[t] "
            f"+ {IMPORT_REPORT}*steel_import[t])")
        pv_steel = ampl.get_value(
            "sum {t in T} discount_factor[t] * (total_steel[t] + steel_import[t])")
        slack_Mt = ampl.get_value("emis_slack") / 1e6
        import_Mt = ampl.get_value("sum{t in T} steel_import[t]") / 1e6
        ccs_Mt = ampl.get_value("sum{t in T} total_ccs[t]") / 1e6
        int_achieved = ampl.get_value(
            "(sum{t in T} total_emissions[t]) / (sum{t in T} total_steel[t])")

        result = {"status": "solved", "pv_cost_B": pv_cost / 1e9,
                  "lcop_pv": pv_cost / pv_steel, "slack_Mt": slack_Mt,
                  "import_Mt": import_Mt, "ccs_Mt": ccs_Mt,
                  "int_achieved": int_achieved}

        build = {}
        for c in BUILD_CLASSES:
            df = ampl.get_variable(f"build_{c}").get_values().to_pandas()
            build[c] = {int(y): float(v) for y, v in
                       zip(df.index, df[df.columns[0]])}

        if tstar > 2025.5:
            com_x = {}
            idle = {}
            for c in BUILD_CLASSES:
                cu_committed = sum(v for y, v in committed.get(c, {}).items() if y < tstar)
                cx = ampl.get_value(
                    f"sum{{t in T: t < {int(tstar)}}} {OCAPEX_EXPR[c]} * committed_build_{c}[t]")
                com_x[c] = cx
                if c in USE_EXPR:
                    use_peak = ampl.get_value(f"max{{t in T}} ({USE_EXPR[c]})")
                elif c == "h2re":
                    h2_kw = ampl.get_value("h2_kw_per_t")
                    use_h2elec = ampl.get_value("max{t in T} (h2dri_h2_in[t] + bf_h2_in[t])")
                    use_peak = h2_kw * use_h2elec
                else:
                    use_peak = 0.0
                idle[c] = (max(0.0, cu_committed - max(0.0, use_peak)) / cu_committed
                          if cu_committed > 1e-3 else 0.0)
            stranded = {c: com_x[c] * idle[c] for c in BUILD_CLASSES}
            result["committed_B"] = sum(com_x.values()) / 1e9
            result["stranded_B"] = sum(stranded.values()) / 1e9
            result["str_conv_B"] = (stranded["bof"] + stranded["cdri"]
                                    + stranded["ngdri"] + stranded["scrap"]) / 1e9
            result["str_h2dri_B"] = stranded["h2dri"] / 1e9
            result["str_h2supply_B"] = (stranded["h2elec"] + stranded["h2re"]) / 1e9
            result["str_ccs_B"] = (stranded["ccs_bf"] + stranded["ccs_cdri"]
                                   + stranded["ccs_ngdri"]) / 1e9
            result["str_scrapchain_B"] = stranded["scrapchain"] / 1e9
            result["str_othchain_B"] = (stranded["coalchain"] + stranded["ngchain"]) / 1e9
        else:
            for k in ("committed_B", "stranded_B", "str_conv_B", "str_h2dri_B",
                      "str_h2supply_B", "str_ccs_B", "str_scrapchain_B", "str_othchain_B"):
                result[k] = 0.0

        return True, result, build
    except Exception as e:
        return False, {"status": f"error:{str(e)[:80]}"}, {}
    finally:
        ampl.close()


def assemble_history(prev, window, lo, hi):
    """prev = {class:{year:val}} pre-lo history; window = the just-solved
    full-horizon build dict; keep prev's years < lo and window's years in
    [lo, hi)."""
    out = {}
    for c in BUILD_CLASSES:
        merged = {y: v for y, v in prev.get(c, {}).items() if y < lo}
        merged.update({y: v for y, v in window.get(c, {}).items() if lo <= y < hi})
        out[c] = merged
    return out


def run_solve(run_id, kind, n_reviews, wid, R, w, h2ready, tstar, committed):
    row = {"run_id": run_id, "kind": kind, "n_reviews": n_reviews, "wid": wid,
           "realized": R, "belief": h2ready, "tstar": tstar, **w}
    t0 = time.time()
    ok, result, build = solve_case(w, h2ready, tstar, committed)
    row.update(result)
    row["solve_s"] = round(time.time() - t0, 2)
    return ok, row, build


def process_world(args):
    R, wid, w, plan_build = args
    rows = []

    ok, row, _ = run_solve(f"pf_{wid}", "pf", None, wid, R, w, R, 2025, {})
    rows.append(row)

    ok, row, _ = run_solve(f"norec_{wid}", "norec", 0, wid, R, w, R, 2051, plan_build)
    rows.append(row)

    def fail_row(run_id, kind, n_reviews, t_k, belief):
        return {"run_id": run_id, "kind": kind, "n_reviews": n_reviews,
                "wid": wid, "realized": R, "belief": belief, "tstar": t_k,
                "status": "error:upstream_failed", "solve_s": 0, **w}

    history = plan_build
    prior_belief = C
    chain_ok = True

    for i, t_k in enumerate(CHECKPOINTS):
        next_t = CHECKPOINTS[i + 1] if i + 1 < len(CHECKPOINTS) else None
        belief = belief_at(t_k, R, prior_belief, next_t)
        kind = "final" if next_t is None else f"chk{t_k}"
        n_reviews = i + 1

        if not chain_ok:
            rows.append(fail_row(f"{kind}_{wid}", kind, n_reviews, t_k, belief))
            rows.append(fail_row(f"settle_n{n_reviews}_{wid}", f"settle_n{n_reviews}",
                                 n_reviews, t_k, "true"))
            continue

        ok, row, window_build = run_solve(f"{kind}_{wid}", kind, n_reviews, wid, R, w,
                                          belief, t_k, history)
        rows.append(row)
        if not ok:
            chain_ok = False
            rows.append(fail_row(f"settle_n{n_reviews}_{wid}", f"settle_n{n_reviews}",
                                 n_reviews, t_k, "true"))
            continue

        settle_hist = assemble_history(history, window_build, t_k, END)
        sok, srow, _ = run_solve(f"settle_n{n_reviews}_{wid}", f"settle_n{n_reviews}",
                                 n_reviews, wid, R, w, R, 2051, settle_hist)
        rows.append(srow)

        if next_t is not None:
            history = assemble_history(history, window_build, t_k, next_t)
        prior_belief = belief

    return rows


def compute_plan():
    """The single C=2030 commitment plan under the fixed study backdrop."""
    print(f"Computing commitment plan (C={C}, backdrop={BACKDROP})...", flush=True)
    ok, result, build = solve_case(BACKDROP, C, 2025, {})
    if not ok:
        raise SystemExit(f"plan solve failed: {result}")
    print(f"  plan solved: lcop_pv={result['lcop_pv']:.2f}, "
          f"int_achieved={result['int_achieved']:.4f}", flush=True)
    return build


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worlds-per-year", type=int, default=N_PER_YEAR)
    p.add_argument("-j", "--jobs", type=int, default=WORKERS)
    p.add_argument("--out", default=str(RES / "regret_ladder.csv"))
    args = p.parse_args()

    RES.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(args.out)

    plan_build = compute_plan()

    worlds = []
    for yr in ARRIVAL_YEARS:
        worlds += [(yr, wid, w, plan_build) for wid, w in
                  worlds_for(yr, args.worlds_per_year)]
    print(f"REGRET LADDER: {len(worlds)} worlds ({args.worlds_per_year}/year x "
          f"{len(ARRIVAL_YEARS)} years {ARRIVAL_YEARS[0]}-{ARRIVAL_YEARS[-1]}), "
          f"C={C}, checkpoints={CHECKPOINTS} -> {len(worlds)*10:,} solves",
          flush=True)

    t0 = time.time()
    n_ok = n_err = n_worlds_done = 0
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        with mp.Pool(args.jobs) as pool:
            for rows in pool.imap_unordered(process_world, worlds, chunksize=1):
                for row in rows:
                    writer.writerow(row)
                    err = str(row.get("status", "")).startswith("error")
                    n_ok += not err
                    n_err += err
                n_worlds_done += 1
                fh.flush()
                if n_worlds_done % 10 == 0 or n_worlds_done == len(worlds):
                    el = time.time() - t0
                    print(f"  {n_worlds_done}/{len(worlds)} worlds "
                          f"(rows ok={n_ok} err={n_err}, "
                          f"{el/max(n_worlds_done,1):.2f}s/world)", flush=True)

    print(f"DONE. wrote {out}", flush=True)
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
