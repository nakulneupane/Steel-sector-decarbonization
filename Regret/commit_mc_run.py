#!/usr/bin/env python

import csv
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AMPL = os.environ.get("AMPL_EXE", r"C:\Users\Other User\AMPL\ampl.exe")
WORKERS = int(os.environ.get("MC_WORKERS", "10"))
N_PER_CLOUD = int(os.environ.get("REG_WORLDS", "100"))
RES = os.path.join(HERE, "results")
TMP = os.path.join(RES, "tmp")
PLANS = os.path.join(HERE, "plans")
OUT = os.path.join(RES, "commit_mc_results.csv")

YEARS = [2030, 2035, 2040, 2045]
REVIEW_A, REVIEW_B = 2035, 2045
BASE_SEED = 20260710                          # = Plots/MC/mc_run.py
FRONT_EFS = [1.4, 1.6, 1.8, 2.0, 2.2]        # panel-c target sweep
OUT_F = None                                  # set in main (results dir)

REGROW_FIELDS = ["status", "pv_cost_B", "lcop_pv", "slack_Mt", "import_Mt",
                 "ccs_Mt", "committed_B", "stranded_B",
                 "str_conv_B", "str_h2dri_B", "str_h2supply_B", "str_ccs_B",
                 "str_scrapchain_B", "str_othchain_B", "int_achieved"]
WORLD = ["theta_tech", "theta_gc", "scrap_rate", "ng_price", "ccoal",
         "ng_avail"]
FIELDS = (["run_id", "kind", "commit", "realized", "wid", "belief", "tstar"]
          + WORLD + REGROW_FIELDS + ["solve_s"])

with open(os.path.join(HERE, "commit_mc_case.mod")) as fh:
    CASE = fh.read()
with open(os.path.join(HERE, "commit_mc_front.mod")) as fh:
    FRONT = fh.read()

FRONTROW_FIELDS = ["status", "lcop_pv", "int_achieved", "slack_Mt", "ccs_Mt"]
FFIELDS = (["run_id", "commit", "ef", "wid"] + WORLD
           + FRONTROW_FIELDS + ["solve_s"])


def worlds_for(year, n):
    """First n seeded draws of one cloud (identical to Plots/MC)."""
    rng = np.random.default_rng(BASE_SEED + year)
    th_t = rng.integers(0, 11, 25000) / 10.0
    th_g = rng.integers(0, 11, 25000) / 10.0
    scrap = (2 + 0.5 * rng.integers(0, 13, 25000)) / 100.0
    ngp = rng.integers(5, 26, 25000)
    ccoal = rng.choice(["low", "mid", "high"], 25000)
    ngav = rng.choice(["bau", "shock", "policy"], 25000)
    return [
        (f"{year}_{i}",
         {"theta_tech": round(float(th_t[i]), 2),
          "theta_gc": round(float(th_g[i]), 2),
          "scrap_rate": round(float(scrap[i]), 4),
          "ng_price": int(ngp[i]),
          "ccoal": str(ccoal[i]), "ng_avail": str(ngav[i])})
        for i in range(n)]


def belief_at_2035(commit, realized):
    if realized <= REVIEW_A:
        return realized
    return max(commit, 2040)


def case_text(w, realized_or_belief, tstar, planfile, dumpout):
    s = CASE
    for tok, val in (("THETATECHVAL", w["theta_tech"]),
                     ("THETAGCVAL", w["theta_gc"]),
                     ("SCRAPRATEVAL", w["scrap_rate"]),
                     ("NGPRICEVAL", w["ng_price"]),
                     ("CCOALFILE", f"scenarios/ccoal_{w['ccoal']}.mod"),
                     ("NGAVAILFILE", f"scenarios/ng_{w['ng_avail']}.mod"),
                     ("H2READYVAL", realized_or_belief),
                     ("TSTARVAL", tstar),
                     ("PLANFILE", planfile),
                     ("DUMPOUT", dumpout)):
        s = s.replace(tok, str(val))
    return s


def err_line(p):
    lines = ((p.stderr or "") + "\n" + (p.stdout or "")).strip().splitlines()
    for ln in reversed(lines):
        if any(k in ln.lower() for k in ("error", "infeasible", "license",
                                         "cannot")):
            return ln.strip()
    return lines[-1].strip() if lines else "no output"


def solve_case(job):
    run_id, kind, commit, realized, wid, w, belief, tstar, plan, dump = job
    row = {"run_id": run_id, "kind": kind, "commit": commit,
           "realized": realized, "wid": wid, "belief": belief,
           "tstar": tstar, **w}
    t0 = time.time()
    r, p = None, None
    for attempt in range(2):
        mod = os.path.join(TMP, f"mc_{run_id}.mod")
        with open(mod, "w") as fh:
            fh.write(case_text(w, belief, tstar, plan, dump))
        try:
            p = subprocess.run([AMPL, mod], cwd=HERE, capture_output=True,
                               text=True, timeout=600)
            for line in p.stdout.splitlines():
                if line.startswith("REGROW,"):
                    v = line.split(",")[1:]
                    if len(v) == len(REGROW_FIELDS):
                        r = v
            if r is not None:
                row.update(zip(REGROW_FIELDS, r))
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        try:
            os.remove(mod)
        except OSError:
            pass
        if r is not None:
            break
        time.sleep(1.0)
    if r is None:
        row["status"] = "error:" + (err_line(p)[:80] if p else "no run")
    row["solve_s"] = round(time.time() - t0, 2)
    return row


def solve_front(job):
    """Panel-c frontier point: committed-world cloud C, target ef, world w."""
    run_id, commit, ef, wid, w = job
    s = FRONT
    for tok, val in (("THETATECHVAL", w["theta_tech"]),
                     ("THETAGCVAL", w["theta_gc"]),
                     ("SCRAPRATEVAL", w["scrap_rate"]),
                     ("NGPRICEVAL", w["ng_price"]),
                     ("CCOALFILE", f"scenarios/ccoal_{w['ccoal']}.mod"),
                     ("NGAVAILFILE", f"scenarios/ng_{w['ng_avail']}.mod"),
                     ("H2YEARVAL", commit), ("AVGEMIVAL", ef)):
        s = s.replace(tok, str(val))
    row = {"run_id": run_id, "commit": commit, "ef": ef, "wid": wid, **w}
    t0 = time.time()
    r, p = None, None
    for attempt in range(2):
        mod = os.path.join(TMP, f"fr_{run_id}.mod")
        with open(mod, "w") as fh:
            fh.write(s)
        try:
            p = subprocess.run([AMPL, mod], cwd=HERE, capture_output=True,
                               text=True, timeout=600)
            for line in p.stdout.splitlines():
                if line.startswith("FRONTROW,"):
                    v = line.split(",")[1:]
                    if len(v) == len(FRONTROW_FIELDS):
                        r = v
            if r is not None:
                row.update(zip(FRONTROW_FIELDS, r))
        except Exception:
            pass
        try:
            os.remove(mod)
        except OSError:
            pass
        if r is not None:
            break
        time.sleep(1.0)
    if r is None:
        row["status"] = "error:" + (err_line(p)[:80] if p else "no run")
    row["solve_s"] = round(time.time() - t0, 2)
    return row


def assemble_history(commit, wid):
    hist = os.path.join(TMP, f"mchist_c{commit}_{wid}.mod")
    win = os.path.join(TMP, f"mcwin_c{commit}_{wid}.mod")
    with open(hist, "w") as out:
        out.write(f"# recourse history: plan_c{commit} pre-2035 "
                  f"+ 2035 epoch window (world {wid})\n")
        with open(os.path.join(PLANS, f"plan_c{commit}.mod")) as fh:
            for ln in fh:
                m = re.search(r"\[(\d{4})\]", ln)
                if m and int(m.group(1)) < REVIEW_A:
                    out.write(ln)
        with open(win) as fh:
            for ln in fh:
                m = re.search(r"\[(\d{4})\]", ln)
                if m and REVIEW_A <= int(m.group(1)) < REVIEW_B:
                    out.write(ln)
    return f"results/tmp/mchist_c{commit}_{wid}.mod"


def run_pool(jobs, writer, fh, label, t0):
    n_ok = n_err = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(solve_case, j) for j in jobs]
        for k, fut in enumerate(as_completed(futs), 1):
            row = fut.result()
            err = str(row.get("status", "")).startswith("error")
            n_ok += not err
            n_err += err
            writer.writerow(row)
            if k % 100 == 0 or k == len(jobs):
                fh.flush()
                el = time.time() - t0
                print(f"  {label}: {k}/{len(jobs)} ok={n_ok} err={n_err} "
                      f"({el/max(k,1):.2f}s/run)", flush=True)
    return n_ok, n_err


def main():
    os.makedirs(TMP, exist_ok=True)
    for c in YEARS:
        if not os.path.exists(os.path.join(PLANS, f"plan_c{c}.mod")):
            raise SystemExit(f"plans/plan_c{c}.mod missing -- run "
                             "commit.bat (single-world study) once first")
    junk = "results/tmp/mc_dump_ignore.mod"
    done = set()
    if os.path.exists(OUT):
        with open(OUT, newline="") as fh:
            done = {r["run_id"] for r in csv.DictReader(fh)
                    if not r.get("status", "").startswith("error")}

    worlds = {yr: worlds_for(yr, N_PER_CLOUD) for yr in YEARS}
    n_worlds = sum(len(v) for v in worlds.values())
    print(f"COMMIT-MC: {n_worlds} worlds ({N_PER_CLOUD}/cloud), "
          f"{len(done)} runs already done", flush=True)

    jobs_a, jobs_b = [], []
    for yr in YEARS:
        for wid, w in worlds[yr]:
            rid = f"pf_{wid}"
            if rid not in done:
                jobs_a.append((rid, "pf", "", yr, wid, w, yr, 2025,
                               "plans/plan_null.mod", junk))
            for c in YEARS:
                rid = f"nr_c{c}_{wid}"
                if rid not in done:
                    jobs_a.append((rid, "norec", c, yr, wid, w, yr, 2051,
                                   f"plans/plan_c{c}.mod", junk))
                rid = f"ra_c{c}_{wid}"
                win = os.path.join(TMP, f"mcwin_c{c}_{wid}.mod")
                if rid not in done or not os.path.exists(win):
                    jobs_a.append((rid, "recA", c, yr, wid, w,
                                   belief_at_2035(c, yr), REVIEW_A,
                                   f"plans/plan_c{c}.mod",
                                   f"results/tmp/mcwin_c{c}_{wid}.mod"))
                rid = f"rb_c{c}_{wid}"
                if rid not in done:
                    jobs_b.append((rid, "rec", c, yr, wid, w, yr, REVIEW_B,
                                   c, wid))     # plan assembled after phase A

    new = not os.path.exists(OUT)
    t0 = time.time()
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        print(f"[1/3] pf + norec + recourse epoch A: {len(jobs_a)} solves",
              flush=True)
        run_pool(jobs_a, w, fh, "phase A", t0)

        print(f"[2/3] final recourse epoch (2045): {len(jobs_b)} solves",
              flush=True)
        jb = []
        for (rid, kind, c, yr, wid, wrl, belief, tstar, cc, ww) in jobs_b:
            win = os.path.join(TMP, f"mcwin_c{cc}_{ww}.mod")
            if not os.path.exists(win):
                print(f"  skip {rid}: epoch-A window missing", flush=True)
                continue
            hist = assemble_history(cc, ww)
            jb.append((rid, kind, c, yr, wid, wrl, belief, tstar, hist, junk))
        run_pool(jb, w, fh, "phase B", time.time())

    print(f"Wrote {OUT}", flush=True)

    # ------- phase 3: panel-c pareto frontiers (target sweep per cloud) -----
    out_f = os.path.join(RES, "commit_mc_front.csv")
    done_f = set()
    if os.path.exists(out_f):
        with open(out_f, newline="") as fh:
            done_f = {r["run_id"] for r in csv.DictReader(fh)
                      if not r.get("status", "").startswith("error")}
    fjobs = []
    for c in YEARS:                    # committed-world cloud = arrival c
        for wid, wrl in worlds[c]:
            for ef in FRONT_EFS:
                rid = f"fr_c{c}_ef{ef}_{wid}"
                if rid not in done_f:
                    fjobs.append((rid, c, ef, wid, wrl))
    print(f"[3/3] panel-c frontier sweep: {len(fjobs)} solves "
          f"({len(done_f)} done)", flush=True)
    new_f = not os.path.exists(out_f)
    t0f = time.time()
    with open(out_f, "a", newline="") as fh:
        wf = csv.DictWriter(fh, fieldnames=FFIELDS, extrasaction="ignore")
        if new_f:
            wf.writeheader()
        n_ok = n_err = 0
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = [ex.submit(solve_front, j) for j in fjobs]
            for k, fut in enumerate(as_completed(futs), 1):
                row = fut.result()
                err = str(row.get("status", "")).startswith("error")
                n_ok += not err
                n_err += err
                wf.writerow(row)
                if k % 100 == 0 or k == len(fjobs):
                    fh.flush()
                    el = time.time() - t0f
                    print(f"  frontier: {k}/{len(fjobs)} ok={n_ok} "
                          f"err={n_err} ({el/max(k,1):.2f}s/run)",
                          flush=True)
    print(f"Wrote {out_f}", flush=True)

    import pandas as pd
    df = pd.read_csv(OUT)
    xlsx = os.path.join(RES, "commit_mc_results.xlsx")
    dff = pd.read_csv(out_f)
    for attempt in range(2):
        try:
            with pd.ExcelWriter(xlsx, engine="openpyxl") as xl:
                df.to_excel(xl, sheet_name="raw", index=False)
                dff.to_excel(xl, sheet_name="frontier_raw", index=False)
            print(f"Wrote {xlsx}", flush=True)
            break
        except PermissionError:
            if attempt == 0:
                print("commit_mc_results.xlsx locked (Excel open?) -- "
                      "retrying in 5 s", flush=True)
                time.sleep(5)
            else:
                raise
    n_err = int(df.status.astype(str).str.startswith("error").sum())
    print(f"DONE rows={len(df)} err={n_err}", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
