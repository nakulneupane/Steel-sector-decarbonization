#!/usr/bin/env python
"""
Four clouds, one per H2 start year {2030, 2035, 2040, 2045}, N=25,000 draws
each (100,000 solves total). Per draw, independent DISCRETE-uniform sampling:
    theta_tech   ~ U{0, 0.1, ..., 1.0}     theta_grid=theta_ccs ~ same grid
    scrap growth ~ U{2, 2.5, ..., 8} %/yr  NG price ~ U{5, 6, ..., 25} $/MMBtu
    coking coal  ~ U{low,mid,high}         NG avail ~ U{bau,shock,policy}
"""
import csv
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
AMPL = os.environ.get("AMPL_EXE", r"C:\Users\Other User\AMPL\ampl.exe")
WORKERS = int(os.environ.get("MC_WORKERS", "10"))
LIMIT = int(os.environ.get("MC_LIMIT", "0"))
CLOUD = os.environ.get("MCP_CLOUD", "")
ALL = os.environ.get("MCP_ALL", "") == "1"
OUT = os.path.join(HERE, "results", "mcp_results.csv")
TMP = os.path.join(HERE, "results", "tmp")

H2_YEARS = [2030, 2035, 2040, 2045]
N_PER_CLOUD = 25000
BASE_SEED = 20260710

MCROW_FIELDS = ["status", "lcop_pv", "cum_emis_Mt", "cum_ccs_Mt", "d_index",
                "cap_dual", "invest_npv_B", "peak_ccoal_Mt", "peak_ng_Mt",
                "steel2050_Mt", "bof2050_Mt", "cdri2050_Mt", "ngdri2050_Mt",
                "h2dri2050_Mt", "scrapeaf2050_Mt",
                "scrap_bof2050_Mt", "scrap_cdri2050_Mt", "scrap_ngdri2050_Mt",
                "scrap_h2dri2050_Mt", "scrap_scrapeaf2050_Mt"]
MCROW2_FIELDS = ["scrap_limit2050_Mt", "scrap_use_cum_Mt",
                 "cost2050_pt", "emis2050_pt"]
INPUTS = ["h2_year", "draw", "theta_tech", "theta_gc", "scrap_rate",
          "ng_price", "ccoal", "ng_avail"]
FIELDS = ["run_id"] + INPUTS + MCROW_FIELDS + MCROW2_FIELDS + ["solve_s"]

with open(os.path.join(HERE, "template.mod")) as fh:
    TEMPLATE = fh.read()


def draws_for(year):
    """Deterministic discrete-uniform draws for one cloud (seeded by year)."""
    rng = np.random.default_rng(BASE_SEED + year)
    base = (year - 2030) // 5 * N_PER_CLOUD
    th_t = rng.integers(0, 11, N_PER_CLOUD) / 10.0        # 0, 0.1, ..., 1.0
    th_g = rng.integers(0, 11, N_PER_CLOUD) / 10.0
    scrap = (2 + 0.5 * rng.integers(0, 13, N_PER_CLOUD)) / 100.0  # 2..8 step .5
    ngp = rng.integers(5, 26, N_PER_CLOUD)                # 5, 6, ..., 25
    ccoal = rng.choice(["low", "mid", "high"], N_PER_CLOUD)
    ngav = rng.choice(["bau", "shock", "policy"], N_PER_CLOUD)
    return [
        (base + i,
         {"h2_year": year, "draw": i,
          "theta_tech": round(float(th_t[i]), 2),
          "theta_gc": round(float(th_g[i]), 2),
          "scrap_rate": round(float(scrap[i]), 4),
          "ng_price": int(ngp[i]),
          "ccoal": str(ccoal[i]), "ng_avail": str(ngav[i])})
        for i in range(N_PER_CLOUD)]


def model_text(c):
    s = TEMPLATE
    for tok, val in (("H2YEARVAL", c["h2_year"]),
                     ("THETATECHVAL", c["theta_tech"]),
                     ("THETAGCVAL", c["theta_gc"]),
                     ("SCRAPRATEVAL", c["scrap_rate"]),
                     ("NGPRICEVAL", c["ng_price"]),
                     ("CCOALFILE", f"scenarios/ccoal_{c['ccoal']}.mod"),
                     ("NGAVAILFILE", f"scenarios/ng_{c['ng_avail']}.mod")):
        s = s.replace(tok, str(val))
    return s


def solve_one(run_id, c):
    mod = os.path.join(TMP, f"run{run_id}.mod")
    with open(mod, "w") as fh:
        fh.write(model_text(c))
    row = {"run_id": run_id, **c}
    t0 = time.time()
    try:
        p = subprocess.run([AMPL, mod], cwd=HERE, capture_output=True,
                           text=True, timeout=300)
        r1 = r2 = None
        for line in p.stdout.splitlines():
            if line.startswith("MCROW,"):
                r1 = line.split(",")[1:]
            elif line.startswith("MCROW2,"):
                r2 = line.split(",")[1:]
        if r1 is None or len(r1) != len(MCROW_FIELDS):
            err = (p.stderr or p.stdout).strip().splitlines()
            row["status"] = "error:" + (err[-1][:80] if err else "no MCROW")
        else:
            row.update(zip(MCROW_FIELDS, r1))
            if r2 and len(r2) == len(MCROW2_FIELDS):
                row.update(zip(MCROW2_FIELDS, r2))
    except subprocess.TimeoutExpired:
        row["status"] = "error:timeout"
    except Exception as e:
        row["status"] = "error:" + str(e).splitlines()[0][:80]
    row["solve_s"] = round(time.time() - t0, 2)
    try:
        os.remove(mod)
    except OSError:
        pass
    return row


def main():
    os.makedirs(TMP, exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        with open(OUT, newline="") as fh:
            done = {int(r["run_id"]) for r in csv.DictReader(fh)
                    if not r.get("status", "").startswith("error")}

    years = [int(CLOUD)] if CLOUD else H2_YEARS
    clouds = {y: [rc for rc in draws_for(y) if rc[0] not in done]
              for y in years}
    for y in years:
        print(f"cloud {y}: {N_PER_CLOUD - len(clouds[y])}/{N_PER_CLOUD} done, "
              f"{len(clouds[y])} to solve", flush=True)

    if ALL or CLOUD:
        todo = [rc for y in years for rc in clouds[y]]
    else:   # staged default: earliest incomplete cloud only
        todo = next((clouds[y] for y in years if clouds[y]), [])
        if todo:
            print(f"STAGED MODE: solving cloud {todo[0][1]['h2_year']} only "
                  f"(rerun the bat for the next cloud)", flush=True)
    if LIMIT:
        todo = todo[:LIMIT]
    if not todo:
        print("Nothing to solve -- all clouds complete.", flush=True)
        return

    new_file = not os.path.exists(OUT)
    n_ok = n_inf = n_err = 0
    t0 = time.time()
    with open(OUT, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futs = {ex.submit(solve_one, i, c): i for i, c in todo}
            for k, fut in enumerate(as_completed(futs), 1):
                row = fut.result()
                st = row.get("status", "")
                n_ok += st == "solved"
                n_inf += st == "infeasible"
                n_err += st.startswith("error")
                w.writerow(row)
                if k % 500 == 0 or k == len(todo):
                    fh.flush()
                    el = time.time() - t0
                    print(f"{k}/{len(todo)}  ok={n_ok} infeas={n_inf} "
                          f"err={n_err}  {el:.0f}s "
                          f"({el/k:.2f}s/run, ETA {el/k*(len(todo)-k)/60:.0f} min)",
                          flush=True)
    print(f"DONE ok={n_ok} infeasible={n_inf} error={n_err} -> {OUT}",
          flush=True)
    sys.exit(1 if (n_err and not n_ok) else 0)


if __name__ == "__main__":
    main()
